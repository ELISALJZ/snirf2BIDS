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
from pandas import DataFrame, read_csv

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


class Metadata:
    """ Metadata File Class

    Class object that encapsulates the JSON and TSV Metadata File Class

    """

    def __init__(self):
        default_list = self.default_fields()
        default = {'path2origin': String(None)}
        for name in default_list:
            # assume they are all string now
            default[name] = String(None)

        self._fields = default
        self._source_snirf = None

    def __setattr__(self, name, val):
        if name.startswith('_'):
            super().__setattr__(name, val)

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
            return super().__getattribute__(name)

    def __delattr__(self, name):
        default = self.default_fields()
        if name not in default.keys():
            del self._fields[name]
            _logger.info("field" + name + "was deleted.")
        else:
            raise TypeError("Cannot remove a default field!")

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
        if "sidecar" in self.get_class_name().lower():
            default_list = _getdefault('BIDS_fNIRS_subject_folder.json', "_nirs.json")
        elif isinstance(self, JSON):
            default_list = _getdefault('BIDS_fNIRS_subject_folder.json', "_" + self.get_class_name().lower() + ".json")
        elif isinstance(self, TSV):
            default_list = _getdefault('BIDS_fNIRS_subject_folder.json', "_" + self.get_class_name().lower() + ".tsv")
        return default_list

    def get_class_name(self):
        return self.__class__.__name__


class JSON(Metadata):
    """ JSON Class

    Class object that encapsulates subclasses that create and contain BIDS JSON files

    """

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
        _logger.info(self.get_class_name() + " class is rewritten given json file at " + fpath)

    def save_to_dir(self, info, fpath):
        filename = ""
        for name in info:
            if info[name] is not None:
                filename = filename + name + info[name] + '_'
        filename = filename + self.get_class_name().lower() + '.json'
        filedir = fpath + '/' + filename

        fields = {}
        for name in self._fields.keys():
            fields[name] = self._fields[name].value
        with open(filedir, 'w') as file:
            json.dump(fields, file, indent=4)
        self._fields['path2origin'].value = filedir

        _logger.info(self.get_class_name() + " class is saved as " + filename + "at " + fpath)


class TSV(Metadata):
    """ TSV Class

        Class object that encapsulates subclasses that create and contain BIDS TSV files

    """

    def save_to_tsv(self, fpath):
        fields = list(self._fields)[1:]
        values = list(self._fields.values())[1:]
        values = [values[i].value for i in range(len(values))]
        tsvDict = dict(zip(fields, values))
        tsvDictFiltered = {key: value for key, value in tsvDict.items() if value is not None}
        tsvDF = DataFrame(tsvDictFiltered)
        tsvDF.to_csv(fpath + '/' + self.get_class_name().lower() + '.tsv', sep='\t', index=False)

    def load_from_tsv(self, fpath):
        # pass
        tsvDF = read_csv(fpath, sep='\t')
        for key in tsvDF.to_dict('list').keys():
            if tsvDF.to_dict('list')[key] is not None:
                self._fields[key].value = tsvDF.to_dict('list')[key]


class Coordsystem(JSON):

    logger: logging.Logger = _logger

    def load_from_SNIRF(self, fpath):
        self._source_snirf = Snirf(fpath)
        self._fields['NIRSCoordinateUnits'].value = self._source_snirf.nirs[0].metaDataTags.LengthUnit
        _logger.info("Coordsystem class is rewritten given snirf file at " + fpath)


# class Participant(TSV):
#
#     def load_from_file(self, fpath):
#         pass
#         # fill in the blank"
#
#         _logger.info("Participant class is rewrite given tsv file at " + fpath)
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


class Optodes(TSV):

    # logger: logging.Logger = _logger

    def load_from_SNIRF(self, fpath):
        self._source_snirf = Snirf(fpath)

        self._fields['name'].value = np.append(self._source_snirf.nirs[0].probe.sourceLabels,
                                               self._source_snirf.nirs[0].probe.detectorLabels)
        self._fields['type'].value = np.append(['source'] * len(self._source_snirf.nirs[0].probe.sourceLabels),
                                               ['detector'] * len(self._source_snirf.nirs[0].probe.detectorLabels))
        if self._source_snirf.nirs[0].probe.detectorPos2D is None and \
                self._source_snirf.nirs[0].probe.sourcePos2D is None:
            self._fields['x'].value = np.append(self._source_snirf.nirs[0].probe.sourcePos3D[:, 0],
                                                self._source_snirf.nirs[0].probe.detectorPos3D[:, 0])
            self._fields['y'].value = np.append(self._source_snirf.nirs[0].probe.sourcePos3D[:, 1],
                                                self._source_snirf.nirs[0].probe.detectorPos3D[:, 1])
            self._fields['z'].value = np.append(self._source_snirf.nirs[0].probe.sourcePos3D[:, 2],
                                                self._source_snirf.nirs[0].probe.detectorPos3D[:, 2])
        elif self._source_snirf.nirs[0].probe.detectorPos3D is None and \
                self._source_snirf.nirs[0].probe.sourcePos3D is None:
            self._fields['x'].value = np.append(self._source_snirf.nirs[0].probe.sourcePos2D[:, 0],
                                                self._source_snirf.nirs[0].probe.detectorPos2D[:, 0])
            self._fields['y'].value = np.append(self._source_snirf.nirs[0].probe.sourcePos2D[:, 1],
                                                self._source_snirf.nirs[0].probe.detectorPos2D[:, 1])


class Channels(TSV):

    logger: logging.Logger = _logger

    def load_from_SNIRF(self, fpath):
        self._source_snirf = Snirf(fpath)

        source = self._source_snirf.nirs[0].probe.sourceLabels
        detector = self._source_snirf.nirs[0].probe.detectorLabels
        wavelength = self._source_snirf.nirs[0].probe.wavelengths

        name = []
        label = np.zeros(self._source_snirf.nirs[0].data[0].measurementList.__len__())
        wavelength_nominal = np.zeros(self._source_snirf.nirs[0].data[0].measurementList.__len__())

        for i in range(self._source_snirf.nirs[0].data[0].measurementList.__len__()):
            source_index = self._source_snirf.nirs[0].data[0].measurementList[i].sourceIndex
            detector_index = self._source_snirf.nirs[0].data[0].measurementList[i].detectorIndex
            wavelength_index = self._source_snirf.nirs[0].data[0].measurementList[i].wavelengthIndex

            name.append(source[source_index-1] + '-' + detector[detector_index-1] + '-' +
                        str(wavelength[wavelength_index-1]))
            label[i] = self._source_snirf.nirs[0].data[0].measurementList[i].dataTypeLabel
            wavelength_nominal[i] = wavelength[wavelength_index-1]

        self._fields['name'].value = name
        self._fields['type'].value = label
        self._fields['source'].value = source
        self._fields['detector'].value = detector
        self._fields['wavelength_nominal'].value = wavelength_nominal
        self._fields['sampling_frequency'].value = np.mean(np.diff(np.array(self._source_snirf.nirs[0].data[0].time)))

        _logger.info("Channel class is rewrite given snirf file at " + fpath)


class Events(TSV):

    logger: logging.Logger = _logger

    def load_from_SNIRF(self, fpath):
        snirf = Snirf(fpath)
        self._source_snirf = snirf
        # fill in the blank

        _logger.info("Event class is rewrite gievn snirf file at " + fpath)


class Sidecar(JSON):

    def load_from_SNIRF(self, fpath):
        self._source_snirf = Snirf(fpath)
        self._fields['SamplingFrequency'].value = np.mean(np.diff(np.array(self._source_snirf.nirs[0].data[0].time)))
        self._fields['NIRSChannelCount'].value = self._source_snirf.nirs[0].data[0].measurementList.__len__()

        if self._source_snirf.nirs[0].probe.detectorPos2D is None \
                and self._source_snirf.nirs[0].probe.sourcePos2D is None:
            self._fields['NIRSSourceOptodeCount'].value = self._source_snirf.nirs[0].probe.sourcePos3D.__len__()
            self._fields['NIRSDetectorOptodeCount'].value = self._source_snirf.nirs[0].probe.detectorPos3D.__len__()
        elif self._source_snirf.nirs[0].probe.detectorPos3D is None \
                and self._source_snirf.nirs[0].probe.sourcePos3D is None:
            self._fields['NIRSSourceOptodeCount'].value = self._source_snirf.nirs[0].probe.sourcePos2D.__len__()
            self._fields['NIRSDetectorOptodeCount'].value = self._source_snirf.nirs[0].probe.detectorPos2D.__len__()

        _logger.info("Sidecar class is rewrite given snirf file at " + fpath)


class BIDS(object):

    def __init__(self):
        _logger.info("an BIDS instance was created.")

        self.coordsystem = Coordsystem()
        # self.participant = Participant()
        self.optodes = Optodes()
        # self.channel = Channel()
        # self.events = Events()
        # self.channel = Channel()
        # self.event = Event()
        self.sidecar = Sidecar()

    def validate(self):
        pass


def Convert():
    # fPath = importData()

    # extract BIDS form a SNIRF file
    # oneBIDS = BIDS_from_SNIRF(fPath)

    # build a BIDS dataset from Scratch
    bids = BIDS()
    bids.optodes.load_from_SNIRF('D:\School\SeniorProject\Repos\snirf2BIDS\sub-01_task-tapping_nirs.snirf')
    bids.optodes.save_to_tsv('D:\School\SeniorProject\Repos\snirf2BIDS')
    bids.optodes.load_from_tsv('D:\School\SeniorProject\Repos\snirf2BIDS\optodes.tsv')
    bids.optodes.save_to_tsv('D:\School\SeniorProject\Repos')
    # bids.sidecar.load_from_SNIRF('/Users/andyzjc/Downloads/SeniorProject/SampleData/RobExampleData/sub-01/nirs/sub-01_task-test_nirs.snirf')
    # bids.channel.load_from_SNIRF('/Users/andyzjc/Downloads/SeniorProject/SampleData/RobExampleData/sub-01/nirs/sub-01_task-test_nirs.snirf')
    # bids.channel.load_from_tsv('/Users/andyzjc/Downloads/SeniorProject/SampleData/RobExampleData/sub-01/nirs/sub-01_task-test_channels.tsv')
    # bids.sidecar.load_from_SNIRF('/Users/andyzjc/Downloads/SeniorProject/SampleData/RobExampleData/sub-01/nirs/sub-01_task-test_nirs.snirf')
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
    # bids.coordsystem.save_to_dir(info=subj1, fpath='/Users/andyzjc/Downloads/SeniorProject/snirf2BIDS')
    #
    # bids2 = BIDS()
    # bids2.coordsystem.load_from_json(fpath='/Users/andyzjc/Downloads/SeniorProject/snirf2BIDS/sub-01_coordsystem.json')
    #
    # bids3 = BIDS()
    # bids3.coordsystem.load_from_SNIRF(
    #     fpath='/Users/andyzjc/Downloads/SeniorProject/SampleData/RobExampleData/sub-01/nirs/sub-01_task-test_nirs.snirf')
    return 0


Convert()
