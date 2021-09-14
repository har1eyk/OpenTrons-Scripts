# imports
from opentrons import protocol_api

# metadata
metadata = {
    'protocolName': 'Create Pos Control Dilution Series for qPCR including 5 tubes for LOD',
    'author': 'Harley King <harley.king@luminultra.com>',
    'description': 'Create a 20-tube pos control dilution series on a 24-well rack.',
    'apiLevel': '2.11'
}
##########################
def run(protocol: protocol_api.ProtocolContext):

    # LABWARE
    pos_rack = protocol.load_labware('vwr_24_tuberack_1500ul', '1')
    fuge_rack = protocol.load_labware('vwr_24_tuberack_1500ul', '2')
    tiprack300 = protocol.load_labware('opentrons_96_filtertiprack_200ul', '8')
    tiprack20 = protocol.load_labware('opentrons_96_filtertiprack_20ul', '9')
    tempdeck = protocol.load_module('tempdeck', '10') # have this so I don't have to move it off
    stds_plate = tempdeck.load_labware('abi_96_wellplate_250ul')
    
    # PIPETTES
    p300 = protocol.load_instrument(
        'p300_single_gen2', 'left', tip_racks=[tiprack300]
    )
    p20 = protocol.load_instrument(
        'p20_single_gen2', 'right', tip_racks=[tiprack20]
    )
     
    # REAGENTS 
    std_1 = fuge_rack['A1'] # 900ul Water
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
    
    std_11_1 = fuge_rack['D1'] # no water; empty tube
    std_11_2 = fuge_rack['D2'] # no water; empty tube
    std_11_3 = fuge_rack['D3'] # no water; empty tube
    std_11_4 = fuge_rack['D4'] # no water; empty tube
    std_11_5 = fuge_rack['D5'] # no water; empty tube

    pos_control = pos_rack['A1'] # 100-1000ul pos control @1uM
    water = pos_rack['D6'] # 100-1000ul pos control @1uM
    
    # LISTS
    std_wells = [std_1, std_2, std_3, std_4, std_5, std_6, std_7, std_8, std_9, std_10, std_11, std_12, std_13, std_14, std_15]
    lod_wells = [std_11_1, std_11_2, std_11_3, std_11_4, std_11_5]
    #### COMMANDS ######
    # Make std dilution series      
    # Make 10nM pos control, std_1
    p300.transfer(
        100,
        pos_control.bottom(2), #1uM
        std_1.bottom(20),
        mix_after=(3, 200), # remove residual fluid from tip
        touch_tip=False
    )
   
    # serial dilutions in microfuge tubes, 10% diliutions
    for i in range(len(std_wells)-1): 
        h_mix = 20
        p300.pick_up_tip()
        p300.mix(2, 200, std_wells[i].bottom(8)) # mix low
        p300.mix(2, 200, std_wells[i].bottom(14)) # mix mid
        p300.mix(5, 200, std_wells[i].bottom(h_mix)) #mix hi
        p300.aspirate(100, std_wells[i].bottom(h_mix), rate=0.8)
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

# move 300ul H2O into tubes; want this done with OT-2 pipette to reduce variability
    p300.pick_up_tip()
    for lod_tube in lod_wells:
        for j in range(2):
            p300.aspirate(150, water)
            protocol.delay(seconds =2)
            p300.touch_tip(v_offset = -3)
            p300.dispense(150, lod_tube)
            p300.blow_out()
            p300.touch_tip()
    p300.drop_tip()
    
    # transfer 300ul from std_11 to std_11_1 to begin dilution series
    p300.pick_up_tip()
    for j in range(2):
        p300.aspirate(150, std_11, rate=0.8)
        protocol.delay(seconds =2)
        p300.touch_tip(v_offset = -3)
        p300.dispense(150, std_11_1)
        p300.blow_out()
        p300.touch_tip()
    p300.drop_tip()
    
    # dilutions in LOD tubes; want at least 120*2 *1.2 = 288ul
    for i in range(len(lod_wells)-1):
        h_mix = 14
        p300.pick_up_tip()      
        p300.mix(2, 200, lod_wells[i].bottom(5)) # mix low
        p300.mix(2, 200, lod_wells[i].bottom(10)) # mix mid
        p300.mix(5, 200, lod_wells[i].bottom(h_mix)) #mix hi
        for z in range(2) # 2*150 = 300
            p300.aspirate(150, lod_wells[i].bottom(h_mix), rate=0.8)
            p300.touch_tip()
            p300.dispense(150, lod_wells[i+1].bottom(5)) # better mixing with mid dispense
            p300.blow_out(lod_wells[i+1].bottom(h_mix))# blow out just below the surface
        p300.drop_tip()
        if i==len(lod_wells)-2: # last tube
            p300.pick_up_tip()
            p300.mix(2, 200, lod_wells[i+1].bottom(5)) # mix low
            p300.mix(2, 200, lod_wells[i+1].bottom(10)) # mix mid
            p300.mix(5, 200, lod_wells[i+1].bottom(h_mix)) #mix hi
            p300.blow_out(lod_wells[i+1].bottom(h_mix))# blow out just below the surface
            p300.drop_tip() 