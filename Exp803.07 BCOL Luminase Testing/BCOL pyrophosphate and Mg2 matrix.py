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
    tiprack300 = protocol.load_labware('opentrons_96_filtertiprack_200ul', '8')
    tiprack20 = protocol.load_labware('opentrons_96_filtertiprack_20ul', '9')
    tempdeck = protocol.load_module('tempdeck', '10') # leaving on so I don't have to move off 
    plate = protocol.load_labware('corning_96_wellplate_360ul_flat', '3')
    mg2_dil =  protocol.load_labware('opentrons_24_tuberack_eppendorf_2ml_safelock_snapcap', '1')
    pyro_dil =  protocol.load_labware('opentrons_24_tuberack_eppendorf_2ml_safelock_snapcap', '2')
    reagent =  protocol.load_labware('opentrons_6_tuberack_nest_50ml_conical', '6')


    # PIPETTES
    p300 = protocol.load_instrument(
        'p300_single_gen2', 'left', tip_racks=[tiprack300]
    )
    p20 = protocol.load_instrument(
        'p20_single_gen2', 'right', tip_racks=[tiprack20]
    )
     
    # REAGENTS
    #reagent_rack
    # mg2+ dilution
    mg2std_1 = mg2_dil['A1'] # 800 uL 1 M mg2+ 
    mg2std_2 = mg2_dil['A2'] # 400uL water
    mg2std_3 = mg2_dil['A3'] # 400uL water
    mg2std_4 = mg2_dil['A4'] # 400uL water
    mg2std_5 = mg2_dil['A5'] # 400uL water
    mg2std_6 = mg2_dil['A6'] # 400uL water 
    mg2std_7 = mg2_dil['B1'] # 400uL water
    mg2std_8 = mg2_dil['B2'] # 400uL water
    mg2std_9 = mg2_dil['B3'] # 400uL water
    mg2std_10 = mg2_dil['B4'] # 400uL water
    mg2std_11 = mg2_dil['B5'] # 400uL water
    mg2std_12 = mg2_dil['B6'] # 400uL water
   
    # pyro dilution
    pyrostd_1 = pyro_dil['A1'] # 1000ul 50 mM pyrophosphate
    pyrostd_2 = pyro_dil['A2'] # 800ul water
    pyrostd_3 = pyro_dil['A3'] # 800ul water
    pyrostd_4 = pyro_dil['A4'] # 800ul water
    pyrostd_5 = pyro_dil['A5'] # 800ul water
    pyrostd_6 = pyro_dil['A6'] # 800ul water 
    pyrostd_7 = pyro_dil['B1'] # 800ul water
    pyrostd_8 = pyro_dil['B2'] # 800ul water

    LURB = reagent['A1']
  
    # lists
    mg2_std = [mg2std_1, mg2std_2, mg2std_3, mg2std_4, mg2std_5, mg2std_6, mg2std_7, mg2std_8, mg2std_9, mg2std_10, mg2std_11, mg2std_12]
    pyro_std = [pyrostd_1, pyrostd_2, pyrostd_3, pyrostd_4, pyrostd_5, pyrostd_6, pyrostd_7, pyrostd_8]
    rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
    cols = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]

    # #### COMMANDS ######
    # #pyrophosphate dilution with mix
    for i in range(len(pyro_std) -1):
        count = 1
        p300.pick_up_tip()
        p300.aspirate(200, pyro_std[i].bottom(5))
        p300.touch_tip()
        p300.dispense (200, pyro_std[i+1].bottom(5))
        for x in range(3):
            mixh = count*5 
            p300.aspirate(200, pyro_std[i+1].bottom(mixh))
            p300.dispense (200, pyro_std[i+1].bottom(mixh))
            count+= 1
        p300.touch_tip()
        p300.drop_tip()

    #mg2+ dilution with mix
    for i in range(len(mg2_std) -1):
        count = 1
        p300.pick_up_tip()
        p300.aspirate(200, mg2_std[i].bottom(5))
        p300.touch_tip()
        p300.dispense (200, mg2_std[i+1].bottom(5))
        p300.aspirate(200, mg2_std[i].bottom(5))
        p300.touch_tip()
        p300.dispense (200, mg2_std[i+1].bottom(5))
        for x in range(3):
            mixh = count*3 
            p300.aspirate(200, mg2_std[i+1].bottom(mixh))
            p300.dispense (200, mg2_std[i+1].bottom(mixh))
            count+= 1
        p300.touch_tip()
        p300.drop_tip()

    # # Dispense LURB
    sample_count = 0
    lurb_h = fifty_ml_heights(15000, 96, 80)
    for col in cols:
        p300.pick_up_tip()
        for row in rows:
            dest = row + str(col)
            p300.aspirate(80, LURB.bottom(lurb_h[sample_count]))
            p300.touch_tip
            p300.dispense(80, plate[dest].bottom(3))
            p300.move_to(plate[dest].bottom(1))
            sample_count += 1
        p300.drop_tip()
  
    # dispense pyrophosphate
    count = 0
    for row in rows:
        p20.pick_up_tip()
        for col in cols:
            dest = row + str(col)
            p20.aspirate(10, pyro_std[count])
            p20.touch_tip()
            p20.dispense(10, plate[dest])
            p20.aspirate(20, plate[dest].bottom(1))
            p20.dispense(20, plate[dest].bottom(1))
            p20.aspirate(20, plate[dest].bottom(1))
            p20.dispense(20, plate[dest].bottom(1))
            p20.move_to(plate[dest].bottom(1))
        p20.drop_tip()
        count += 1
    
    # dispense mg2
    count = 0
    for col in cols:
        p20.pick_up_tip()
        for row in rows:
            dest = row + str(col)
            p20.aspirate(10, mg2_std[count])
            p20.touch_tip()
            p20.dispense(10, plate[dest])
            p20.aspirate(20, plate[dest].bottom(1))
            p20.dispense(20, plate[dest].bottom(1))
            p20.aspirate(20, plate[dest].bottom(1))
            p20.dispense(20, plate[dest].bottom(1))
            p20.move_to(plate[dest].bottom(1))
        p20.drop_tip()
        count += 1

             


             

  
    
