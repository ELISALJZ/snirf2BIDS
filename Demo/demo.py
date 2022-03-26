# A demo to use the fnirs-bids converter
import snirf2bids

def convert():
    """ To demonstrate 2 methods of using the fnirs-bids converter

    """

    #####################
    # Variable initialization

    # a snirf file (input) path
    snirf_file_path = '/Users/andyzjc/Downloads/SeniorProject/snirf2BIDS/Demo/sub-02_task-test_nirs.snirf'

    # a bids (output) destination directory
    bids_path = '/Users/andyzjc/Downloads/SeniorProject/snirf2BIDS/Demo'

    # a dictionary that holds the participant (subject) information
    subj1 = {"participant_id": 'sub-01',
             "age": 34,
             "sex": 'M'}

    subj2 = {"participant_id": 'sub-01',
             "age": 21,
             "sex": 'F'}

    ##################### 


    # straight forward way to convert this snirf file to bids structure given the participant file information
    snirf2bids.snirf_to_bids(snirf=snirf_file_path,
                             output=bids_path,
                             participants=subj1)



    return 0



convert()