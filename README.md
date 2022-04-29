[![snirf2bids](https://img.shields.io/pypi/v/snirf2bids?color=blue&label=snirf2bids&style=flat-square)](https://pypi.org/project/snirf2bids/0.1.7/)
[![pysnirf2](https://img.shields.io/pypi/v/pysnirf2?color=blue&label=pysnirf2&style=flat-square)](https://pypi.org/project/pysnirf2/)

# Table of Contents
- [Introduction](#snirf2bids)
- [Features](#features)
  - [Create BIDS Compliant Structures](#create-bids-compliant-structures)

- [Code Generation](#code-generation)
- [Maintainers](#maintainers)
- [Contributors](#contributors)

 

# snirf2BIDS
Conveniently generate BIDS structure from `.snirf` files.  
Developed by BU BME Senior Design Group 3 (2022): Christian Arthur, Jeonghoon Choi, Jiazhen Liu, Juncheng Zhang.   
Will be maintained by [Boston University Neurophotonics Center(BUNPC)](https://github.com/BUNPC).  
snirf2BIDS requires Python >3 and h5py >3.6.

# Features

## Create BIDS Compliant Structures
`Export(self, outputFormat: str = 'Folder', fpath: str = None)` creates the BIDS compliant metadata files based on information stored in the `Subject` class object. It has `outputFormat` as Folder or Text.
Folder: Assemble output (metadata file) to a specific file directory specified by the user.
Text: Assmble output (metadata file) as a string in JSON-like format.
```python
        def snirf_to_bids(inputpath: str, outputpath: str, participants: dict = None):
    """Creates a BIDS-compliant folder structure (right now, just the metadata files) from a SNIRF file
        Args:
            inputpath: The file path to the reference SNIRF file
            outputpath: The file path/directory for the created BIDS metadata files
            participants: A dictionary with participant information
                Example =
                    {participant_id: 'sub-01',
                     age: 34,
                     sex: 'M'}
    

    subj = Subject(inputpath)
    subj.export('Folder', outputpath)
 ```

# Code Generation

The fields and descriptions in JSON files are generated based on the latest [Brain Imaging Data Structure v1.7.1-dev](https://bids-specification--802.org.readthedocs.build/en/stable/04-modality-specific-files/11-functional-near-infrared-spectroscopy.html#channels-description-_channelstsv) 
and [SNIRF specification](https://github.com/fNIRS/snirf).

# Maintainers
[@Christian Arthur :melon:](https://github.com/chrsthur)<br>
[@Juncheng Zhang :tangerine:](https://github.com/andyzjc)<br>
[@Jeonghoon Choi :pineapple:](https://github.com/jeonghoonchoi)<br>
[@Jiazhen Liu :grapes:](https://github.com/ELISALJZ)<br>

# Contributors
This project exsists thanks to all people who contribute. <br>
<center class= "half">
<a href="https://github.com/sstucker">
<img src="https://github.com/sstucker.png" width="50" height="50">
</a>

<a href="https://github.com/rob-luke">
<img src="https://github.com/rob-luke.png" width="50" height="50">
</a>

<a href="https://github.com/chrsthur">
<img src="https://github.com/chrsthur.png" width="50" height="50">
</a>

<a href="https://github.com/andyzjc">
<img src="https://github.com/andyzjc.png" width="50" height="50">
</a>

<a href="https://github.com/jeonghoonchoi">
<img src="https://github.com/jeonghoonchoi.png" width="50" height="50">
</a>

<a href="https://github.com/ELISALJZ">
<img src="https://github.com/ELISALJZ.png" width="50" height="50">
</a>
  
<a href="https://github.com/dboas">
<img src="https://github.com/dboas.png" width="50" height="50">
</a>
                                                     </center>
