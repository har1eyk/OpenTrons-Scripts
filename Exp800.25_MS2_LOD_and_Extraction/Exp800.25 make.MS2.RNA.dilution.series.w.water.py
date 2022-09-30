# imports
from opentrons import protocol_api

# metadata
metadata = {
    'protocolName': 'Create 4-Fold RNA Dilution Series for Qauntified Sample',
    'author': 'Harley King <harley.king@luminultra.com>',
    'description': 'Create 12 tube dilution series on a 24-well alum block for RNA cooling.',
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
def tip_heightsEpp(init_vol, steps, vol_dec):
    vols = []
    heights = []
    # these values originate from Excel spreadsheet "Exp803..."
    p0=-0.272820744
    p1=0.019767959
    p2=2.00442E-06
    p3=-8.99691E-09
    p4=6.72776E-12
    p5=-1.55428E-15
    if init_vol > 2000:
        offset = 12 # model out of range; see sheet
    else:
        offset = 8 #mm Need to add offset to ensure tip reaches below liquid level
    for i in range(steps):
        x = init_vol-vol_dec*i
        vols.append(x)
        h = p5*x**5+p4*x**4+p3*x**3+p2*x**2+p1*x**1 + p0
        h = h-offset
        if h < 6: # prevent negative heights; go to bottom to avoid air aspirant above certain height
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
    # pos_rack = protocol.load_labware('vwr_24_tuberack_1500ul', '1')
    # fuge_rack = protocol.load_labware('opentrons_24_tuberack_generic_2ml_screwcap', '2')
    tiprack300 = protocol.load_labware('opentrons_96_filtertiprack_200ul', '8')
    # tiprack20 = protocol.load_labware('opentrons_96_filtertiprack_20ul', '9')
    # have this so I don't have to move it off
    # tempdeck = protocol.load_module('tempdeck', '4')
    sectempdeck = protocol.load_module('tempdeck', '1')
    # plate = tempdeck.load_labware('abi_96_wellplate_250ul')
    # swapped out 2mL generic for 1.5mL screwcap
    # need to test if this works 20220921 hjk
    fuge_rack = sectempdeck.load_labware(
        'opentrons_24_aluminumblock_generic_2ml_screwcap')
    water_rack = protocol.load_labware('opentrons_10_tuberack_falcon_4x50ml_6x15ml_conical', '2')

    # PIPETTES
    p300 = protocol.load_instrument(
        'p300_single_gen2', 'left', tip_racks=[tiprack300]
    )
    # p20 = protocol.load_instrument(
    #     'p20_single_gen2', 'right', tip_racks=[tiprack20]
    # )

    # REAGENTS
    a_std_1 = fuge_rack['A1']  # 980ul Water + 20ul  Already prepared
    a_std_2 = fuge_rack['A2']  # empty, water will be added
    a_std_3 = fuge_rack['A3']  # empty, water will be added
    a_std_4 = fuge_rack['A4']  # empty, water will be added
    a_std_5 = fuge_rack['A5']  # empty, water will be added
    a_std_6 = fuge_rack['A6']  # empty, water will be added
    a_std_7 = fuge_rack['B1']  # empty, water will be added
    a_std_8 = fuge_rack['B2']  # empty, water will be added
    a_std_9 = fuge_rack['B3']  # empty, water will be added
    a_std_10 = fuge_rack['B4']  #empty, water will be added
    a_std_11 = fuge_rack['B5']  #empty, water will be added
    a_std_12 = fuge_rack['B6']  #empty, water will be added
    a_std_13 = fuge_rack['C1']  #empty, water will be added
    a_std_14 = fuge_rack['C2']  #empty, water will be added
    a_std_15 = fuge_rack['C3']  #empty, water will be added
    a_std_16 = fuge_rack['C4']  #empty, water will be added
    a_std_17 = fuge_rack['C5']  #empty, water will be added
    a_std_18 = fuge_rack['C6']  #empty, water will be added
    
    water = water_rack['A1'] #750*18 =  13.5, 15mL tube okay. Fill to 15mL

    # LISTS
    stds = [a_std_1, a_std_2, a_std_3, a_std_4, a_std_5, a_std_6, a_std_7, a_std_8, a_std_9, a_std_10, a_std_11, a_std_12, a_std_13, a_std_14, a_std_15, a_std_16, a_std_17, a_std_18]

    ### COMMANDS ######
    # Add water to tubes
    waterH=fifteen_ml_heights(15000, 4*18+1 , 187.5) # 187.5*4=750ul
    dispenseH = tip_heights(750, 4, 187.5)
    p300.pick_up_tip()
    p300.mix(3, 200, water.bottom(waterH[0])) # pre-moisten tip
    for i in range(1,len(stds)): # don't need to add water to first tube
        std = stds[i]
        for h in range(1,5):
            p300.aspirate(187.5, water.bottom(waterH[4*i+h])) # function of std tube and current step 
            p300.dispense(187.5, std.bottom(dispenseH[-h])) # want to reverse heights
    p300.drop_tip()
   
    # Make std dilution series
    for i in range(len(stds)-1):
        p300.pick_up_tip()
        p300.mix(2, 200, stds[i].bottom(4))  # mix low
        p300.mix(2, 200, stds[i].bottom(8))  # mix mid
        p300.mix(5, 200, stds[i].bottom(16))  # mix hi
        p300.aspirate(125, stds[i].bottom(8)) # 2*150 = 250
        p300.touch_tip(v_offset=-3, speed=20)
        p300.dispense(125, stds[i+1].bottom(8))
        p300.mix(2, 125, stds[i+1].bottom(8))  # wash tip
        p300.blow_out(stds[i+1].bottom(16))  # blow out just below the surface
        p300.touch_tip(v_offset=-3, speed=20)
        p300.aspirate(125, stds[i].bottom(8))
        p300.touch_tip(v_offset=-3, speed=20)
        p300.dispense(125, stds[i+1].bottom(8))
        p300.mix(2, 125, stds[i+1].bottom(8))  # wash tip
        p300.blow_out(stds[i+1].bottom(16))  # blow out just below the surface
        p300.touch_tip(v_offset=-3, speed=20)
        p300.drop_tip()
        if i == len(stds)-2:  # last tube
            p300.pick_up_tip()
            p300.mix(2, 200, stds[i+1].bottom(4))  # mix low
            p300.mix(2, 200, stds[i+1].bottom(8))  # mix mid
            p300.mix(5, 200, stds[i+1].bottom(16))  # mix hi
            # blow out just below the surface
            p300.blow_out(stds[i+1].bottom(16))
            p300.drop_tip()
