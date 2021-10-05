import h5py as h5py
import numpy as np
from colorama import Fore
import os

class AuxClass:
    pass

class ProbeClass:
    pass

class StimClass:
    pass

class MeasurementListClass:
    pass

class DataClass:
    pass

    def addGroup(self, groupName):
        if "measurementList" in groupName:
            setattr(self, groupName, MeasurementListClass())
        else:
            print(Fore.RED + 'Please Add a Valid measurementListClass!')
            return

class MetaDataTagsClass:
    pass

class NirsClass:
    pass

    def addGroup(self, groupName):
        if "aux" in groupName:
            setattr(self, groupName, AuxClass())
        elif "probe" in groupName:
            setattr(self, groupName, ProbeClass())
        elif "stim" in groupName:
            setattr(self, groupName, StimClass())
        elif "data" in groupName:
            setattr(self, groupName, DataClass())
        elif "metaDataTags" in groupName:
            setattr(self, groupName, MetaDataTagsClass())
        else:
            print(Fore.RED + 'Please Add a Valid Group!')
            return

class SnirfClass:
    pass

    def addGroup(self, groupName):
        if 'nirs' in groupName:
            setattr(self, groupName, NirsClass())
        else:
            print(Fore.RED + 'Please Add a /Nirs Class!')
            return

def printClass(oneClass):
    if hasattr(oneClass, '__dict__') or hasattr(oneClass, '__slots__'):
        for attribute in oneClass.__dict__.keys():
            if attribute[:2] != '__' and 'addGroup' not in attribute and 'Class' not in attribute:
                value = getattr(oneClass, attribute)
                if not callable(value):
                    print('\t' + attribute, '=', value)
                    if not isinstance(value, str):
                        if value.ndim > 1:
                            print('\t\t' + 'The shape is: ' + str(value.shape))
                else:
                    print(attribute + ':')
                    printClass(value)
    else:
        print(Fore.RED + 'Please Input An Valid Class!')
        return

# def printDataset(oneDataset):
#     if not isinstance(oneDataset, type) and type(oneDataset) == np.ndarray or str or int:
#         print(oneDataset)
#         if not isinstance(oneDataset, str):
#             if oneDataset.ndim > 1:
#                 print('\t\t' + 'The shape is: ' + str(oneDataset.shape))
#     else:
#         return

def SnirfLoad(filePath):

    def getData(gID):
        # check actual data type and dimension, and print accordingly
        if h5py.check_string_dtype(gID.dtype):  # string
            if gID.len() == 1:
                data = gID[0].decode('ascii')
            else:
                data = []
                for y in gID:
                    data.append(y.decode('ascii'))
                data = np.array(data)
        else:
            data = gID[()]
        return data

    def buildDataset(oneClass, oneGroup):
        if isinstance(oneGroup, h5py.Group):
            for xx in oneGroup.keys():
                oneDataset = oneGroup[xx]
                if isinstance(oneDataset, h5py.Dataset):
                    data = getData(oneDataset)
                    setattr(oneClass, xx, data)
                else:
                    if 'measurementList' in xx:
                        setattr(oneClass, xx, MeasurementListClass())
                        newClass = getattr(oneClass, xx)
                        buildDataset(newClass, oneDataset)
                    else:
                        return
        return oneClass

    if ".snirf" in filePath:
        fileID = h5py.File(filePath, 'r')
    else:
        print(Fore.RED + "Please Input a Valid File (SNIRF)!")
        return

    # generate a SNIRF class
    oneSnirf = SnirfClass()
    for ii in fileID.keys():
        oneName = fileID[ii]
        if isinstance(oneName, h5py.Group):
            oneSnirf.addGroup(ii)
            oneNirs = getattr(oneSnirf, ii)
            for jj in oneName.keys():  # /nirs
                oneNirs.addGroup(jj)
                buildDataset(getattr(oneNirs, jj), oneName[jj])
        else:
            if h5py.check_string_dtype(oneName.dtype):
                setattr(oneSnirf, ii, oneName[0].decode('ascii'))
    return oneSnirf

def SnirfSave(snirfObject, pathName):

    def writeDataset(grp,groupObj,field):
        if isinstance(getattr(groupObj, field), str):
            grp.create_dataset(field, data=[eval('groupObj.' + field + ".encode('UTF-8')")])
        elif isinstance(getattr(groupObj, field), np.ndarray):
            if isinstance(getattr(groupObj, field)[0], str):
                grpField = getattr(groupObj, field)
                strArray = [grpField[i].encode('UTF-8') for i in range(grpField.size)]
                grp.create_dataset(field, data=strArray)
            else:
                grp.create_dataset(field, data=getattr(groupObj, field))
        else:
            grp.create_dataset(field, data=getattr(groupObj, field))
        return grp

    def writeGroup(f, groupObj, attribute):
        grp = f.create_group(attribute)

        for field in groupObj.__dict__.keys():
            if field[:2] != '__' and 'addGroup' not in field and 'Print' not in field:
                oneClass = getattr(groupObj, field)
                if hasattr(oneClass, '__dict__') or hasattr(oneClass, '__slots__'):
                    writeGroup(grp, getattr(groupObj, field), field)
                else:
                    grp = writeDataset(grp, groupObj, field)
        return f

    if hasattr(snirfObject, '__dict__') or hasattr(snirfObject, '__slots__'):
        if type(snirfObject).__name__ != 'SnirfClass':
            print(Fore.RED + 'Please input a Valid SNIRF Class Object!')
            return
        if os.path.isfile(pathName):
            print(Fore.RED + 'File already Exist! Please input Another Filename!')
            return
        if ".snirf" not in pathName:
            print(Fore.RED + 'Please input a Valid file extension (SNIRF)!')
            return
    else:
        print(Fore.RED + 'Please input a Valid Class Object!')
        return

    with h5py.File(pathName, 'w') as f:
        for attribute in snirfObject.__dict__.keys():
            if attribute[:2] != '__' and 'addGroup' not in attribute and 'Print' not in attribute:
                oneClass = getattr(snirfObject, attribute)
                if hasattr(oneClass, '__dict__') or hasattr(oneClass, '__slots__'):
                    f = writeGroup(f, getattr(snirfObject, attribute), attribute)
                else:
                    f = writeDataset(f, snirfObject, attribute)

# def main():
#     filePath = '/Users/andyzjc/Downloads/SeniorProject/SampleData/Homer3Example/homerexample_modified.snirf'
#     test = SnirfLoad((filePath))
#     printClass(test.nirs.data1.measurementList1)
#     test.addGroup('')
#     SnirfSave(test, '/Users/andyzjc/Downloads/test6.snirf')
#     return test
#
# test = main()
