# imports
from opentrons import protocol_api

# metadata
metadata = {
    'protocolName': 'Create RNA Dilution Series for qPCR',
    'author': 'Harley King <harley.king@luminultra.com>',
    'description': 'Create 7 tube dilution series on a 24-well rack.',
    'apiLevel': '2.11'
}
##########################
def run(protocol: protocol_api.ProtocolContext):

    # LABWARE
    # pos_rack = protocol.load_labware('vwr_24_tuberack_1500ul', '1')
    # fuge_rack = protocol.load_labware('opentrons_24_tuberack_generic_2ml_screwcap', '2')
    tiprack300 = protocol.load_labware('opentrons_96_filtertiprack_200ul', '8')
    tiprack20 = protocol.load_labware('opentrons_96_filtertiprack_20ul', '9')
    tempdeck = protocol.load_module('tempdeck', '10') # have this so I don't have to move it off
    sectempdeck = protocol.load_module('tempdeck', '4') 
    plate = tempdeck.load_labware('abi_96_wellplate_250ul')
    fuge_rack = sectempdeck.load_labware('opentrons_24_aluminumblock_generic_2ml_screwcap')    
    
    # PIPETTES
    p300 = protocol.load_instrument(
        'p300_single_gen2', 'left', tip_racks=[tiprack300]
    )
    p20 = protocol.load_instrument(
        'p20_single_gen2', 'right', tip_racks=[tiprack20]
    )
     
    # REAGENTS 
    a_std_1 = fuge_rack['A1'] # 980ul Water + 20ul STD
    a_std_2 = fuge_rack['A2'] # 750ul water
    a_std_3 = fuge_rack['A3'] # 750ul water
    a_std_4 = fuge_rack['A4'] # 750ul water
    a_std_5 = fuge_rack['A5'] # 750ul water
    a_std_6 = fuge_rack['A6'] # 750ul water 
    a_std_7 = fuge_rack['D1'] # 750ul water
    b_std_1 = fuge_rack['B1'] # 980ul Water + 20ul STD
    b_std_2 = fuge_rack['B2'] # 750ul water
    b_std_3 = fuge_rack['B3'] # 750ul water
    b_std_4 = fuge_rack['B4'] # 750ul water
    b_std_5 = fuge_rack['B5'] # 750ul water
    b_std_6 = fuge_rack['B6'] # 750ul water 
    b_std_7 = fuge_rack['D2'] # 750ul water
    c_std_1 = fuge_rack['C1'] # 980ul Water + 20ul STD
    c_std_2 = fuge_rack['C2'] # 750ul water
    c_std_3 = fuge_rack['C3'] # 750ul water
    c_std_4 = fuge_rack['C4'] # 750ul water
    c_std_5 = fuge_rack['C5'] # 750ul water
    c_std_6 = fuge_rack['C6'] # 750ul water 
    c_std_7 = fuge_rack['D3'] # 750ul water

    # LISTS
    a_stds = [a_std_1, a_std_2, a_std_3, a_std_4, a_std_5, a_std_6, a_std_7]
    b_stds = [b_std_1, b_std_2, b_std_3, b_std_4, b_std_5, b_std_6, b_std_7]
    c_stds = [c_std_1, c_std_2, c_std_3, c_std_4, c_std_5, c_std_6, c_std_7]
    all_stds = [a_stds, b_stds, c_stds]

    #### COMMANDS ######
    # Make std dilution series         
    for stds in all_stds:      
        for i in range(len(stds)-1): 
            p300.pick_up_tip()
            p300.mix(2, 200, stds[i].bottom(4)) # mix low
            p300.mix(2, 200, stds[i].bottom(8)) # mix mid
            p300.mix(5, 200, stds[i].bottom(16)) #mix hi
            p300.aspirate(125, stds[i].bottom(8))
            p300.touch_tip()
            p300.dispense(125, stds[i+1].bottom(8))
            p300.blow_out(stds[i+1].bottom(16))# blow out just below the surface
            p300.touch_tip()
            p300.aspirate(125, stds[i].bottom(8))
            p300.touch_tip()
            p300.dispense(125, stds[i+1].bottom(8))
            p300.blow_out(stds[i+1].bottom(16))# blow out just below the surface
            p300.touch_tip()
            p300.drop_tip()
            if i==len(stds)-2: # last tube
                p300.pick_up_tip()
                p300.mix(2, 200, stds[i+1].bottom(4)) # mix low
                p300.mix(2, 200, stds[i+1].bottom(8)) # mix mid
                p300.mix(5, 200, stds[i+1].bottom(16)) #mix hi
                p300.blow_out(stds[i+1].bottom(16))# blow out just below the surface
                p300.drop_tip()
