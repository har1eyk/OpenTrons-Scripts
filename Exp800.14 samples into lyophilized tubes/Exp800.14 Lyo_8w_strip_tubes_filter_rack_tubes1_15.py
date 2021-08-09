# imports
from opentrons import protocol_api

# metadata
metadata = {
    'protocolName': 'Lyo Samples in 8-well strips from Tubes 1 to 15 plus NTC.',
    'author': 'Harley King <harley.king@luminultra.com>',
    'description': 'Test qPCR Samples Using Lyophilized Samples in 8-well strips from Tubes 1 to 15 plus NTC.',
    'apiLevel': '2.11'
}

##########################

def run(protocol: protocol_api.ProtocolContext):

    # LABWARE
    stds_rack = protocol.load_labware('vwr_24_tuberack_1500ul', '2')
    tiprack300 = protocol.load_labware('opentrons_96_filtertiprack_200ul', '8')
    tiprack20 = protocol.load_labware('opentrons_96_filtertiprack_20ul', '9')
    # tempdeck = protocol.load_module('tempdeck', '4')
    # plate = tempdeck.load_labware('opentrons_96_aluminumblock_generic_pcr_strip_200ul')
    holder_1 = protocol.load_labware('8wstriptubesonfilterracks_96_aluminumblock_250ul', '3')
    holder_2 = protocol.load_labware('8wstriptubesonfilterracks_96_aluminumblock_250ul', '6')
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
    std_5 = stds_rack['A5'] # 900ul water
    std_6 = stds_rack['A6'] # 900ul water 
    std_7 = stds_rack['B1'] # 900ul water
    std_8 = stds_rack['B2'] # 900ul water
    std_9 = stds_rack['B3'] # 900ul water
    std_10 = stds_rack['B4'] # 900ul water
    std_11 = stds_rack['B5'] # 900ul water
    std_12 = stds_rack['B6'] # 900ul water
    std_13 = stds_rack['C1'] # 900ul water
    std_14 = stds_rack['C2'] # 900ul water
    std_15 = stds_rack['C3'] # 900ul water
    water = stds_rack['D6'] # empty, receives sN_mix and WATER as NTC
    
    # user inputs
    # this is 4 reps on each tube e.g. 16*4 = 64 samples
    num_of_sample_reps = 3 # doesn't yet accommodate other ints
    holderList = [holder_1, holder_2]
    tot_sample_vol = 20
    # lists
    all_stds = [std_1, std_2, std_3, std_4, std_5, std_6, std_7, std_8, std_9, std_10, std_11, std_12, std_13, std_14, std_15, water]
    dest_rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'] # easier to add rows for stds rather than repeat
    
    # #### COMMANDS ######    
    # Distribute stds DNA to strip tubes * # reps
    for i, (stdtube, row) in enumerate(zip(all_stds, dest_rows)): #loop through all std tubes
        p300.pick_up_tip()
        p300.move_to(stdtube.bottom(40))
        p300.aspirate(20*num_of_sample_reps*(1+0.1), stdtube)
        protocol.delay(seconds=1) #equilibrate
        p300.touch_tip(v_offset=-12) # two levels to remove residue
        protocol.delay(seconds=1) #equilibrate
        p300.touch_tip(v_offset=-4) # remove residue 
        start = 0
        stop = num_of_sample_reps # max is 6 reps
        if i <= 7: # stds 1..8 go in first column i.e. don't go to next holder
            holder = holderList[0]
        else: # stds 8..15, NTC
            holder = holderList[1]
        for y in range(start, stop):
            source = stdtube
            col = 2*y+1
            dest = row+str(col)
            p300.move_to(holder[dest].bottom(40)) # move above caps
            p300.dispense(tot_sample_vol, holder[dest].bottom(6))
            protocol.delay(seconds=1)
            p300.touch_tip(v_offset=-12) #touch tip x mm below the top of the current location
            p300.move_to(holder[dest].top()) # need this move to recenter tip so it doesn't drag up tubes
            p300.move_to(holder[dest].bottom(40)) # position above caps
        p300.move_to(holder[dest].bottom(40)) # position above caps
        p300.drop_tip()