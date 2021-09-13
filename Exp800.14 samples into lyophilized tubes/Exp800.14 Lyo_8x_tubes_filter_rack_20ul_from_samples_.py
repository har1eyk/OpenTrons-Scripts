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
    fuge_rack = protocol.load_labware('vwr_24_tuberack_1500ul', '1')
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
    #fuge_rack @ position 1
    # samp_1 = fuge_rack['B1'] 
    # samp_2 = fuge_rack['B2']
    # samp_3 = fuge_rack['B3']
    # samp_4 = fuge_rack['B4']
    # samp_5 = fuge_rack['B5']
    # samp_6 = fuge_rack['B6']
    # samp_7 = fuge_rack['C1']

    # sds_rack  @ position 2
    # WATER = stds_rack['D1'] # 1500ul WATER
    SAMP_1mix = stds_rack['B1'] # empty
    SAMP_2mix = stds_rack['B2'] # empty
    SAMP_3mix = stds_rack['B3'] # empty
    SAMP_4mix = stds_rack['B4'] # empty
    SAMP_5mix = stds_rack['B5'] # empty
    SAMP_6mix = stds_rack['B6'] # empty
    SAMP_7mix = stds_rack['C1'] # empty
    SAMP_8mix = stds_rack['C2'] # empty
    # SAMP_2mix = stds_rack['B6'] # empty
    # SAMP_3mix = stds_rack['C1'] # empty
    # SAMP_4mix = stds_rack['C2'] # empty
    # SAMP_5mix = stds_rack['B5'] # empty
    # SAMP_6mix = stds_rack['B6'] # empty
    # SAMP_7mix = stds_rack['C1'] # empty
    # NTC_mix = stds_rack['D6'] # empty, receives sN_mix and WATER as NTC
    
    # user inputs
    num_of_sample_reps = 12
    # is num_of_sample_reps > 12?
    holderList = [holder_1, holder_2]
    add_sample_vol = 2
    tot_sample_vol = 20
    add_water_vol = tot_sample_vol-add_sample_vol
    # lists
    # ALL_SAMPs = [samp_1, samp_2, samp_3, samp_4, samp_5, samp_6, samp_7, WATER]
    SAMP_mixes = [SAMP_1mix, SAMP_2mix, SAMP_3mix, SAMP_4mix, SAMP_5mix, SAMP_6mix, SAMP_7mix, SAMP_8mix]
    SAMP_wells = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
    
    # #### COMMANDS ######    
    # Add sample DNA, mix, distribute to strip tubes
    for i, mixtube in enumerate(SAMP_mixes):
        p20.pick_up_tip()
        # p300.pick_up_tip()
        # p300.move_to(mixtube.bottom(40)) #prevent tip from crashing into tube cap
        # mix_vol = 0.70*num_of_sample_reps*tot_sample_vol*1.2 # mix 70% of total vol
        # if mix_vol < 200:
            # mix_vol = 0.70*num_of_sample_reps*tot_sample_vol*1.2 # mix 70% of total vol
        # else:
            # mix_vol = 200
        # p300.mix(7, mix_vol, mixtube.bottom(2))
        # protocol.delay(seconds=2)
        # p300.blow_out(mixtube.bottom(10))
        p20.move_to(mixtube.bottom(40))
        # num_of_sample_reps is another way of stating number of strips
        for y in range(0, len(holderList)):
            holderPos = y
            holder = holderList[holderPos]
            start = 6*y
            stop = num_of_sample_reps if num_of_sample_reps <= 6*y+6  else 6*y+6 # This is max it can go in cycle; can't go above e.g. A13 !<>
            for x in range(start, stop): # samples in 1-6, 7-12, 13-18 increments
                print ("start: ", start, "stop: ", stop)
                p20.aspirate(20, mixtube, rate=0.75) 
                protocol.delay(seconds=1) #equilibrate
                row = SAMP_wells[i]
                dest = row+str(2*x+1-12*holderPos) # need +1 offset for col 
                # dest = row+str(2*x+1-12*holderPos) # need +1 offset for col 
                # if (2*x+1) > 11:
                    # holder = holderList[holderPos+1]
                    # dest = row+str(2*x+1-12*holderPos)
                p20.move_to(mixtube.bottom(40)) #move p20 pipette +4cm so no crash into lyo tubes
                p20.move_to(holder[dest].bottom(40)) #move across holder in +4cm pos
                p20.dispense(20, holder[dest].bottom(6), rate=0.75) # more height so tip doesn't touch pellet
                protocol.delay(seconds=2)
                p20.move_to(holder[dest].bottom(6))
                p20.blow_out()
                p20.touch_tip()
                p20.move_to(holder[dest].bottom(40)) #move back holder in +4cm pos
                p20.move_to(mixtube.bottom(40)) #return to tube at +4cm so no crash into lyo tubes
        # p300.drop_tip()
        p20.drop_tip()