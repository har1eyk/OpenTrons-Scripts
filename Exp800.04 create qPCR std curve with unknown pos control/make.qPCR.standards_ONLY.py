# imports
from opentrons import protocol_api

# metadata
metadata = {
    'protocolName': 'Create Pos Control Dilution Series for qPCR',
    'author': 'Harley King <harley.king@luminultra.com>',
    'description': 'Create a 15-tube pos control dilution series on a 24-well rack.',
    'apiLevel': '2.10'
}
##########################
def run(protocol: protocol_api.ProtocolContext):

    # LABWARE
    fuge_rack = protocol.load_labware('vwr_24_tuberack_1500ul', '4')
    # water_rack = protocol.load_labware('opentrons_10_tuberack_falcon_4x50ml_6x15ml_conical', '5') 
    # tiprack300 = protocol.load_labware('opentrons_96_tiprack_300ul', '8')
    tiprack300 = protocol.load_labware('opentrons_96_filtertiprack_200ul', '8')
    # tiprack20 = protocol.load_labware('opentrons_96_tiprack_20ul', '9')
    tiprack20 = protocol.load_labware('opentrons_96_filtertiprack_20ul', '9')
    tempdeck = protocol.load_module('tempdeck', '10')
    # stds_plate = tempdeck.load_labware('amplifyt_96_aluminumblock_300ul')
    stds_plate = tempdeck.load_labware('abi_96_wellplate_250ul')
    
    # PIPETTES
    p300 = protocol.load_instrument(
        'p300_single_gen2', 'left', tip_racks=[tiprack300]
    )
    p20 = protocol.load_instrument(
        'p20_single_gen2', 'right', tip_racks=[tiprack20]
    )
     
    # REAGENTS 
    std_1 = fuge_rack['A1'] # 990ul Water
    std_2 = fuge_rack['A2'] # 900ul water
    std_3 = fuge_rack['A3'] # 900ul water
    std_4 = fuge_rack['A4'] # 900ul water
    std_5 = fuge_rack['A5'] # 900ul water
    std_6 = fuge_rack['A6'] # 900ul water 
    std_7 = fuge_rack['B1'] # 900ul water
    std_8 = fuge_rack['B2'] # 900ul water
    std_9 = fuge_rack['B3'] # 900ul water
    std_10 = fuge_rack['B4'] # 900ul water
    std_11 = fuge_rack['B5'] # 900ul water
    std_12 = fuge_rack['B6'] # 900ul water
    std_13 = fuge_rack['C1'] # 900ul water
    std_14 = fuge_rack['C2'] # 900ul water
    std_15 = fuge_rack['C3'] # 900ul water
    pos_control = fuge_rack['D1'] # pos control @1uM
    
    # LISTS
    std_wells = [std_1, std_2, std_3, std_4, std_5, std_6, std_7, std_8, std_9, std_10, std_11, std_12, std_13, std_14, std_15]
    tip_heights = [26.4,25.2,24,22.8,21.5,20.1,18.7,17.3,15.9,14.5,13.1,11.6,10,8,4.4,1]
    
   
    #### COMMANDS ######
    # Make std dilution series      
    # Make 10nM pos control, std_1
    p20.transfer(
        10,
        pos_control.bottom(20), #1uM
        std_1.bottom(20),
        mix_after=(2, 20), # remove residual fluid from tip
        blow_out=True,
        touch_tip=True,
        blowout_location='destination well'
    )
   
    # serial dilutions in microfuge tubes, 10% diliutions
    for i in range(len(std_wells)-1): 
        h_mix = 20
        p300.pick_up_tip()
        # if i==0: # first tube
            # p300.mix(5, 200, std_wells[i].bottom(h_mix)) # need to add mixes to first and last tubes
        p300.mix(2, 200, std_wells[i].bottom(8)) # mix low
        p300.mix(2, 200, std_wells[i].bottom(14)) # mix mid
        p300.mix(5, 200, std_wells[i].bottom(h_mix)) #mix hi
        p300.aspirate(100, std_wells[i].bottom(h_mix), rate=0.4)
        p300.touch_tip()
        p300.dispense(100, std_wells[i+1].bottom(14)) # better mixing with mid dispense
        p300.blow_out(std_wells[i+1].bottom(h_mix))# blow out just below the surface
        p300.drop_tip()
        if i==len(std_wells)-2: # last tube
            p300.pick_up_tip()
            p300.mix(2, 200, std_wells[i+1].bottom(8)) # mix low
            p300.mix(2, 200, std_wells[i+1].bottom(14)) # mix mid
            p300.mix(5, 200, std_wells[i+1].bottom(h_mix)) #mix hi
            p300.blow_out(std_wells[i+1].bottom(h_mix))# blow out just below the surface
            p300.drop_tip()
