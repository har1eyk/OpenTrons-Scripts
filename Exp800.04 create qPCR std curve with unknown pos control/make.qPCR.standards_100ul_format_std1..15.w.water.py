# imports
from opentrons import protocol_api

# metadata
metadata = {
    'protocolName': 'Create 15-tube Dilution Series with Std_0 (6e11).',
    'author': 'Harley King <harley.king@luminultra.com>',
    'description': 'Create a 15-tube pos control dilution series on a 24-well rack. 900ul water also added from 15mL tube.',
    'apiLevel': '2.12'
}
##########################
# calculate water dispense heights in 1.5mL tube
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

def run(protocol: protocol_api.ProtocolContext):

    # LABWARE
    pos_rack = protocol.load_labware('vwr_24_tuberack_1500ul', '1')
    fuge_rack = protocol.load_labware('vwr_24_tuberack_1500ul', '2')
    water_rack = protocol.load_labware('opentrons_10_tuberack_nest_4x50ml_6x15ml_conical', '3')
    tiprack300 = protocol.load_labware('opentrons_96_filtertiprack_200ul', '8')
    # tiprack20 = protocol.load_labware('opentrons_96_filtertiprack_20ul', '9')
    # tempdeck = protocol.load_module('tempdeck', '10') # have this so I don't have to move it off
    # stds_plate = tempdeck.load_labware('abi_96_wellplate_250ul')
    
    # PIPETTES
    p300 = protocol.load_instrument(
        'p300_single_gen2', 'left', tip_racks=[tiprack300]
    )
    # p20 = protocol.load_instrument(
    #     'p20_single_gen2', 'right', tip_racks=[tiprack20]
    # )
     
    # REAGENTS 
    std_1 = fuge_rack['A1'] # no water
    std_2 = fuge_rack['A2'] # no water
    std_3 = fuge_rack['A3'] # no water
    std_4 = fuge_rack['A4'] # no water
    std_5 = fuge_rack['A5'] # no water
    std_6 = fuge_rack['A6'] #  no water
    std_7 = fuge_rack['B1'] # no water
    std_8 = fuge_rack['B2'] # no water
    std_9 = fuge_rack['B3'] # no water
    std_10 = fuge_rack['B4'] # no water
    std_11 = fuge_rack['B5'] # no water
    std_12 = fuge_rack['B6'] # no water
    std_13 = fuge_rack['C1'] # no water
    std_14 = fuge_rack['C2'] # no water
    std_15 = fuge_rack['C3'] # no water

    pos_control = pos_rack['A1'] # 100-1000ul pos control @1uM
    
    water = water_rack['A1'] # 15mL water in 15mL conical

    # LISTS
    std_wells = [std_1, std_2, std_3, std_4, std_5, std_6, std_7, std_8, std_9, std_10, std_11, std_12, std_13, std_14, std_15]

    #### COMMANDS ######
    # fill tubes with water
    p300.pick_up_tip()
    waterH = fifteen_ml_heights(15000, 76, 180) # 180*5=900, 15*5 = 75 total steps
    dispenseH = tip_heights(900, 5, 180)
    p300.mix(2,200, water.bottom(waterH[3])) # pre-wet tip for more accurate dispenses at top water height.
    for i, stdTube in enumerate(std_wells):
        for h in range(1,6): #1 to 5
            p300.aspirate(180, water.bottom(waterH[5*i+h]))
            p300.dispense(180, stdTube.bottom(dispenseH[-h])) # want to reverse heights
    p300.drop_tip()

    # Make std dilution series      
    # Make 10nM pos control, std_1
    p300.transfer(
        100,
        pos_control.bottom(2), #1uM
        std_1.bottom(20),
        mix_after=(3, 200), # remove residual fluid from tip
        touch_tip=True
    )
   
    # serial dilutions in microfuge tubes, 10% diliutions
    for i in range(len(std_wells)-1): 
        h_mix = 20
        p300.pick_up_tip()
        p300.mix(2, 200, std_wells[i].bottom(8)) # mix low
        p300.mix(2, 200, std_wells[i].bottom(14)) # mix mid
        p300.mix(5, 200, std_wells[i].bottom(h_mix)) #mix hi
        p300.aspirate(100, std_wells[i].bottom(h_mix), rate=0.4)
        p300.touch_tip()
        p300.dispense(100, std_wells[i+1].bottom(14)) # better mixing with mid dispense
        p300.mix(2, 100, std_wells[i+1].bottom(14)) # ensure tip is rinsed 
        p300.blow_out(std_wells[i+1].bottom(h_mix))# blow out just below the surface
        p300.drop_tip()
        if i==len(std_wells)-2: # last tube
            p300.pick_up_tip()
            p300.mix(2, 200, std_wells[i+1].bottom(8)) # mix low
            p300.mix(2, 200, std_wells[i+1].bottom(14)) # mix mid
            p300.mix(5, 200, std_wells[i+1].bottom(h_mix)) #mix hi
            p300.blow_out(std_wells[i+1].bottom(h_mix))# blow out just below the surface
            p300.drop_tip()
