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
    epp_rack = protocol.load_labware('opentrons_24_tuberack_eppendorf_2ml_safelock_snapcap', '5')
    tiprack300 = protocol.load_labware('opentrons_96_filtertiprack_200ul', '8')
    tiprack20 = protocol.load_labware('opentrons_96_filtertiprack_20ul', '9')
    tempdeck = protocol.load_module('tempdeck', '10') # leaving on so I don't have to move off 
    plate = protocol.load_labware('corning_96_wellplate_360ul_flat', '3')
    reagent_rack = protocol.load_labware(
        'opentrons_15_tuberack_nest_15ml_conical', '6')  # A1-C5, 15 ml tubes

    # PIPETTES
    p300 = protocol.load_instrument(
        'p300_single_gen2', 'left', tip_racks=[tiprack300]
    )
    p20 = protocol.load_instrument(
        'p20_single_gen2', 'right', tip_racks=[tiprack20]
    )
     
    # REAGENTS
    #reagent_rack
    ul7 = reagent_rack['A1'] #add 5 mL  
    x3 = reagent_rack['A2'] #add 5 mL  
    ul3021 = reagent_rack['A3'] #add 5 mL  
    lurb = reagent_rack['B1'] #add 6.5 mL
    sample = reagent_rack['C1'] #add 10.5 mL
    #epp_rack
    lurbnl = epp_rack['A2']  #add 1.8 mL
    trash = epp_rack['D6'] # trash; receives some of the blowouts 
    
    
    # lists
    detergent_vol = [42.9, 50, 66.7, 83.3] # from excel spreadsheet
    lurb_vol = [57.1, 50, 33.3, 16.7] # from excel spreadsheet, 6.5mL
    sample_vol = 100
    rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
    cols = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    detergent = [ul7, x3, ul3021]


    #### COMMANDS ######
    # Add lurb
    lurb_vol.reverse() #reverse lurb vol so that lower volumes are added first 
    count = 0.3333 #count so next vol is added to every 3rd row
    sample_count = 0
    lurb_h = fifteen_ml_heights(5000, 88, 45)
    for col in cols[::-1]: #reverse lurb vol so that lower volumes are added first 
        if lurb_vol[int(count)] <= 20: #if volume is under 20 uL, use p20
            p20.pick_up_tip()
            for row in rows[:7]:
                dest = row + str(col)
                p20.aspirate((lurb_vol[int(count)]), lurb.bottom(lurb_h[sample_count])) #int is used to round down to nearest integer, sample count 
                # p300.touch_tip()
                p20.dispense(lurb_vol[int(count)], plate[dest].bottom(3))
                p20.move_to(plate[dest].bottom())  
                sample_count += 1
            count += 0.3333 # count so next vol is added to every 3rd row
            p20.drop_tip()
        else:
             p300.pick_up_tip()
             for row in rows[:7]:
                dest = row + str(col)
                p300.aspirate((lurb_vol[int(count)]), lurb.bottom(lurb_h[sample_count])) #int is used to round down to nearest integer, sample count 
                # p300.touch_tip()
                p300.dispense(lurb_vol[int(count)], plate[dest].bottom(2))
                p300.move_to(plate[dest].bottom())
                sample_count += 1
             count += 0.3333 # count so next vol is added to every 3rd row
             p300.drop_tip()
   
   
    # create list with proper heights
    detergent_h = fifteen_ml_heights(2500, 96, 65)
    a = 24
    sub_detergent_h1 = detergent_h[:8] #splice list into first 8 vlaues for first 3 collumns 
    for i, elem in enumerate(sub_detergent_h1):
        detergent_h1 = list(islice(cycle(sub_detergent_h1), i + 1, i + 1 + a)) #replicates list 3 times to get the correct tip height for each of the 3 detergents 
  
    sub_detergent_h2 = detergent_h[8:16]
    for i, elem in enumerate(sub_detergent_h2):
        detergent_h2 = list(islice(cycle(sub_detergent_h2), i + 1, i + 1 + a)) 
   
    sub_detergent_h3 = detergent_h[16:24]
    for i, elem in enumerate(sub_detergent_h3):
        detergent_h3 = list(islice(cycle(sub_detergent_h3), i + 1, i + 1 + a)) 
   
    sub_detergent_h4 = detergent_h[24:32]
    for i, elem in enumerate(sub_detergent_h4):
        detergent_h4 = list(islice(cycle(sub_detergent_h4), i + 1, i + 1 + a)) 

    master_d_list = detergent_h1 + detergent_h2 + detergent_h3 + detergent_h4
    
    # add all detergents
    detergent_count = 0
    sample_count = 0
    count = 0.3333
    x = (len(detergent) * 4) + 1
    for i, elem in enumerate(detergent):
        detergent2 = list(islice(cycle(detergent), i + 1, i + 1 + x)) #replicates list to be able to cycle through detergents 
    for col in cols:
        p300.pick_up_tip()
        for row in rows:
            dest = row + str(col)
            p300.aspirate(detergent_vol[int(count)], detergent2[(detergent_count)].bottom(master_d_list[sample_count]))
            # p300.touch_tip()
            p300.dispense(detergent_vol[int(count)], plate[dest].bottom(2))
            p300.move_to(plate[dest].bottom())
            sample_count += 1
        count += 0.3333
        detergent_count += 1
        p300.drop_tip()

 
    lurb_vol.reverse() # reverse again becuase im going back to adding left to right 
    count = 0.3333
    p300.pick_up_tip()
    for row in rows[7:]:
        for col in cols[:9]:
            dest = row + str(col)
            p300.aspirate(lurb_vol[int(count)], lurbnl)
            p300.touch_tip()
            p300.dispense(lurb_vol[int(count)], plate[dest].bottom(2))
            p300.move_to(plate[dest].bottom())
            count += 0.33333
    p300.drop_tip()

    p20.pick_up_tip()
    for row in rows[7:]:
        for col in cols[9:]:
            dest = row + str(col)
            p20.aspirate(lurb_vol[int(count)], lurbnl)
            p20.touch_tip()
            p20.dispense(lurb_vol[int(count)], plate[dest].bottom(2))
            p20.move_to(plate[dest].bottom())
        count += 0.33333
    p20.drop_tip()

    # protocol.pause('All reagents added but ATP for background calculations. Resume to add ATP.')
    
    #add ATP/e.coli 
    sample_h = fifteen_ml_heights(10000, 96, 110)
    sample_count = 0
    p300.pick_up_tip()
    for col in cols:
        for row in rows:
            dest = row + str(col)
            p300.aspirate(sample_vol, sample.bottom(sample_h[sample_count]))
            # p300.touch_tip
            p300.dispense(sample_vol, plate[dest].bottom(4))
            p300.move_to(plate[dest].bottom())
            sample_count += 1
    p300.drop_tip()
    print (sample_h)
    print(sample_count)

