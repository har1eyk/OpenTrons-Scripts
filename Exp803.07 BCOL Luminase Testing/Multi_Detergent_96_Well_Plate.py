# imports
from typing import Counter
from opentrons import protocol_api
from itertools import cycle, islice, repeat
from opentrons.commands.types import MoveToCommand

from opentrons.protocols.geometry.module_geometry import models_compatible
# metadata
metadata = {
    'protocolName': 'Create 96w Plate with Luminase Reagents',
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
    tiprack20 = protocol.load_labware('opentrons_96_filtertiprack_20ul', '9')
    tempdeck = protocol.load_module('tempdeck', '10') # leaving on so I don't have to move off 
    plate = protocol.load_labware('corning_96_wellplate_360ul_flat', '3')
    reagent_rack = protocol.load_labware('opentrons_6_tuberack_nest_50ml_conical', '6')

    # PIPETTES
    p300 = protocol.load_instrument(
        'p300_single_gen2', 'left', tip_racks=[tiprack300]
    )
    p20 = protocol.load_instrument(
        'p20_single_gen2', 'right', tip_racks=[tiprack20]
    )
     
    # REAGENTS
    #reagent_rack
    ul7 = reagent_rack['A1']
    x3 = reagent_rack['A2']
    ul3021 = reagent_rack['A3'] 
    lurb = reagent_rack['B1'] #Raquel's V2 mix form 22 April 2021; 7mL
    #epp_rack
    dATP = epp_rack['A1'] # ATP Should be at 0.1mM or 100uM; 1584ul
    lurbnl = epp_rack['A2']  #
    trash = epp_rack['D6'] # trash; receives some of the blowouts 
    
    
    # lists
    detergent_vol = [79.3, 92.5, 123.33, 154.2] # from excel spreadsheet
    lurb_vol = [105.7, 92.5, 61.7, 30.8] # from excel spreadsheet, 6.5mL
    dATP_vol = 15
    rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
    cols = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    detergent = [ul7, x3, ul3021]


    #### COMMANDS ######
    # Add lurb
    count = 0.3333
    sample_count = 0
    lurb_h = fifty_ml_heights(6500, 88, 80)
    for col in cols:
        p300.pick_up_tip()
        for row in rows[:7]:
            dest = row + str(col)
            p300.aspirate(lurb_vol[int(count)], lurb.bottom(lurb_h[sample_count]))
            p300.touch_tip()
            p300.dispense(lurb_vol[int(count)], plate[dest].bottom(3))
            p300.move_to(plate[dest].bottom())
            sample_count += 1
        p300.drop_tip()
        count += 0.3333

    # add UL7
    detergent_count = 0
    count = 0.3333
    x = (len(detergent) * 4) + 1
    for i, elem in enumerate(detergent):
        detergent2 = list(islice(cycle(detergent), i + 1, i + 1 + x)) 
    for col in cols:
        p300.pick_up_tip()
        for row in rows:
            dest = row + str(col)
            p300.aspirate(detergent_vol[int(count)], detergent2[(detergent_count)].bottom(2))
            p300.touch_tip()
            p300.dispense(detergent_vol[int(count)], plate[dest].bottom(3))
            p300.move_to(plate[dest].bottom())
        count += 0.3333
        detergent_count += 1
        p300.drop_tip()
     
    # add LURB without luciferase to last row
    count = 0.3333
    for col in cols:
        p300.pick_up_tip()
        for row in rows[7:]:
            dest = row + str(col)
            p300.aspirate(lurb_vol[int(count)], lurbnl)
            p300.touch_tip()
            p300.dispense(lurb_vol[int(count)], plate[dest].bottom())
        p300.drop_tip()
        count += 0.33333
    

    protocol.pause('All reagents added but ATP for background calculations. Resume to add ATP.')
    
    #add ATP/e.coli 
    p300.pick_up_tip()
    dATP_h=tip_heightsEpp(1584, 8, 180) # decrement by rows for multiasp and disp
    dATP_counter = 0
    dATP_bolus = 5
    for row in rows: # process 8 rows
        p300.aspirate(dATP_vol*12+dATP_bolus, dATP.bottom(dATP_h[dATP_counter])) #5ul bolus
        for j in range(12): # all cols
            dest = row+str(j+1)
            p300.dispense(dATP_vol, plate[dest].bottom(2))
        dATP_counter += 1
        p300.dispense(dATP_bolus, trash.top(-4)) # remove bolus
        p300.blow_out(trash.top(-4))
        p300.touch_tip(trash, v_offset=-4)
    p300.drop_tip()

