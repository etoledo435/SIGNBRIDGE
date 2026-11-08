[app]
title = SignBridge Studio
package.name = signbridge
package.domain = org.cyber.signbridge
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0.0
requirements = python3,kivy,opencv-python,mediapipe,numpy,plyer
orientation = portrait
fullscreen = 0
android.permissions = CAMERA, INTERNET
android.api = 33
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a

[buildozer]
log_level = 2
warn_on_root = 1
