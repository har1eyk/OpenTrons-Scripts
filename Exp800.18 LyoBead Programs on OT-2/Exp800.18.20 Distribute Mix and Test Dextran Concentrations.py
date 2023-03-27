# imports
from re import I
from opentrons import protocol_api

# metadata
metadata = {
    'protocolName': 'Distribute 14ul COVID-19 RT qPCR mmix and Add Dextran and Water to 20ul.',
    'author': 'Harley King <harley.king@luminultra.com>',
    'description': 'Testing Dextran Concentrations in LyoReady Mastermix.',
    'apiLevel': '2.13'
}

##########################
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
        offset = 11 #mm Need to add offset to ensure tip reaches below liquid level
    for i in range(steps):
        x = init_vol-vol_dec*i
        vols.append(x)
        h = p5*x**5+p4*x**4+p3*x**3+p2*x**2+p1*x**1 + p0
        h = h-offset
        if h < 7: # prevent negative heights; go to bottom to avoid air aspirant above certain height
            h = 1        
            heights.append(h)
        else:
            heights.append(round(h, 1))
    return heights

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

# Calc heights for 50mL conical tubes
def fifty_ml_heights(init_vol, steps, vol_dec):
    vols = []
    heights = []
    # these values originate from Excel spreadsheet "Exp803..."
    b = 0
    m = 0.0024
    if init_vol > 51000:
        offset = 14  # model out of range; see sheet
    else:
        offset = 15  # mm Need to add offset to ensure tip reaches below liquid level
    for i in range(steps):
        x = init_vol-vol_dec*i
        vols.append(x)
        h = m*x+b
        h = h-offset
        if h < 17.5:  # If less than 5mL remain in 50mL tube, go to bottom for asp
            h = 2
            heights.append(h)
        else:
            heights.append(round(h, 1))
    return heights

def run(protocol: protocol_api.ProtocolContext):

    # EXPERIMENT OUTLINE
    # This experiment tests if dextran concentrations in the LyoReady Mastermix affects the qPCR results.
    # Dextran is in 50mL tube
    # LyoReady mastermix (or other) are added to 12, 1.5mL tubes chilled in temp module. EAch column is a concentration of Dextran. 12 different concentrations.
    # To these tubes dextran and water are added, mixed and aliquoted to PCR plate.

    # LABWARE
    tiprack300 = protocol.load_labware('opentrons_96_filtertiprack_200ul', '8')
    tiprack20 = protocol.load_labware('opentrons_96_filtertiprack_20ul', '9')
    
    tempdeck = protocol.load_module('tempdeck', '1')
    # pcr_plate = tempdeck.load_labware('bioer_96_aluminumblock_200ul.json')
    plate = tempdeck.load_labware('bioer_96_aluminumblock_200ul')
    
    tempdeckTwo = protocol.load_module('tempdeck', '7')
    alumBlock = tempdeckTwo.load_labware('opentrons_24_aluminumblock_nest_1.5ml_snapcap')

    reagent_rack = protocol.load_labware('opentrons_10_tuberack_nest_4x50ml_6x15ml_conical', '11')

    # PIPETTES
    p20 = protocol.load_instrument(
        'p20_single_gen2', 'right', tip_racks=[tiprack20]
    )

    p300 = protocol.load_instrument(
        'p300_single_gen2', 'left', tip_racks=[tiprack300]
    )
    
    # REAGENTS   
    cond_1 = alumBlock['A1']  # empty, "conditions" for each column
    cond_2 = alumBlock['A2']  # empty
    cond_3 = alumBlock['A3']  # empty
    cond_4 = alumBlock['A4']  # empty
    cond_5 = alumBlock['A5']  # empty
    cond_6 = alumBlock['A6']  # empty
    cond_7 = alumBlock['B1']  # empty
    cond_8 = alumBlock['B2']  # empty
    cond_9 = alumBlock['B3']  # empty
    cond_10 = alumBlock['B4']  # empty
    cond_11 = alumBlock['B5']  # empty
    cond_12 = alumBlock['B6']  # empty
          
    LU_Mix = alumBlock['D1'] # LU MasterMix; 14*96*1.10 = 1584ul

    dextran = reagent_rack['A3'] # 50mL tube with dextran
    water = reagent_rack['A4'] # 50mL tube with water
    
    # USER INPUT
    dextran_beg_vol= 700 # dextran volume in ul
    water_beg_vol = 700 # water volume in ul

    # LISTS
    rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
    conds = [cond_1, cond_2, cond_3, cond_4, cond_5, cond_6, cond_7, cond_8, cond_9, cond_10, cond_11, cond_12]
    excess = 1.05
    # disp_locs = ['A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8', 'A9', 'A10', 'A11', 'A12'] #DISPENSE LOCATIONS ON PCR PLATE
    dextranVols =[0, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5, 5.5, 6] # dextran volumes in 20ul rxn. 4/20 at 25% = 5% dextran, current concentration in mastermixes
    waterVols= [20-14-vol for vol in dextranVols] #  
    print ("dextranVols: ", dextranVols)
    print ("waterVols: ", waterVols)

    # #### COMMANDS ######    
    # 1.1 Add 14*8*excess = 117.6ul of LU MasterMix to condition tube on alum block
    # 1.2 Add Dextran*14*8*excess to condition tube on alum block
    # 1.3 Add 2[0-(14-Dextran)]*excess to condition tube on alum block
    # 1.4 mix condition tubes on alum block and aliquot to PCR plate

    # 1.1 Add 14*8*excess = 117.6ul of LU MasterMix to condition tube on alum block
    h_list = tip_heights(1584, 12, 117.6)
    p300.pick_up_tip()
    p300.mix(3, 200, LU_Mix.bottom(h_list[0]))
    for tube in conds:
        p300.aspirate(8*14*excess, LU_Mix.bottom(h_list[0]), rate=0.75) # 8*14*excess = 117.6ul
        p300.touch_tip(v_offset=-3, speed=30)
        p300.dispense(8*14*excess, tube.bottom(1))
        p300.blow_out(tube.bottom(tip_heights(8*14*excess,1,1)[0]))
    p300.drop_tip()

    # 1.2 Add Dextran*14*8*excess to condition tube on alum block
    dextranVolsTube = [vol*excess*8 for vol in dextranVols] # dextran volumes in 20ul rxn. 4/20 at 25% = 5% dextran, current concentration in mastermixes
    print ("dextranVolsTube: ", dextranVolsTube)
    d_heights= fifty_ml_heights(dextran_beg_vol, 12, int(sum(dextranVolsTube)/len(dextranVolsTube)) ) # average dextran volume per tube
    for dVol, tube, h in zip(dextranVolsTube, conds, d_heights):
        if dVol < 0.01: # OT-2 logic needs this because if aspirate vol = 0 then default will be 20ul. 
            continue
        if dVol < 20:
            p20.pick_up_tip()
            p20.mix(1, 20, dextran.bottom(h))
            p20.aspirate(dVol, dextran.bottom(h), rate=0.5)
            p20.touch_tip(v_offset=-3, speed=30)
            p20.dispense(dVol, tube.bottom(4))
            p20.blow_out(tube.bottom(tip_heights(14*8*excess+dVol,1,1)[0]))
            p20.drop_tip()
        else: 
            p300.pick_up_tip()
            p300.mix(1, 200, dextran.bottom(h))
            p300.aspirate(dVol, dextran.bottom(h), rate=0.5)
            p300.touch_tip(v_offset=-3, speed=30)
            p300.dispense(dVol, tube.bottom(4))
            p300.blow_out(tube.bottom(tip_heights(14*8*excess+dVol,1,1)[0]))
            p300.drop_tip()
    
    # 1.3 Add 2[0-(14-Dextran)]*excess to condition tube on alum block
    waterVolsTube = [vol*8*excess for vol in waterVols] # water volumes in tubes
    print ("waterVolsTube: ", waterVolsTube)
    w_heights= fifty_ml_heights(water_beg_vol, 12, int(sum(waterVolsTube)/len(waterVolsTube)) ) # average dextran volume per tube
    for wVol, tube, h in zip(waterVolsTube, conds, w_heights):
        if wVol < 0.01: # OT-2 logic needs this because if aspirate vol = 0 then default will be 20ul.
            continue
        if wVol < 20:
            p20.pick_up_tip()
            p20.mix(1, 20, water.bottom(h))
            p20.aspirate(wVol, water.bottom(h), rate=0.5)
            # p20.touch_tip(v_offset=-3, speed=30) # don't need to touch off water, no beads
            p20.dispense(wVol, tube.bottom(4))
            p20.blow_out(tube.bottom(tip_heights(14*8*excess+wVol,1,1)[0]))
            p20.drop_tip()
        else: 
            p300.pick_up_tip()
            p300.mix(1, 200, water.bottom(h))
            p300.aspirate(wVol, water.bottom(h), rate=0.5)
            p300.touch_tip(v_offset=-3, speed=30)
            p300.dispense(wVol, tube.bottom(4))
            p300.blow_out(tube.bottom(tip_heights(14*8*excess+wVol,1,1)[0]))
            p300.drop_tip()

    # 1.4 mix condition tubes on alum block and aliquot to PCR plate
    p300.pick_up_tip()
    for col, tube in enumerate(conds):
        tube_height = tip_heights(168, 8, 20)
        p20.pick_up_tip()
        p300.mix(2, 150, tube.bottom(2)) # tube total volume = 168
        p300.blow_out(tube.bottom(tube_height[0]))
        p300.touch_tip(v_offset=-3, speed=30)
        for i, row in enumerate(rows):
            p20.aspirate(20, tube.bottom(tube_height[i]), rate=0.75)
            dest = row+str(col+1) 
            p20.dispense(20, plate[dest].bottom(2))
        p20.drop_tip()
    p300.drop_tip()


    
