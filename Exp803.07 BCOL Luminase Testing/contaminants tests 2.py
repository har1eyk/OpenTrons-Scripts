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
    # tempdeck = protocol.load_module('tempdeck', '10') # leaving on so I don't have to move off 
    plate = protocol.load_labware('corning_96_wellplate_360ul_flat', '3')
    contam =  protocol.load_labware('opentrons_24_tuberack_eppendorf_2ml_safelock_snapcap', '1')
    reagent =  protocol.load_labware('opentrons_24_tuberack_eppendorf_2ml_safelock_snapcap', '2')


    # PIPETTES
    p300 = protocol.load_instrument(
        'p300_single_gen2', 'left', tip_racks=[tiprack300]
    )
    p20 = protocol.load_instrument(
        'p20_single_gen2', 'right', tip_racks=[tiprack20]
    )
     
    # REAGENTS
    #contam
    A = contam['A1']
    B = contam['A2']
    X3 = contam['A3']
    W = contam['A4']

    #reagent_rack
    prob = reagent['A1']
    ecoli = reagent['A2']
    atp = reagent['A3'] 
    lumisolve = reagent ['A4']
    lumisolve2 = reagent ['A5']
    lumisolve3 = reagent ['A6']
  
    # lists
    rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
    cols = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    contams = [A, B, X3, W]
    
    # #### COMMANDS ######
    # Add 50 uL sample and lumisolve
    for col in cols[:4]:
        p300.pick_up_tip()
        for row in rows:
            dest = row + str(col)
            p300.aspirate(50, lumisolve)
            p300.touch_tip()
            p300.dispense(50, plate[dest].bottom(5))
            p300.move_to(plate[dest].bottom(1))
        p300.drop_tip()
    
    for col in cols[4:8]:
        p300.pick_up_tip()
        for row in rows:
            dest = row + str(col)
            p300.aspirate(50, lumisolve2)
            p300.touch_tip()
            p300.dispense(50, plate[dest].bottom(5))
            p300.move_to(plate[dest].bottom(1))
        p300.drop_tip()
    
    for col in cols[8:]:
        p300.pick_up_tip()
        for row in rows:
            dest = row + str(col)
            p300.aspirate(50, lumisolve3)
            p300.touch_tip()
            p300.dispense(50, plate[dest].bottom(5))
            p300.move_to(plate[dest].bottom(1))
        p300.drop_tip()

    for col in cols[:4]:
        p300.pick_up_tip()
        for row in rows:
            dest = row + str(col)
            p300.aspirate(50, prob)
            p300.touch_tip()
            p300.dispense(50, plate[dest].bottom(3))
            p300.move_to(plate[dest].bottom(1))
        p300.drop_tip()

    for col in cols[4:8]:
        p300.pick_up_tip()
        for row in rows:
            dest = row + str(col)
            p300.aspirate(50, ecoli)
            p300.touch_tip()
            p300.dispense(50, plate[dest].bottom(5))
            p300.move_to(plate[dest].bottom(1))
        p300.drop_tip()
    
    for col in cols[8:]:
        p300.pick_up_tip()
        for row in rows:
            dest = row + str(col)
            p300.aspirate(50, atp)
            p300.touch_tip()
            p300.dispense(50, plate[dest].bottom(5))
            p300.move_to(plate[dest].bottom(1))
        p300.drop_tip()


    #dispense acid base x3 and water
    x = (len(contams) * 3) 
    for i, elem in enumerate(contams):
        contams2 = list(islice(cycle(contams), i + 1, i + 1 + x)) 
    count = 0 
    contamcount = 0
    for i in contams2:
        for col in cols[count:(count +1)]:
            volct = 1
            p20.pick_up_tip()
            for row in rows:
                dest = row + str(col)
                p20.aspirate(volct, contams2[contamcount])
                p20.touch_tip()
                p20.dispense(volct, plate[dest].bottom(5))
                p20.move_to(plate[dest].bottom(1)) 
                volct += 2.5
            p20.drop_tip()
            count += 1
            contamcount += 1
