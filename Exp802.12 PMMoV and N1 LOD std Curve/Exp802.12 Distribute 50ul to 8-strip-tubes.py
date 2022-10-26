# imports
from opentrons import protocol_api

# metadata
metadata = {
    'protocolName': 'Deliver 50ul from tubes on cooling rack to PCR tubes.',
    'author': 'Harley King <harley.king@luminultra.com>',
    'description': 'Add DNA or RNA to samples to lyophilized 8-well strip tubes. Tubes are held by 200 filter tip racks.',
    'apiLevel': '2.11'
}

def run(protocol: protocol_api.ProtocolContext):

    # LABWARE
    tiprack300 = protocol.load_labware('opentrons_96_filtertiprack_200ul', '8')
    tiprack20 = protocol.load_labware('opentrons_96_filtertiprack_20ul', '9')
    # tempdeck = protocol.load_module('tempdeck', '4')
    # plate = tempdeck.load_labware('opentrons_96_aluminumblock_generic_pcr_strip_200ul')
      # plate = tempdeck.load_labware('abi_96_wellplate_250ul')
    sectempdeck = protocol.load_module('tempdeck', '10')
    fuge_rack = sectempdeck.load_labware('opentrons_24_aluminumblock_generic_2ml_screwcap')
    holder_1 = protocol.load_labware('8wstriptubesonfilterracks_96_aluminumblock_250ul', '3')
    holder_2 = protocol.load_labware('8wstriptubesonfilterracks_96_aluminumblock_250ul', '6')
    # PIPETTES
    p300 = protocol.load_instrument(
        'p300_single_gen2', 'left', tip_racks=[tiprack300]
    )
    p20 = protocol.load_instrument(
        'p20_single_gen2', 'right', tip_racks=[tiprack20]
    )
    
    # REAGENTS
    SAMP_1mix = fuge_rack['B5']
    SAMP_2mix = fuge_rack['D1']
    SAMP_3mix = fuge_rack['D2']
    SAMP_4mix = fuge_rack['D3']
    SAMP_5mix = fuge_rack['B6']
    SAMP_6mix = fuge_rack['C1']
    SAMP_7mix = fuge_rack['C2']
    SAMP_8mix = fuge_rack['C3']
    
    
    # user inputs
    # num_of_sample_reps is another way of stating number of strips
    num_of_sample_reps = 6

    holderList = [holder_1]
    # lists
    # ALL_SAMPs = [samp_1, samp_2, samp_3, samp_4, samp_5, samp_6, samp_7, WATER]
    SAMP_mixes = [SAMP_1mix, SAMP_2mix, SAMP_3mix, SAMP_4mix, SAMP_5mix, SAMP_6mix, SAMP_7mix, SAMP_8mix]
    # SAMP_mixes = [SAMP_1mix, SAMP_2mix, SAMP_3mix, SAMP_4mix, SAMP_5mix, SAMP_6mix, SAMP_7mix, WATER]
    SAMP_wells = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
    
    # #### COMMANDS ######    
    # Add sample DNA, mix, distribute to strip tubes
    for i, mixtube in enumerate(SAMP_mixes):
        for y in range(0, len(holderList)):
            p300.pick_up_tip()
            p300.move_to(mixtube.bottom(40))
            p300.aspirate(num_of_sample_reps*20*1.08, mixtube.bottom(2)) # 6*20*1.08 = 130
            protocol.delay(seconds=1) #equilibrate
            p300.touch_tip(v_offset=-3)
            holderPos = y
            holder = holderList[holderPos]
            start = 6*y
            stop = num_of_sample_reps if num_of_sample_reps <= 6*y+6  else 6*y+6 # This is max it can go in cycle; can't go above e.g. A13 !<>
            for x in range(start, stop): # samples in 1-6, 7-12, 13-18 increments
                # print ("start: ", start, "stop: ", stop)
                row = SAMP_wells[i]
                dest = row+str(2*x+1-12*holderPos) # need +1 offset for col 
                p300.move_to(holder[dest].bottom(40)) #move across holder in +4cm pos
                p300.dispense(20, holder[dest].bottom(6), rate=0.75) # more height so tip doesn't touch pellet
                # p300.move_to(holder[dest].bottom(8))
                # p300.blow_out(holder[dest]. bottom(8))
                p300.touch_tip()
                p300.move_to(holder[dest].top()) # centers tip so tip doesn't lift tubes after touch
                p300.move_to(holder[dest].bottom(40)) #move across holder in +4cm pos
                # p300.move_to(holder[dest].bottom(40)) #move back holder in +4cm pos
                # p300.move_to(mixtube.bottom(40)) #return to tube at +4cm so no crash into lyo tubes
            p300.drop_tip()