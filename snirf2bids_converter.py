# To convert a given folder containing snirf files to BIDS folder directory with necessary files
import numpy as np
import sys
import os
import shutil
import validator
import Snirf
import json
from colorama import Fore, Style
from tkinter import Tk
from tkinter.filedialog import askdirectory

# Step 2: given a snirf class, extract information to build appropriate file
    # For the whole dataset:
        #  dataset_description.json
        #     participants.tsv
        #     participants.json
        #     README.txt
        #     CHANGES.txt
    # For each sub/ses/snirf:
        # a. form file name sub-label_ses-label_

def buildBidsFile(previousFileDirectory):
    oneSnirf = Snirf.SnirfLoad(previousFileDirectory)


def generateBidsDirectory(folderPath, allSubj, allFile):
    for index, oneSubj in enumerate(allSubj):
        SubjNum = int(''.join(filter(str.isdigit, oneSubj)))
        subjFolder = folderPath + '/' + 'sub-' + str(SubjNum)
        os.mkdir(subjFolder)
        os.mkdir(subjFolder + '/' + 'nirs')
        oneSubjFiles = allFile[index]
        SubjName = 'sub-' + str(SubjNum) + '_'
        for oneFile in oneSubjFiles:
            taskName = 'task-' + '(' + oneFile.replace('.snirf','') + ')' + '_'
            newFileDirectory = subjFolder + '/' + 'nirs' + '/' + SubjName + taskName + 'nirs.snirf'
            previousFileDirectory = folderPath + '/' + oneSubj + '/' + oneFile
            shutil.copy(previousFileDirectory, newFileDirectory)

            # generate nirs.json
            buildBidsFile(previousFileDirectory)


def checkSubjectFolder(oneSubjPath):
    if os.path.isdir(oneSubjPath):
        allFile = os.listdir(oneSubjPath)

        if allFile.__len__() >= 1:
            for oneFile in allFile:
                if '.snirf' in oneFile:
                    Decision = validator.validate(oneSubjPath + '/' + oneFile)
                    Decision = True
                    if not Decision:
                        print(Fore.RED + oneSubjPath + '/' + oneFile + ' is invalid! Conversion Terminated!')
                        sys.exit()
                else:
                    allFile.remove(oneFile)
        else:
            print(Fore.RED + 'Please have at least one SNIRF file in the dataset folder! Conversion Terminated!')
            sys.exit()
    else:
        print(Fore.RED + 'Invalid Subject Directory! Conversion Terminated!')
        sys.exit()

    return allFile

def checkDatasetFolder(folderPath):
    if os.path.isdir(folderPath):
        allSubj = os.listdir(folderPath)

        bad = '.DS_Store'
        if bad in allSubj:
            allSubj.remove(bad)

        if allSubj.__len__() >= 1:
            allFile = []
            for oneSubj in allSubj:
                if "sub" in oneSubj or "Sub" in oneSubj:
                    oneSubjallFile = checkSubjectFolder(folderPath + '/' + oneSubj)
                    allFile.append(oneSubjallFile)
                else:
                    allSubj.remove(oneSubj)
        else:
            print(Fore.RED + 'Please have at least one Subject in the dataset folder! Conversion Terminated!')
            sys.exit()
    else:
        print(Fore.RED + 'Invalid Dataset Directory! Conversion Terminated!')
        sys.exit()

    print(Fore.GREEN + 'All Files are valid within ' + folderPath)
    return allSubj, allFile

def importDatafolder():
    # Import dataset folder
    if sys.argv.__len__() > 1:
        folderPath = sys.argv[1]
    else:
        Tk().withdraw()
        folderPath = askdirectory(title='Please select a Dataset.')
        if not folderPath:
            sys.exit()

    return folderPath

def Convert():
    folderPath = importDatafolder()
    allSubj,allFile = checkDatasetFolder(folderPath)
    generateBidsDirectory(folderPath, allSubj, allFile)

Convert()






