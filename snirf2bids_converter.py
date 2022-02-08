# To convert a given folder containing snirf files to BIDS folder directory with necessary files
import numpy as np
import sys
import os
import shutil
import json
from colorama import Fore, Style
from tkinter import Tk
from tkinter.filedialog import askopenfilename
from pysnirf2 import Snirf
import logging

_loggers = {}


def _create_logger(name, log_file, level=logging.INFO):
    if name in _loggers.keys():
        return _loggers[name]
    handler = logging.FileHandler(log_file)
    handler.setFormatter(logging.Formatter('%(asctime)s %(lineno)d %(message)s'))
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    _loggers[name] = logger
    return logger


_logger = _create_logger('fNIRS_BIDS', 'fNIRS_BIDS.log')


def _getdefault(fpath, key):
    file = open(fpath)
    fields = json.load(file)

    return fields[key]


class Field:
    def __init__(self, val):
        self._value = val

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, val):
        self._value = val


class String(Field):

    def __init__(self, val):
        super().__init__(val)
        self._type = str

    @staticmethod
    def validate(val):
        if type(val) is str or val is None:
            return True


class Number(Field):

    def __init__(self, val):
        super().__init__(val)
        self.type = int

    @staticmethod
    def validate(val):
        if type(val) is not str or val is None:
            return True


class Coordsystem(object):

    logger: logging.Logger = _logger

    def __init__(self):
        default_list = _getdefault('BIDS_fNIRS_subject_folder.json', '_coordsystem.json')
        default = {}
        default['path2origin'] = String(None)
        for name in default_list:
            # assume they are all string now
            default[name] = String(None)

        self._fields = default
        _logger.info("Coordsystem class was created.")

    def __setattr__(self, name, val):
        if name.startswith('_'):
            super(Coordsystem, self).__setattr__(name, val)

        elif name in self._fields.keys():
            if self._fields[name].validate(val):
                self._fields[name].value = val
                _logger.info("Field " + name + " had been re-written.")
            else:
                raise ValueError("Incorrect data type")

        elif name not in self._fields.keys():
            if String.validate(val):  # Use our static method to validate a guy of this type before creating it
                self._fields[name] = String(val)
                _logger.info("Customized String Field " + name + " had been created.")
            elif Number.validate(val):
                self._fields[name] = Number(val)
                _logger.info("Customized Number Field " + name + " had been created.")
            else:
                raise ValueError('invalid input')

    def __getattr__(self, name):
        if name in self._fields.keys():
            return self._fields[name].value  # Use the property of the Guy in our managed collection
        else:
            return super(Coordsystem, self).__getattribute__(name)

    def __delattr__(self, name):
        default = _getdefault('BIDS_fNIRS_subject_folder.json', '_coordsystem.json')
        if name not in default.keys():
            del self._fields[name]
            _logger.info("field" + name + "was deleted.")
        else:
            raise TypeError("Cannot remove a default field!")

    def load_from_SNIRF(self, fpath):
        snirf = Snirf(fpath)
        self._Source_snirf = snirf
        self._fields['NIRSCoordinateUnits'].value = snirf.nirs[0].metaDataTags.LengthUnit
        _logger.info("Coordsystem class is rewrite gievn snirf file at " + fpath)

    def load_from_json(self, fpath):
        with open(fpath) as file:
            fields = json.load(file)
        new = {}
        for name in fields:
            # assume they are all string now
            if String.validate(fields[name]):
                new[name] = String(fields[name])
            elif Number.validate(fields[name]):
                new[name] = Number(fields[name])
            else:
                raise TypeError("Incorrect Datatype")

        self._fields = new
        _logger.info("Coordsystem class is rewrite gievn json file at " + fpath)

    def save_to_dir(self, info, fpath):
        filename = ""
        for name in info:
            if info[name] is not None:
                filename = filename + name + info[name] + '_'
        filename = filename + 'coordsystem.json'
        filedir = fpath + '/' + filename

        fields = {}
        for name in self._fields.keys():
            fields[name] = self._fields[name].value
        with open(filedir, 'w') as file:
            json.dump(fields, file, indent=4)
        self._fields['path2origin'].value = filedir

        _logger.info("Coordsystem class is saved as " + filename + "at " + fpath)

    def change_type(self, name):
        if self._fields[name]._type is str:
            self._fields[name] = Number(None)
            _logger.info("Field " + name + "had been re-written to number field due to type change.")

        elif self._fields[name]._type is int:
            self._fields[name] = String(None)
            _logger.info("Field " + name + "had been re-written to string field due to type change.")

        else:
            raise TypeError("Invalid field!")

    def default_fields(self):
        return _getdefault('BIDS_fNIRS_subject_folder.json', '_coordsystem.json')


# class Participant(object):
#
#     logger: logging.Logger = _logger
#
#     def __init__(self):
#         pass
#         # fill in the blank
#         #_logger.info("Participant class was created.")
#
#     def __setattr__(self, name, val):
#         if name.startswith('_'):
#             super(Participant, self).__setattr__(name, val)
#
#         elif name in self._fields.keys():
#             if self._fields[name].validate(val):
#                 self._fields[name].value = val
#                 _logger.info("Field " + name + " had been re-written.")
#             else:
#                 raise ValueError("Incorrect data type")
#
#         elif name not in self._fields.keys():
#             if String.validate(val):  # Use our static method to validate a guy of this type before creating it
#                 self._fields[name] = String(val)
#                 _logger.info("Customized String Field " + name + " had been created.")
#             elif Number.validate(val):
#                 self._fields[name] = Number(val)
#                 _logger.info("Customized Number Field " + name + " had been created.")
#             else:
#                 raise ValueError('invalid input')
#
#     def __getattr__(self, name):
#         if name in self._fields.keys():
#             return self._fields[name].value  # Use the property of the Guy in our managed collection
#         else:
#             return super(Participant, self).__getattribute__(name)  # Fall back to the original __setattr__ behavior
#
#     def __delattr__(self, name):
#         default = _getdefault('BIDS_fNIRS_subject_folder.json', 'participants.tsv')
#         if name not in default.keys():
#             del self._fields[name]
#             _logger.info("field" + name + "was deleted.")
#         else:
#             raise TypeError("Cannot remove a default field!")
#
#     def load_from_file(self, fpath):
#         pass
#         # fill in the blank"
#
#         _logger.info("Participant class is rewrite gievn tsv file at " + fpath)
#
#     def save_to_json(self, info, fpath):
#         pass
#         # fill in the blank
#
#         #_logger.info("Participant class is saved as " + filename + "at " + fpath)
#
#     def save_to_TSV(self, info, fpath):
#         pass
#         # fill in the blank
#
#         # _logger.info("Participant class is saved as " + filename + "at " + fpath)
#
#     def change_type(self, name):
#         if self._fields[name]._type is str:
#             self._fields[name] = Number(None)
#             _logger.info("Field " + name + "had been re-written to number field due to type change.")
#
#         elif self._fields[name]._type is int:
#             self._fields[name] = String(None)
#             _logger.info("Field " + name + "had been re-written to string field due to type change.")
#
#         else:
#             raise TypeError("Invalid field!")
#
#     def default_fields(self):
#         pass
#         # fill in the blank
#
#         # return _getdefault('BIDS_fNIRS_subject_folder.json', 'participants.tsv')


class Optode(object):

    logger: logging.Logger = _logger

    def __init__(self):
        default_list = _getdefault('BIDS_fNIRS_subject_folder.json', '_optodes.tsv')
        default = {}
        default['path2origin'] = String(None)
        for name in default_list:
            # assume they are all string now
            default[name] = String(None)

        self._fields = default
        _logger.info("Coordsystem class was created.")

    def __setattr__(self, name, val):
        if name.startswith('_'):
            super(Optode, self).__setattr__(name, val)

        elif name in self._fields.keys():
            if self._fields[name].validate(val):
                self._fields[name].value = val
                _logger.info("Field " + name + " had been re-written.")
            else:
                raise ValueError("Incorrect data type")

        elif name not in self._fields.keys():
            if String.validate(val):  # Use our static method to validate a guy of this type before creating it
                self._fields[name] = String(val)
                _logger.info("Customized String Field " + name + " had been created.")
            elif Number.validate(val):
                self._fields[name] = Number(val)
                _logger.info("Customized Number Field " + name + " had been created.")
            else:
                raise ValueError('invalid input')

    def __getattr__(self, name):
        if name in self._fields.keys():
            return self._fields[name].value  # Use the property of the Guy in our managed collection
        else:
            return super(Optode, self).__getattribute__(name)  # Fall back to the original __setattr__ behavior

    def __delattr__(self, name):
        default = _getdefault('BIDS_fNIRS_subject_folder.json', '_optodes.tsv')
        if name not in default.keys():
            del self._fields[name]
            _logger.info("field" + name + "was deleted.")
        else:
            raise TypeError("Cannot remove a default field!")

    def load_from_SNIRF(self, fpath):
        snirf = Snirf(fpath)
        self._Source_snirf = snirf
        # fill in the blank

        #_logger.info("Optode class is rewrite gievn snirf file at " + fpath)

    def load_from_tsv(self, fpath):
        pass
        # fill in the blank"

        # _logger.info("Optode class is rewrite given tsv file at " + fpath)

    def save_to_tsv(self, info, fpath):
        pass
        # fill in the blank

        # _logger.info("Optode class is saved as " + filename + "at " + fpath)

    def change_type(self, name):
        if self._fields[name]._type is str:
            self._fields[name] = Number(None)
            _logger.info("Field " + name + "had been re-written to number field due to type change.")

        elif self._fields[name]._type is int:
            self._fields[name] = String(None)
            _logger.info("Field " + name + "had been re-written to string field due to type change.")

        else:
            raise TypeError("Invalid field!")

    def default_fields(self):
        pass
        # fill in the blank

        # return _getdefault('BIDS_fNIRS_subject_folder.json', '_optodes.tsv)


class Channel(object):

    logger: logging.Logger = _logger

    def __init__(self):
        default_list = _getdefault('BIDS_fNIRS_subject_folder.json', '_channels.tsv')
        default = {}
        default['path2origin'] = String(None)
        for name in default_list:
            # assume they are all string now
            default[name] = String(None)

        self._fields = default
        _logger.info("Channel class was created.")

    def __setattr__(self, name, val):
        if name.startswith('_'):
            super(Channel, self).__setattr__(name, val)

        elif name in self._fields.keys():
            if self._fields[name].validate(val):
                self._fields[name].value = val
                _logger.info("Field " + name + " had been re-written.")
            else:
                raise ValueError("Incorrect data type")

        elif name not in self._fields.keys():
            if String.validate(val):  # Use our static method to validate a guy of this type before creating it
                self._fields[name] = String(val)
                _logger.info("Customized String Field " + name + " had been created.")
            elif Number.validate(val):
                self._fields[name] = Number(val)
                _logger.info("Customized Number Field " + name + " had been created.")
            else:
                raise ValueError('invalid input')

    def __getattr__(self, name):
        if name in self._fields.keys():
            return self._fields[name].value  # Use the property of the Guy in our managed collection
        else:
            return super(Channel, self).__getattribute__(name)  # Fall back to the original __setattr__ behavior

    def __delattr__(self, name):
        default = _getdefault('BIDS_fNIRS_subject_folder.json', '_channels.tsv')
        if name not in default.keys():
            del self._fields[name]
            _logger.info("field" + name + "was deleted.")
        else:
            raise TypeError("Cannot remove a default field!")

    def load_from_SNIRF(self, fpath):
        snirf = Snirf(fpath)
        self._Source_snirf = snirf

        source = snirf.nirs[0].probe.sourceLabels
        detector = snirf.nirs[0].probe.detectorLabels
        wavelength = snirf.nirs[0].probe.wavelengths

        name = []
        label = np.zeros(snirf.nirs[0].data[0].measurementList.__len__())
        wavelength_nominal = np.zeros(snirf.nirs[0].data[0].measurementList.__len__())

        for i in range(snirf.nirs[0].data[0].measurementList.__len__()):
            source_index = snirf.nirs[0].data[0].measurementList[i].sourceIndex
            detector_index = snirf.nirs[0].data[0].measurementList[i].detectorIndex
            wavelength_index = snirf.nirs[0].data[0].measurementList[i].wavelengthIndex

            name.append(source[source_index-1] + '-' + detector[detector_index-1] + '-' + str(wavelength[wavelength_index-1]))
            label[i] = snirf.nirs[0].data[0].measurementList[i].dataTypeLabel
            wavelength_nominal[i] = wavelength[wavelength_index-1]

        self._fields['name'].value = name
        self._fields['type'].value = label
        self._fields['source'].value = source
        self._fields['detector'].value = detector
        self._fields['wavelength_nominal'].value = wavelength_nominal
        self._fields['sampling_frequency'].value = np.mean(np.diff(np.array(snirf.nirs[0].data[0].time)))

        _logger.info("Channel class is rewrite gievn snirf file at " + fpath)

    def load_from_tsv(self, fpath):
        pass

        # _logger.info("Channel class is rewrite given tsv file at " + fpath)

    def save_to_tsv(self, info, fpath):
        pass
        # fill in the blank

        # _logger.info("Optode class is saved as " + filename + "at " + fpath)

    def change_type(self, name):
        if self._fields[name]._type is str:
            self._fields[name] = Number(None)
            _logger.info("Field " + name + "had been re-written to number field due to type change.")

        elif self._fields[name]._type is int:
            self._fields[name] = String(None)
            _logger.info("Field " + name + "had been re-written to string field due to type change.")

        else:
            raise TypeError("Invalid field!")

    def default_fields(self):
        return _getdefault('BIDS_fNIRS_subject_folder.json', '_channels.tsv').keys()


class Event(object):

    logger: logging.Logger = _logger

    def __init__(self):
        default_list = _getdefault('BIDS_fNIRS_subject_folder.json', '_events.json')
        default = {}
        default['path2origin'] = String(None)
        for name in default_list:
            # assume they are all string now
            default[name] = String(None)

        self._fields = default
        _logger.info("Event class was created.")

    def __setattr__(self, name, val):
        if name.startswith('_'):
            super(Event, self).__setattr__(name, val)

        elif name in self._fields.keys():
            if self._fields[name].validate(val):
                self._fields[name].value = val
                _logger.info("Field " + name + " had been re-written.")
            else:
                raise ValueError("Incorrect data type")

        elif name not in self._fields.keys():
            if String.validate(val):  # Use our static method to validate a guy of this type before creating it
                self._fields[name] = String(val)
                _logger.info("Customized String Field " + name + " had been created.")
            elif Number.validate(val):
                self._fields[name] = Number(val)
                _logger.info("Customized Number Field " + name + " had been created.")
            else:
                raise ValueError('invalid input')

    def __getattr__(self, name):
        if name in self._fields.keys():
            return self._fields[name].value  # Use the property of the Guy in our managed collection
        else:
            return super(Event, self).__getattribute__(name)  # Fall back to the original __setattr__ behavior

    def __delattr__(self, name):
        default = _getdefault('BIDS_fNIRS_subject_folder.json', '_events.json')
        if name not in default.keys():
            del self._fields[name]
            _logger.info("field" + name + "was deleted.")
        else:
            raise TypeError("Cannot remove a default field!")

    def load_from_SNIRF(self, fpath):
        snirf = Snirf(fpath)
        self._Source_snirf = snirf
        # fill in the blank

        _logger.info("Event class is rewrite gievn snirf file at " + fpath)

    def load_from_json(self, fpath):
        with open(fpath) as file:
            fields = json.load(file)
        new = {}
        for name in fields:
            # assume they are all string now
            if String.validate(fields[name]):
                new[name] = String(fields[name])
            elif Number.validate(fields[name]):
                new[name] = Number(fields[name])
            else:
                raise TypeError("Incorrect Datatype")

        self._fields = new
        _logger.info("Event class is rewrite given json file at " + fpath)

    def save_to_dir(self, info, fpath):
        filename = ""
        for name in info:
            if info[name] is not None:
                filename = filename + name + info[name] + '_'
        filename = filename + 'event.json'
        filedir = fpath + '/' + filename

        fields = {}
        for name in self._fields.keys():
            fields[name] = self._fields[name].value
        with open(filedir, 'w') as file:
            json.dump(fields, file, indent=4)
        self._fields['path2origin'].value = filedir

        _logger.info("Event class is saved as " + filename + "at " + fpath)

    def change_type(self, name):
        if self._fields[name]._type is str:
            self._fields[name] = Number(None)
            _logger.info("Field " + name + "had been re-written to number field due to type change.")

        elif self._fields[name]._type is int:
            self._fields[name] = String(None)
            _logger.info("Field " + name + "had been re-written to string field due to type change.")

        else:
            raise TypeError("Invalid field!")

    def default_fields(self):
        return _getdefault('BIDS_fNIRS_subject_folder.json', '_events.json')


class Sidecar(object):

    logger: logging.Logger = _logger

    def __init__(self):
        default_list = _getdefault('BIDS_fNIRS_subject_folder.json', '_nirs.json')
        default = {}
        default['path2origin'] = String(None)
        for name in default_list:
            # assume they are all string now
            default[name] = String(None)

        self._fields = default
        _logger.info("Sidecar class was created.")

    def __setattr__(self, name, val):
        if name.startswith('_'):
            super(Sidecar, self).__setattr__(name, val)

        elif name in self._fields.keys():
            if self._fields[name].validate(val):
                self._fields[name].value = val
                _logger.info("Field " + name + " had been re-written.")
            else:
                raise ValueError("Incorrect data type")

        elif name not in self._fields.keys():
            if String.validate(val):  # Use our static method to validate a guy of this type before creating it
                self._fields[name] = String(val)
                _logger.info("Customized String Field " + name + " had been created.")
            elif Number.validate(val):
                self._fields[name] = Number(val)
                _logger.info("Customized Number Field " + name + " had been created.")
            else:
                raise ValueError('invalid input')

    def __getattr__(self, name):
        if name in self._fields.keys():
            return self._fields[name].value
        else:
            return super(Sidecar, self).__getattribute__(name)

    def __delattr__(self, name):
        default = _getdefault('BIDS_fNIRS_subject_folder.json', '_nirs.json')
        if name not in default.keys():
            del self._fields[name]
            _logger.info("field" + name + "was deleted.")
        else:
            raise TypeError("Cannot remove a default field!")

    def load_from_SNIRF(self, fpath):
        snirf = Snirf(fpath)
        self._Source_snirf = snirf
        self._fields['SamplingFrequency'].value = np.mean(np.diff(np.array(snirf.nirs[0].data[0].time)))
        self._fields['NIRSChannelCount'].value = snirf.nirs[0].data[0].measurementList.__len__()

        if snirf.nirs[0].probe.detectorPos2D is None and snirf.nirs[0].probe.sourcePos2D is None:
            self._fields['NIRSSourceOptodeCount'].value = snirf.nirs[0].probe.sourcePos3D.__len__()
            self._fields['NIRSDetectorOptodeCount'].value = snirf.nirs[0].probe.detectorPos3D.__len__()
        elif snirf.nirs[0].probe.detectorPos3D is None and snirf.nirs[0].probe.sourcePos3D is None:
            self._fields['NIRSSourceOptodeCount'].value = snirf.nirs[0].probe.sourcePos2D.__len__()
            self._fields['NIRSDetectorOptodeCount'].value = snirf.nirs[0].probe.detectorPos2D.__len__()

        _logger.info("Sidecar class is rewrite gievn snirf file at " + fpath)

    def load_from_json(self, fpath):
        with open(fpath) as file:
            fields = json.load(file)
        new = {}
        for name in fields:
            # assume they are all string now
            if String.validate(fields[name]):
                new[name] = String(fields[name])
            elif Number.validate(fields[name]):
                new[name] = Number(fields[name])
            else:
                raise TypeError("Incorrect Datatype")

        self._fields = new
        _logger.info("Sidecar class is rewrite given json file at " + fpath)

    def save_to_dir(self, info, fpath):
        filename = ""
        for name in info:
            if info[name] is not None:
                filename = filename + name + info[name] + '_'
        filename = filename + 'nirs.json'
        filedir = fpath + '/' + filename

        fields = {}
        for name in self._fields.keys():
            fields[name] = self._fields[name].value
        with open(filedir, 'w') as file:
            json.dump(fields, file, indent=4)
        self._fields['path2origin'].value = filedir

        _logger.info("Sidecar class is saved as " + filename + "at " + fpath)

    def change_type(self, name):
        if self._fields[name]._type is str:
            self._fields[name] = Number(None)
            _logger.info("Field " + name + "had been re-written to number field due to type change.")

        elif self._fields[name]._type is int:
            self._fields[name] = String(None)
            _logger.info("Field " + name + "had been re-written to string field due to type change.")

        else:
            raise TypeError("Invalid field!")

    def default_fields(self):
        return _getdefault('BIDS_fNIRS_subject_folder.json', '_nirs.json').keys()


class BIDS(object):

    logger: logging.Logger = _logger

    def __init__(self):
        _logger.info("an BIDS instance was created.")

        self.coordsystem = Coordsystem()
        # self.participant = Participant()
        # self.optode = Optode()
        self.channel = Channel()
        # self.event = Event()
        self.sidecar = Sidecar()

    def validate(self):
        pass




# def importData():
#     # Import dataset folder
#     if sys.argv.__len__() > 1:
#         folderPath = sys.argv[1]
#     else:
#         Tk().withdraw()
#         fPath = askopenfilename(title='Please select a Dataset.')
#
#     return fPath


def Convert():
    # fPath = importData()

    # extract BIDS form a SNIRF file
    # oneBIDS = BIDS_from_SNIRF(fPath)

    # build a BIDS dataset from Scratch
    bids = BIDS()
    # bids.channel.load_from_SNIRF('/Users/andyzjc/Downloads/SeniorProject/SampleData/RobExampleData/sub-01/nirs/sub-01_task-test_nirs.snirf')
    # bids.channel.load_from_tsv('/Users/andyzjc/Downloads/SeniorProject/SampleData/RobExampleData/sub-01/nirs/sub-01_task-test_channels.tsv')
    bids.sidecar.load_from_SNIRF('/Users/andyzjc/Downloads/SeniorProject/SampleData/RobExampleData/sub-01/nirs/sub-01_task-test_nirs.snirf')
    #bids.coordsystem.change_type('RequirementLevel')

    # print(bids.coordsystem.RequirementLevel)
    # bids.coordsystem.test = 'test'
    #
    # bids.coordsystem.default_fields()
    #
    subj1 = {
        'sub-': '01',
        'ses-': None,
        'task-': None,
        'run-': None,
    }
    #
    bids.coordsystem.save_to_dir(info=subj1, fpath='/Users/andyzjc/Downloads/SeniorProject/snirf2BIDS')
    #
    # bids2 = BIDS()
    # bids2.coordsystem.load_from_json(fpath='/Users/andyzjc/Downloads/SeniorProject/snirf2BIDS/sub-01_coordsystem.json')
    #
    # bids3 = BIDS()
    # bids3.coordsystem.load_from_SNIRF(
    #     fpath='/Users/andyzjc/Downloads/SeniorProject/SampleData/RobExampleData/sub-01/nirs/sub-01_task-test_nirs.snirf')
    return 0


Convert()
