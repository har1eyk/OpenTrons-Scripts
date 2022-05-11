# imports
from opentrons import protocol_api

# metadata
metadata = {
    'protocolName': 'Create RNA Dilution Series for Qauntified Sample',
    'author': 'Harley King <harley.king@luminultra.com>',
    'description': 'Create 8 tube dilution series on a 24-well rack for RNA cooling.',
    'apiLevel': '2.12'
}
##########################


def run(protocol: protocol_api.ProtocolContext):

    # LABWARE
    # pos_rack = protocol.load_labware('vwr_24_tuberack_1500ul', '1')
    # fuge_rack = protocol.load_labware('opentrons_24_tuberack_generic_2ml_screwcap', '2')
    tiprack300 = protocol.load_labware('opentrons_96_filtertiprack_200ul', '8')
    # tiprack20 = protocol.load_labware('opentrons_96_filtertiprack_20ul', '9')
    # have this so I don't have to move it off
    # tempdeck = protocol.load_module('tempdeck', '4')
    sectempdeck = protocol.load_module('tempdeck', '10')
    # plate = tempdeck.load_labware('abi_96_wellplate_250ul')
    fuge_rack = sectempdeck.load_labware(
        'opentrons_24_aluminumblock_generic_2ml_screwcap')

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
