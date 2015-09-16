# ipaTools

Sometimes we find ourself doing same activity over and over then it makes perfect sense to create programs to automate such activity. This repository contains iOS app development utility programs to automate creation of ipa files.

###makeipa.py

A python script to create resigned ipa file from given ipa/app/xcarchive file. 

#####Prerequisites:
1.	MacBook installed with XCode and iOS SDK
2.	Python 2.7 or later
3.	Apple Distribution Certificate installed on the MacBook (created on developer.apple.com)
4.	iOS App Provisioning Profile (created on developer.apple.com)
5.	entitlements.plist (its template is given bvelow)

#####Template of entitlements.plist File
```
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>application-identifier</key>
	<string>Y88DLQ42G7.com.company.appname</string>
	<key>keychain-access-groups</key>
	<array>
		<string>Y88DLQ42G7.com.company.appname</string>
	</array>
</dict>
</plist>
```
#####Preparation Steps:
1.	Copy makeipa.py and provision profile files in a folder
2.	Open makeipa.py for edit and update following lines:
a.	_IPHONE_DISTRIBUTION_CERTIFICATE_NAME = "iPhone Distribution: Santosh Sharma (Y88DLQ42G7)" for your distribution certificate name.
b.	_EMBEDDED_MOBILEPROFILE_FILE_NAME = "embedded.mobileprovision" for provision profile file name downloaded from developer.apple.com.
3.	Edit entitlements.plist file for app bundle id used in two places.

#####Usage:
```
python makeipa.py <full path of xcarchive or app or ipa file>
```
