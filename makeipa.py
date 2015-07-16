################################################################################
# makeipa.py
#
# A python script to create resigned ipa file from given ipa/app/xcarchive file 
#
# Author: Santosh Sharma
# Version: 1.1
# Creation Date: July 15, 2015
# Revision Date: July 16, 2015
#
# New in version 1.1:
# - Support for compressed .app and .xcarchive files
#
################################################################################

import sys
import time
import os
import shutil
import zipfile
import subprocess

#global constanta
_IPHONE_DISTRIBUTION_CERTIFICATE_NAME = "iPhone Distribution: Santosh Sharma (Y88DLQ42G7)"
_EMBEDDED_MOBILEPROFILE_FILE_NAME = "embedded.mobileprovision"
_ENTITLEMENTS_PLIST_FILE_NAME = "entitlements.plist"

#global variables
_workDirectoryName = None

#extract zip file
def extractAll(zipName):
    global _workDirectoryName
    z = zipfile.ZipFile(_workDirectoryName + "/" + zipName, "r")
    z.extractall(_workDirectoryName)
    z.close

#get file extension
def getFileExtension(fileName):
    nameParts = fileName.split(".")
    if len(nameParts) > 1:
        return nameParts[1]
    else:
        return None

#get file name excluding extension
def getFileNameExcludingExtension(fileName):
    nameParts = fileName.split(".")
    if len(nameParts) > 1:
        return nameParts[0]
    else:
        return None

#extract compressed file retaining same name
def extractCompressedFileRetainingName(compressedFileName):
    global _workDirectoryName
    #proceed only if file exists
    if os.path.exists(_workDirectoryName + "/" + compressedFileName):
        #rename the file to add .zip extension
        os.rename(_workDirectoryName + "/" + compressedFileName, _workDirectoryName + "/" + compressedFileName + ".zip")
        print("Renamed " + compressedFileName + " to " + compressedFileName + ".zip in work directory " + _workDirectoryName )
        #extract zip file
        extractAll(compressedFileName + ".zip")
        print("Extracted " + compressedFileName + ".zip in work directory " + _workDirectoryName)
        #delete the zip file
        os.remove(_workDirectoryName + "/" + compressedFileName + ".zip")
        print("Deleted " + _workDirectoryName + "/" + compressedFileName + ".zip")
        #delete resource fork folder if found
        if os.path.exists(_workDirectoryName + "/__MACOSX"):
            shutil.rmtree(_workDirectoryName + "/__MACOSX")
            print("Deleted resource fork files " + _workDirectoryName + "/__MACOSX")
    
#process app file
def processAppFile(appFileName):
    global _workDirectoryName
    print("Processing " + appFileName + "...")
    #if file is compressed then uncompress it
    if os.path.isfile(_workDirectoryName + "/" + appFileName):
        extractCompressedFileRetainingName(appFileName)
    #remove _codeSignature subfolder from app archive
    shutil.rmtree(_workDirectoryName + "/" + appFileName + "/_codeSignature")
    print("Deleted " + _workDirectoryName + "/" + appFileName + "/_codeSignature")
    #replace embedded.mobileprovision file in app
    if os.path.exists(_workDirectoryName + "/" + appFileName + "/" + _EMBEDDED_MOBILEPROFILE_FILE_NAME):
        os.remove(_workDirectoryName + "/" + appFileName + "/" + _EMBEDDED_MOBILEPROFILE_FILE_NAME)
    shutil.copy(_EMBEDDED_MOBILEPROFILE_FILE_NAME, _workDirectoryName + "/" + appFileName + "/embedded.mobileprovision")
    print("Replaced " + _workDirectoryName + "/" + appFileName + "/embedded.mobileprovision")
    #create a folder named Payload and move app into Payload
    shutil.move(_workDirectoryName + "/" + appFileName, _workDirectoryName + "/Payload/" + appFileName)
    print("Moved " + appFileName + " into Payload folder")
    #sign the app
    #os.system("codesign -f -s \"" + _IPHONE_DISTRIBUTION_CERTIFICATE_NAME + "\" " + _workDirectoryName + "/Payload/" + appFileName)
    p = subprocess.Popen(["codesign -f -s \"" + _IPHONE_DISTRIBUTION_CERTIFICATE_NAME + "\" --entitlements " + _ENTITLEMENTS_PLIST_FILE_NAME + " " + _workDirectoryName + "/Payload/" + appFileName], stdout=subprocess.PIPE, shell=True)
    output, err = p.communicate()
    if err:
        print("Error:" + err)
    #check whether _codeSignature subfolder created in app archive
    if os.path.exists(_workDirectoryName + "/Payload/" + appFileName + "/_codeSignature"):
        print("Code sign completed")
        #zip archive the Payload folder as .ipa file
        shutil.move(_workDirectoryName + "/Payload", _workDirectoryName + "/" + getFileNameExcludingExtension(appFileName) + "/Payload")
        shutil.make_archive(_workDirectoryName + "/" + getFileNameExcludingExtension(appFileName), "zip", _workDirectoryName + "/" + getFileNameExcludingExtension(appFileName))
        #rename the zip extension to ipa
        shutil.move(_workDirectoryName + "/" + getFileNameExcludingExtension(appFileName) + ".zip", _workDirectoryName + "/" + getFileNameExcludingExtension(appFileName) + ".ipa")
        print(_workDirectoryName + "/" + getFileNameExcludingExtension(appFileName) + ".ipa is created")
        #delete Payload folder
        shutil.rmtree(_workDirectoryName + "/" + getFileNameExcludingExtension(appFileName))
        print("All temporary files are removed")
    else:
        print("Code sign failed")
        #delete work folder and all temporary files
        shutil.rmtree(_workDirectoryName)
        print("Deleted workfolder " + _workDirectoryName + " and all temporary files")

#process ipa file
def processIpaFile(ipaFileName):
    global _workDirectoryName
    print("Processing " + ipaFileName + "...")
    #extract ipa file
    extractAll(ipaFileName)
    print("Uncompressed " + ipaFileName + " into Payload folder")
    #delete ipa file from work directory
    os.remove(_workDirectoryName + "/" + ipaFileName)
    print("Deleted " + ipaFileName)
    #move app from payload folder into work folder
    for item in os.listdir(_workDirectoryName + "/Payload"):
        if getFileExtension(item) == "app":
            shutil.copytree(_workDirectoryName + "/Payload/" + item, _workDirectoryName + "/" + item)
            print("Copied " + item + " from Payload to " + _workDirectoryName)
    #delete payload folder
    shutil.rmtree(_workDirectoryName + "/Payload")
    print("Deleted " + _workDirectoryName + "/Payload")
    #process app file
    for item in os.listdir(_workDirectoryName):
        if getFileExtension(item) == "app":
            processAppFile(item)
            
 
#process XCArchive file
def processXCArchiveFile(xcarchiveFileName):
    global _workDirectoryName
    print("Processing xcarchive file...")
    #if file is compressed then uncompress it
    if os.path.isfile(_workDirectoryName + "/" + xcarchiveFileName):
        extractCompressedFileRetainingName(xcarchiveFileName)
    #find app file from Products/Applications subdirectory
    appFileName = None
    for item in os.listdir(_workDirectoryName + "/" + xcarchiveFileName + "/Products/Applications"):
        if getFileExtension(item) == "app":
            appFileName = item
            shutil.copytree(_workDirectoryName + "/" + xcarchiveFileName + "/Products/Applications/" + item, _workDirectoryName + "/" + item)
            print("Copied " + appFileName + " to " + _workDirectoryName)
    #delete xcarchive file
    shutil.rmtree(_workDirectoryName + "/" + xcarchiveFileName)
    print("Deleting " + _workDirectoryName + "/" + xcarchiveFileName)
    #process app file
    processAppFile(appFileName)

#create work directory
def createWorkDrirectory():
    #get current date time in yyyymmddHHMMSS format to use as work directory name
    workDirectoryName = time.strftime("%Y%m%d%H%M%S")
    #create work directory
    if not os.path.exists(workDirectoryName):
        os.makedirs(workDirectoryName)
    print("Created work directory named - " + workDirectoryName)
    return workDirectoryName
        
#process the file mentioned in program argument
def processFile(inputFileName):
    global _workDirectoryName
    #create work directory
    _workDirectoryName = createWorkDrirectory()
    #copy input file to work directory
    if os.path.isdir(inputFileName):
        shutil.copytree(inputFileName, _workDirectoryName + "/" + inputFileName)
    else:
        shutil.copy(inputFileName, _workDirectoryName + "/" + inputFileName)
    print("Copied " + inputFileName + " to work directory " + _workDirectoryName)
    fileExtension = getFileExtension(inputFileName)
    if fileExtension == "xcarchive":
        processXCArchiveFile(inputFileName)
    else:
        if fileExtension == "app":
            processAppFile(inputFileName)
        else:
            if fileExtension == "ipa":
                processIpaFile(inputFileName)
                
#validate dependencies
def validateDependencies():
    #chack whether embedded.mobileprovision file exists in current working directory
    if os.path.exists(_EMBEDDED_MOBILEPROFILE_FILE_NAME) == False:
        print(_EMBEDDED_MOBILEPROFILE_FILE_NAME + " file is required in current working directory")
        return False
    #check whether _ENTITLEMENTS_PLIST_FILE_NAME exists
    if os.path.exists(_ENTITLEMENTS_PLIST_FILE_NAME) == False:
        print(_ENTITLEMENTS_PLIST_FILE_NAME + " file is required in current working directory")
        return False
    return True

#main module
def main():
    #display program argumante
    if len(sys.argv) == 2:
        fileName = sys.argv[1]
        if os.path.exists(fileName):
            if validateDependencies():
                processFile(fileName)
        else:
            print(fileName + " not found")
    else:
        print("About makeipa: A command line tool to create ipa file signed with Apple Enterprise Distribution Certificate.")
        print("Usage: python makeipa.py <full path of xcarchive or app or ipa file>")

#program execution starts here
main()
    

    
