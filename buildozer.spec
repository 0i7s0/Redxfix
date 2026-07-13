[app]
# عنوان التطبيق
title = Redxfix

# اسم حزمة التطبيق (يجب أن يكون فريداً)
package.name = redxfix
package.domain = org.redxfix

# المسار الأساسي للكود
source.dir = .

# الامتدادات المطلوبة
source.include_exts = py,png,jpg,kv,atlas

# نسخة التطبيق
version = 1.0

# ملف الأيقونة
icon.filename = %(source.dir)s/er.png

# المتطلبات (أضف أي مكتبات أخرى تستخدمها في كودك هنا)
requirements = python3,kivy

# الاتجاه (portrait للموبايل، landscape للتابلت)
orientation = portrait

# إعدادات الشاشة
fullscreen = 0

# معمارية الأندرويد
android.archs = arm64-v8a, armeabi-v7a

# السماح بالنسخ الاحتياطي
android.allow_backup = True

[buildozer]
log_level = 2
warn_on_root = 1
