# imports
from typing import Counter
from opentrons import protocol_api
from itertools import cycle, islice, repeat
from opentrons.commands.types import MoveToCommand

from opentrons.protocols.geometry.module_geometry import models_compatible
# metadata
metadata = {
    'protocolName': '2 varraible 96 well plate with standard dil',
    'author': 'Harley King <harley.king@luminultra.com>',
    'description': 'Create a 96w plate with luminase, ATP and lysing buffer to find max luminescence.',
    'apiLevel': '2.11'
}
##########################
# functions
# calculates ideal tip height for entering liquid
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
# Calc heights for 2mL Eppendorf tubes
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
        offset = 13 #mm Need to add offset to ensure tip reaches below liquid level
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
    epp_rack = protocol.load_labware('opentrons_24_tuberack_eppendorf_2ml_safelock_snapcap', '5')
    tiprack300 = protocol.load_labware('opentrons_96_filtertiprack_200ul', '8')
    # tiprack20 = protocol.load_labware('opentrons_96_filtertiprack_20ul', '9')
    tempdeck = protocol.load_module('tempdeck', '10') # leaving on so I don't have to move off 
    plate = protocol.load_labware('corning_96_wellplate_360ul_flat', '3')
    ATP_dil =  protocol.load_labware('opentrons_24_tuberack_eppendorf_2ml_safelock_snapcap', '1')
    LUC_dil =  protocol.load_labware('opentrons_24_tuberack_eppendorf_2ml_safelock_snapcap', '2')
    reagent =  protocol.load_labware('opentrons_6_tuberack_nest_50ml_conical', '6')


    # PIPETTES
    p300 = protocol.load_instrument(
        'p300_single_gen2', 'left', tip_racks=[tiprack300]
    )
    # p20 = protocol.load_instrument(
    #     'p20_single_gen2', 'right', tip_racks=[tiprack20]
    # )
     
    # REAGENTS
    #reagent_rack
    # ATP+ dilution
    ATPstd_1 = ATP_dil['A1'] # 1000 uL 1 mM ATP 
    ATPstd_2 = ATP_dil['A2'] # 900uL water
    ATPstd_3 = ATP_dil['A3'] # 900uL water
    ATPstd_4 = ATP_dil['A4'] # 900uL water
    ATPstd_5 = ATP_dil['A5'] # 900uL water
    ATPstd_6 = ATP_dil['A6'] # 900uL water 
    ATPstd_7 = ATP_dil['B1'] # 900uL water
    ATPstd_8 = ATP_dil['B2'] # 900uL water
    ATPstd_9 = ATP_dil['B3'] # 900uL water
    ATPstd_10 = ATP_dil['B4'] # 900uL water
    ATPstd_11 = ATP_dil['B5'] # 900uL water
    ATPstd_12 = ATP_dil['B6'] # 900uL water
   
    # LUC dilution
    LUCstd_1 = LUC_dil['A1'] # 800ul 10 mM luciferin
    LUCstd_2 = LUC_dil['A2'] # 400ul water
    LUCstd_3 = LUC_dil['A3'] # 400ul water
    LUCstd_4 = LUC_dil['A4'] # 400ul water
    LUCstd_5 = LUC_dil['A5'] # 400ul water
    LUCstd_6 = LUC_dil['A6'] # 400ul water 
    LUCstd_7 = LUC_dil['B1'] # 400ul water
    LUCstd_8 = LUC_dil['B2'] # 400ul water

    LURB = reagent['A1']
  
    # lists
    ATP_std = [ATPstd_1, ATPstd_2, ATPstd_3, ATPstd_4, ATPstd_5, ATPstd_6, ATPstd_7, ATPstd_8, ATPstd_9, ATPstd_10, ATPstd_11, ATPstd_12]
    LUC_std = [LUCstd_1, LUCstd_2, LUCstd_3, LUCstd_4, LUCstd_5, LUCstd_6, LUCstd_7, LUCstd_8]
    rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
    cols = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]

    #### COMMANDS ######
    #Luciferin dilution with mix
    for i in range(len(LUC_std) -1):
        count = 1
        mixh = count*5 
        p300.pick_up_tip()
        p300.aspirate(200, LUC_std[i].bottom(5))
        p300.touch_tip()
        p300.dispense (200, LUC_std[i+1].bottom(5))
        p300.touch_tip()
        p300.aspirate(200, LUC_std[i].bottom(5))
        p300.touch_tip()
        p300.dispense (200, LUC_std[i+1].bottom(5))
        p300.touch_tip()
        for x in range(3):
            p300.aspirate(200, LUC_std[i+1].bottom(mixh))
            p300.dispense (200, LUC_std[i+1].bottom(mixh))
            count+= 1
        p300.drop_tip()

    #ATP dilution with mix
    for i in range(len(ATP_std) -1):
        p300.pick_up_tip()
        p300.aspirate(100, ATP_std[i].bottom(5))
        p300.touch_tip()
        p300.dispense (100, ATP_std[i+1].bottom(5))
        for x in range(3):
            p300.aspirate(100, ATP_std[i+1].bottom(5))
            p300.dispense (100, ATP_std[i+1].bottom(5))
        p300.drop_tip()

    # Dispense LURB
    sample_count = 0
    lurb_h = fifty_ml_heights(15000, 96, 100)
    for col in cols:
        p300.pick_up_tip()
        for row in rows:
            dest = row + str(col)
            p300.aspirate(100, LURB.bottom(lurb_h[sample_count]))
            p300.touch_tip
            p300.dispense(100, plate[dest].bottom(3))
            p300.move_to(plate[dest].bottom(1))
            sample_count += 1
        p300.drop_tip()
  
  
    # dispense luciferin 
    count = 0
    for row in rows:
        p300.pick_up_tip()
        p300.aspirate(140, LUC_std[count].bottom(5))
        p300.touch_tip()
        for col in cols[:6]:
            dest = row + str(col)
            p300.dispense(20, plate[dest])
            p300.aspirate(50, plate[dest].bottom(1))
            p300.dispense(50, plate[dest].bottom(1))
            p300.move_to(plate[dest].bottom(1))
        p300.aspirate(140, LUC_std[count].bottom(5))
        p300.touch_tip()
        for col in cols[6:]:
            dest = row + str(col)
            p300.dispense(20, plate[dest])
            p300.aspirate(50, plate[dest].bottom(1))
            p300.dispense(50, plate[dest].bottom(1))
            p300.move_to(plate[dest].bottom(1))
        count += 1
        p300.drop_tip()

    # Dispense ATP
    count = 0
    for col in cols:
        p300.pick_up_tip()
        for row in rows:
            dest = row + str(col)
            p300.aspirate(100, ATP_std[count].bottom(5))
            p300.touch_tip
            p300.dispense(100, plate[dest].bottom(3))
            p300.move_to(plate[dest].bottom(1))
        count += 1
        p300.drop_tip()


             

  
    
