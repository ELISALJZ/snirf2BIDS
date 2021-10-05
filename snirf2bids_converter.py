# To convert a given folder containing snirf files to BIDS folder directory with necessary files
import numpy as np
import mne
import mne_nirs
import os
import argparse
from mne_bids import BIDSPath, write_raw_bids, stats
from mne_nirs.io.snirf import write_raw_snirf
from mne.utils import logger
from glob import glob
import os.path as op
import subprocess
from pathlib import Path
from datetime import datetime
import json
import hashlib
from checksumdir import dirhash
from pprint import pprint
import validator
import Snirf
import h5py as h5py
import numpy as np
import re
from colorama import Fore, Style
import sys
from tkinter import Tk
from tkinter.filedialog import askdirectory

# Step 1: import a snirf dataset
    # a. check for at least 1 subject and number in current/... or current folder
    # b. check for at least 1 snirf file for session name
    # c. load the snirf file into a snirf class
    # d. validate the snirf file so that there is only one nirs
    # e. if valid, create folder directory based

# Step 2: given a snirf class, extract information to build appropriate file
    # For the whole dataset:
        #  dataset_description.json
        #     participants.tsv
        #     participants.json
        #     README.txt
        #     CHANGES.txt
    # For each sub/ses/snirf:
        # a. form file name sub-label_ses-label_

def generateBidsDirectory(folderPath, allSubj):
    datasetDirectory = folderPath
    for oneSubj in allSubj:
        allFile = os.listdir(datasetDirectory + '/' + oneSubj)
        for oneFile in allFile:
            print('test')
    return

def checkSubjectFolder(oneSubjPath):
    if os.path.isdir(oneSubjPath):
        allFile = os.listdir(oneSubjPath)

        if allFile.__len__() >= 1:
            for oneFile in allFile:
                if '.snirf' in oneFile:
                    Decision = validator.validate(oneSubjPath + '/' + oneFile)
                    Decision = True
                    if not Decision:
                        print(Fore.RED + oneSubjPath + '/' + oneFile + ' is invalid!')
                        sys.exit()
                else:
                    allFile.remove(oneFile)
        else:
            print(Fore.RED + 'Please have at least one SNIRF file in the dataset folder!')
            sys.exit()
    else:
        print(Fore.RED + 'Invalid Subject Directory!')
        sys.exit()

    return allFile

def checkDatasetFolder(folderPath):
    if os.path.isdir(folderPath):
        allSubj = os.listdir(folderPath)

        bad = '.DS_Store'
        if bad in allSubj:
            allSubj.remove(bad)

        if allSubj.__len__() >= 1:
            AllFile = []
            for index, oneSubj in enumerate(allSubj):
                if "sub" in oneSubj or "Sub" in oneSubj:
                    oneSubjallFile = checkSubjectFolder(folderPath + '/' + oneSubj)
                    AllFile[index].append(oneSubjallFile)
                else:
                    allSubj.remove(oneSubj)
        else:
            print(Fore.RED + 'Please have at least one Subject in the dataset folder!')
            sys.exit()
    else:
        print(Fore.RED + 'Invalid Dataset Directory!')
        sys.exit()

    print(Fore.GREEN + 'All Files are valid within ' + folderPath)
    return allSubj

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
    allSubj = checkDatasetFolder(folderPath)
    generateBidsDirectory(folderPath, allSubj)

Convert()






