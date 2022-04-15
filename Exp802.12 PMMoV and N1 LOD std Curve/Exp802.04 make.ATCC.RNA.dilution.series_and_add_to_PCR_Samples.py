# imports
from opentrons import protocol_api

# metadata
metadata = {
    'protocolName': 'Create RNA Dilution Series for Qauntified Sample and then add to PCR Samples',
    'author': 'Harley King <harley.king@luminultra.com>',
    'description': 'Create 12 tube dilution series on a 24-well rack for RNA cooling. Add to PCR samples.',
    'apiLevel': '2.12'
}
##########################


def run(protocol: protocol_api.ProtocolContext):

    # LABWARE
    tiprack300 = protocol.load_labware('opentrons_96_filtertiprack_200ul', '8')
    # tiprack20 = protocol.load_labware('opentrons_96_filtertiprack_20ul', '9')
    sectempdeck = protocol.load_module('tempdeck', '10')
    fuge_rack = sectempdeck.load_labware(
        # 'opentrons_24_aluminumblock_generic_2ml_screwcap')
        'opentrons_24_aluminumblock_nest_1.5ml_screwcap')
    holder_1 = protocol.load_labware('8wstriptubesonfilterracks_96_aluminumblock_250ul', '3')
    holder_2 = protocol.load_labware('8wstriptubesonfilterracks_96_aluminumblock_250ul', '6')
    # PIPETTES
    p300 = protocol.load_instrument(
        'p300_single_gen2', 'left', tip_racks=[tiprack300]
    )
    # p20 = protocol.load_instrument(
    #     'p20_single_gen2', 'right', tip_racks=[tiprack20]
    # )

    # REAGENTS
    a_std_1 = fuge_rack['A1']  # 980ul Water + 20ul  Already prepared
    a_std_2 = fuge_rack['A2']  # 750ul water
    a_std_3 = fuge_rack['A3']  # 750ul water
    a_std_4 = fuge_rack['A4']  # 750ul water
    a_std_5 = fuge_rack['A5']  # 750ul water
    a_std_6 = fuge_rack['A6']  # 750ul water
    a_std_7 = fuge_rack['D1']  # 750ul water
    a_std_8 = fuge_rack['D2']  # 750ul water
    a_std_9 = fuge_rack['D3']  # 750ul water
    a_std_10 = fuge_rack['D4']  # 750ul water
    a_std_11 = fuge_rack['D5']  # 750ul water
    a_std_12 = fuge_rack['D6']  # 750ul water



    # LISTS
    stds = [a_std_1, a_std_2, a_std_3, a_std_4, a_std_5, a_std_6,
            a_std_7, a_std_8, a_std_9, a_std_10, a_std_11, a_std_12]
    stds_to_add_to_PCR_tubes = [a_std_3, a_std_4, a_std_5, a_std_6, a_std_7, a_std_8, a_std_9, a_std_10]
    num_of_sample_reps_per_holder = 6 # can't exceed 6
    holderList = [holder_1, holder_2]
    SAMP_wells = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']

    #### COMMANDS ######
    # Make std dilution series
    for i in range(len(stds)-1):
       p300.pick_up_tip()
       p300.mix(2, 200, stds[i].bottom(4))  # mix low
       p300.mix(2, 200, stds[i].bottom(8))  # mix mid
       p300.mix(5, 200, stds[i].bottom(16))  # mix hi
       p300.aspirate(125, stds[i].bottom(8)) # 2*150 = 250
       p300.touch_tip(v_offset=-3)
       p300.dispense(125, stds[i+1].bottom(8))
       p300.mix(2, 125, stds[i+1].bottom(8))  # wash tip
       p300.blow_out(stds[i+1].bottom(16))  # blow out just below the surface
       p300.touch_tip(v_offset=-3)
       p300.aspirate(125, stds[i].bottom(8))
       p300.touch_tip(v_offset=-3)
       p300.dispense(125, stds[i+1].bottom(8))
       p300.mix(2, 125, stds[i+1].bottom(8))  # wash tip
       p300.blow_out(stds[i+1].bottom(16))  # blow out just below the surface
       p300.touch_tip(v_offset=-3)
       p300.drop_tip()
       if i == len(stds)-2:  # last tube
          p300.pick_up_tip()
          p300.mix(2, 200, stds[i+1].bottom(4))  # mix low
          p300.mix(2, 200, stds[i+1].bottom(8))  # mix mid
          p300.mix(5, 200, stds[i+1].bottom(16))  # mix hi
            # blow out just below the surface
          p300.blow_out(stds[i+1].bottom(16))
          p300.drop_tip()

# Add to PCR samples
# Add sample DNA, mix, distribute to strip tubes
    for i, mixtube in enumerate(stds_to_add_to_PCR_tubes):
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