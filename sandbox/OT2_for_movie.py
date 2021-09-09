# imports
from opentrons import protocol_api

# metadata
metadata = {
    'protocolName': 'OT-2_camera',
    'author': 'Harley King <harley.king@luminultra.com>',
    'description': 'Rapid movement of OT-2 for the camera',
    'apiLevel': '2.11'
}

##########################

def run(protocol: protocol_api.ProtocolContext):

    # LABWARE
    stds_rack = protocol.load_labware('vwr_24_tuberack_1500ul', '2')
    tiprack300 = protocol.load_labware('opentrons_96_filtertiprack_200ul', '8')
    tiprack20 = protocol.load_labware('opentrons_96_filtertiprack_20ul', '9')
    tempdeck = protocol.load_module('tempdeck', '1')
    plate = tempdeck.load_labware('opentrons_96_aluminumblock_generic_pcr_strip_200ul')
    # holder_1 = protocol.load_labware('8wstriptubesonfilterracks_96_aluminumblock_250ul', '3')
    # holder_2 = protocol.load_labware('8wstriptubesonfilterracks_96_aluminumblock_250ul', '6')
    # holder_3 = protocol.load_labware('8wstriptubesonfilterracks_96_aluminumblock_250ul', '7')
    # PIPETTES
    p300 = protocol.load_instrument(
        'p300_single_gen2', 'left', tip_racks=[tiprack300]
    )
    p20 = protocol.load_instrument(
        'p20_single_gen2', 'right', tip_racks=[tiprack20]
    )
    
    # REAGENTS
    std_1 = stds_rack['A1'] # 990ul Water
    std_2 = stds_rack['A2'] # 900ul water
    std_3 = stds_rack['A3'] # 900ul water
    std_4 = stds_rack['A4'] # 900ul water
    
    # # user inputs
    # # this is 4 reps on each tube e.g. 16*4 = 64 samples
    # num_of_sample_reps = 6 # doesn't yet accommodate other ints
    # holderList = [holder_1, holder_2]
    # tot_sample_vol = 20
    # # lists
    # all_stds = [std_1, std_2, std_3, std_4, std_5, std_6, std_7, std_8, std_9, std_10, std_11, std_12, std_13, std_14, std_15, water]
    # dest_rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'] # easier to add rows for stds rather than repeat
    
    # #### COMMANDS ######    
    # Distribute stds DNA to strip tubes * # reps
    p300.transfer(
        20,
        std_1,
        plate.rows_by_name()['A'])