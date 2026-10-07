[app]

title = Zotero Citation Manager
version = 1.0
package.name = zoterocitationmanager
package.domain = org.avinash
source.dir = .
source.include_exts = py
requirements = python3==3.11.9,hostpython3==3.11.9,kivy,requests,charset-normalizer==2.1.1
orientation = portrait
android.accept_sdk_license = True
[buildozer]

[buildozer:android]

android.api = 35
android.minapi = 23
p4a.branch = master
