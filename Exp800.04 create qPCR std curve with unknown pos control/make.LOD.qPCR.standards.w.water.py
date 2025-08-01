# imports
from opentrons import protocol_api

# metadata
metadata = {
    'protocolName': 'Create Pos Control Dilution Series for qPCR including 5 tubes for LOD. Uses Water on deck.',
    'author': 'Harley King <harley.king@luminultra.com>',
    'description': 'Create a 20-tube pos control dilution series on a 24-well rack.',
    'apiLevel': '2.12'
}
##########################
def tip_heights(init_vol, steps, vol_dec):
    vols = []
    heights = []
    # these values originate from Excel spreadsheet "Exp803..."
    p0=0.029502064
    p1=0.084625954
    p2=-0.000174864
    p3=2.18373E-07
    p4=-1.30599E-10
    p5=2.97839E-14
    if init_vol > 1500:
        offset = 14 # model out of range; see sheet
    else:
        offset = 7 #mm Need to add offset to ensure tip reaches below liquid level
    for i in range(steps):
        x = init_vol-vol_dec*i
        vols.append(x)
        h = p5*x**5+p4*x**4+p3*x**3+p2*x**2+p1*x**1 + p0
        h = h-offset
        if h < 8: # prevent negative heights; go to bottom to avoid air aspirant above certain height
            h = 1        
            heights.append(h)
        else:
            heights.append(round(h, 1))
    return heights
# calculate water level heights in 15mL tube
def fifteen_ml_heights(init_vol, steps, vol_dec):
    vols = []
    heights = []
    # these values originate from Excel spreadsheet "Volume.heights.in.15.0mL.conical.tube"
    p0 = 6.52
    p1 = 0.013
    p2 = -2.11E-6
    p3 = 3.02E-10
    p4 = -1.95E-14
    p5 = 4.65E-19
    if init_vol > 1500:  # where tube begins to cone
        offset = 5  # ensure tip contacts fluid
    else:  # if in cone portion
        offset = 5  # mm Need to add offset to ensure tip reaches below liquid level
    for i in range(steps):
        x = init_vol-vol_dec*i
        vols.append(x)
        h = p5*x**5+p4*x**4+p3*x**3+p2*x**2+p1*x**1 + p0
        h = h-offset
        if h < 8:  # prevent negative heights; go to bottom to avoid air aspirant above certain height
            h = 1
            heights.append(h)
        else:
            heights.append(round(h, 1))
    return heights
# Calc heights for 50mL conical tubes
def fifty_ml_heights(init_vol, steps, vol_dec):
    vols = []
    heights = []
    # these values originate from Excel spreadsheet "Exp803..."
    b = 0
    m = 0.0024
    if init_vol > 51000:
        offset = 12  # model out of range; see sheet
    else:
        offset = 5  # mm Need to add offset to ensure tip reaches below liquid level
    for i in range(steps):
        x = init_vol-vol_dec*i
        vols.append(x)
        h = m*x+b
        h = h-offset
        if h < 12:  # If less than 5mL remain in 50mL tube, go to bottom for asp
            h = 3
            heights.append(h)
        else:
            heights.append(round(h, 1))
    return heights

def run(protocol: protocol_api.ProtocolContext):

    # LABWARE
    pos_rack = protocol.load_labware('vwr_24_tuberack_1500ul', '1')
    fuge_rack = protocol.load_labware('vwr_24_tuberack_1500ul', '2')
    water_rack = protocol.load_labware('opentrons_10_tuberack_nest_4x50ml_6x15ml_conical', '3')
    tiprack300 = protocol.load_labware('opentrons_96_filtertiprack_200ul', '8')
    # tiprack20 = protocol.load_labware('opentrons_96_filtertiprack_20ul', '9')
    tempdeck = protocol.load_module('tempdeck', '10') # have this so I don't have to move it off
    # stds_plate = tempdeck.load_labware('abi_96_wellplate_250ul')
    
    # PIPETTES
    p300 = protocol.load_instrument(
        'p300_single_gen2', 'left', tip_racks=[tiprack300]
    )
    # p20 = protocol.load_instrument(
    #     'p20_single_gen2', 'right', tip_racks=[tiprack20]
    # )
     
    # REAGENTS 
    std_1 = fuge_rack['A1'] # no water; empty tube
    std_2 = fuge_rack['A2'] # no water; empty tube
    std_3 = fuge_rack['A3'] # no water; empty tube
    std_4 = fuge_rack['A4'] # no water; empty tube
    std_5 = fuge_rack['A5'] # no water; empty tube
    std_6 = fuge_rack['A6'] # no water ; empty tube
    std_7 = fuge_rack['B1'] # no water; empty tube
    std_8 = fuge_rack['B2'] # no water; empty tube
    std_9 = fuge_rack['B3'] # no water; empty tube
    std_10 = fuge_rack['B4'] #no water; empty tube
    std_11 = fuge_rack['B5'] #no water; empty tube
    std_12 = fuge_rack['B6'] #no water; empty tube
    std_13 = fuge_rack['C1'] #no water; empty tube
    std_14 = fuge_rack['C2'] #no water; empty tube
    std_15 = fuge_rack['C3'] #no water; empty tube
    
    std_11_1 = fuge_rack['D1'] # no water; empty tube
    std_11_2 = fuge_rack['D2'] # no water; empty tube
    std_11_3 = fuge_rack['D3'] # no water; empty tube
    std_11_4 = fuge_rack['D4'] # no water; empty tube
    std_11_5 = fuge_rack['D5'] # no water; empty tube

    # water rack
    water = water_rack['A3'] # 20mL water in 50mL conical tube, 900*15 = 13500ul: 300*5 = 1500ul = 15mL
    dilution_tube = std_10 # this is the tube used for LOD series; usually Tube_11.
    # Positive Control Rack 
    pos_control = pos_rack['A1'] # 100-1000ul pos control @1uM
    
    # LISTS
    std_wells = [std_1, std_2, std_3, std_4, std_5, std_6, std_7, std_8, std_9, std_10, std_11, std_12, std_13, std_14, std_15]
    lod_wells = [std_11_1, std_11_2, std_11_3, std_11_4, std_11_5]
    #### COMMANDS ######
   # fill tubes1..15 with water
    p300.pick_up_tip()
    waterH = fifty_ml_heights(20000, 76, 180) # 180*5=900, 15*5 = 75 total steps
    dispenseH = tip_heights(900, 5, 180)
    for i, stdTube in enumerate(std_wells):
        for h in range(1,6): #1 to 5
            p300.aspirate(180, water.bottom(waterH[5*i+h]))
            p300.dispense(180, stdTube.bottom(dispenseH[-h])) # want to reverse heights

    #fill tubes11_1..11.5 with water
    waterHLOD = fifty_ml_heights(20000-13500, 11, 150) # 150*2=300, 300*5 = 1500ul, need to add 10+1 so no list range error
    dispenseHLOD = tip_heights(900, 2, 150)
    for j, lodTube in enumerate(lod_wells):
        for r in range(1,3): #1 to 2
            p300.aspirate(150, water.bottom(waterHLOD[2*j+r]))
            p300.dispense(150, lodTube.bottom(dispenseHLOD[-r])) # want to reverse heights
    p300.drop_tip()
         
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

    # transfer 300ul from std_11 to std_11_1 to begin dilution series
    p300.pick_up_tip()
    for j in range(2):
        p300.aspirate(150, dilution_tube.bottom(8), rate=0.8)
        protocol.delay(seconds =2)
        p300.move_to(dilution_tube.bottom(15)) # move up to allow droplets to coalesce 
        p300.move_to(dilution_tube.bottom(8)) # touch to remove fluid
        p300.dispense(150, std_11_1.bottom(5))
        p300.mix(2, 200, std_11_1.bottom(8))
        p300.blow_out(std_11_1.bottom(15))
        p300.touch_tip()
    p300.drop_tip()
    
    # dilutions in LOD tubes; want at least 120*2 *1.2 = 288ul
    for i in range(len(lod_wells)-1):
        h_mix = 14
        p300.pick_up_tip()      
        p300.mix(2, 200, lod_wells[i].bottom(5)) # mix low
        p300.mix(2, 200, lod_wells[i].bottom(10)) # mix mid
        p300.mix(5, 200, lod_wells[i].bottom(h_mix)) #mix hi
        for z in range(2): # 2*150 = 300
            p300.aspirate(150, lod_wells[i].bottom(8), rate=0.8)
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