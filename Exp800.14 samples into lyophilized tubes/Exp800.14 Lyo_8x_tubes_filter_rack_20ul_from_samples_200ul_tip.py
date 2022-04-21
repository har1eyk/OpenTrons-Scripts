# imports
from opentrons import protocol_api

# metadata
metadata = {
    'protocolName': 'Test qPCR Samples Using Lyophilized Samples in 8-well strips.',
    'author': 'Harley King <harley.king@luminultra.com>',
    'description': 'Add DNA samples to lyophilized 8-well strip tubes. Tubes are held by 200 filter tip racks.',
    'apiLevel': '2.11'
}

# def which_holder (plate, samp, dest):

##########################

def run(protocol: protocol_api.ProtocolContext):

    # LABWARE
    stds_rack = protocol.load_labware('vwr_24_tuberack_1500ul', '1')
    tiprack300 = protocol.load_labware('opentrons_96_filtertiprack_200ul', '8')
    tempdeck = protocol.load_module('tempdeck', '10')
    # plate = tempdeck.load_labware('opentrons_96_aluminumblock_generic_pcr_strip_200ul')
    holder_1 = protocol.load_labware('8wstriptubesonfilterracks_96_aluminumblock_250ul', '3')
    holder_2 = protocol.load_labware('8wstriptubesonfilterracks_96_aluminumblock_250ul', '6')
    # holder_3 = protocol.load_labware('8wstriptubesonfilterracks_96_aluminumblock_250ul', '7')
    # PIPETTES
    p300 = protocol.load_instrument(
        'p300_single_gen2', 'left', tip_racks=[tiprack300]
    )
    # p20 = protocol.load_instrument(
    #     'p20_single_gen2', 'right', tip_racks=[tiprack20]
    # )
    
    # REAGENTS
    #fuge_rack @ position 1
    # samp_1 = fuge_rack['B1'] 
    # samp_2 = fuge_rack['B2']
    # samp_3 = fuge_rack['B3']
    # samp_4 = fuge_rack['B4']
    # samp_5 = fuge_rack['B5']
    # samp_6 = fuge_rack['B6']
    # samp_7 = fuge_rack['C1']

    # sds_rack  @ position 2
    # WATER = stds_rack['D6'] # 1500ul WATER
    SAMP_1mix = stds_rack['A6'] # empty
    SAMP_2mix = stds_rack['B1'] # empty
    SAMP_3mix = stds_rack['B2'] # empty
    SAMP_4mix = stds_rack['B3'] # empty
    SAMP_5mix = stds_rack['B4'] # empty
    SAMP_6mix = stds_rack['B5'] # empty
    SAMP_7mix = stds_rack['B6'] # empty
    SAMP_8mix = stds_rack['D6'] # empty
    # SAMP_2mix = stds_rack['B6'] # empty
    # SAMP_3mix = stds_rack['C1'] # empty
    # SAMP_4mix = stds_rack['C2'] # empty
    # SAMP_5mix = stds_rack['B5'] # empty
    # SAMP_6mix = stds_rack['B6'] # empty
    # SAMP_7mix = stds_rack['C1'] # empty
    # NTC_mix = stds_rack['D6'] # empty, receives sN_mix and WATER as NTC
    
    # user inputs
    # num_of_sample_reps is another way of stating number of strips
    num_of_sample_reps_per_holder = 4 # can't exceed 6
    holderList = [holder_1, holder_2]
    # holderList = [holder_1]
    
    # lists
    # ALL_SAMPs = [samp_1, samp_2, samp_3, samp_4, samp_5, samp_6, samp_7, WATER]
    SAMP_mixes = [SAMP_1mix, SAMP_2mix, SAMP_3mix, SAMP_4mix, SAMP_5mix, SAMP_6mix, SAMP_7mix, SAMP_8mix]
    # SAMP_mixes = [SAMP_1mix, SAMP_2mix, SAMP_3mix, SAMP_4mix, SAMP_5mix, SAMP_6mix, SAMP_7mix, WATER]
    SAMP_wells = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
    
    # #### COMMANDS ######    
    # Add sample DNA, mix, distribute to strip tubes
    for i, mixtube in enumerate(SAMP_mixes):
        for y in range(0, len(holderList)): #usually length 1 or 2
            p300.pick_up_tip()
            p300.move_to(mixtube.bottom(40))
            p300.aspirate(num_of_sample_reps_per_holder*20*1.10, mixtube.bottom(2)) # 6*20*1.08 = 130
            protocol.delay(seconds=1) #equilibrate
            p300.touch_tip(v_offset=-3)
            holderPos = y
            holder = holderList[holderPos]
            for x in range(num_of_sample_reps_per_holder): # samples in holder
                row = SAMP_wells[i]
                dest = row+str(2*x+1) # need +1 offset for col 
                p300.move_to(holder[dest].bottom(40)) #move across holder in +4cm pos
                p300.dispense(20, holder[dest].bottom(6), rate=0.75) # more height so tip doesn't touch pellet
                p300.touch_tip()
                p300.move_to(holder[dest].top()) # centers tip so tip doesn't lift tubes after touch
                p300.move_to(holder[dest].bottom(40)) #move across holder in +4cm pos
            p300.drop_tip()