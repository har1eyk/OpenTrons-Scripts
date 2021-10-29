# imports
from opentrons import protocol_api

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
        offset = 11 #mm Need to add offset to ensure tip reaches below liquid level
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

# splits aspiration volume into equal parts 
def split_asp(tot, max_vol):
    n =1
    if tot/n > max_vol: # if total greater than max
       while tot/n > max_vol: # increment n until some tot/n < max_vol
            n+=1
            if tot/n == max_vol: # if tot evently divided e.g. 1000
                subvol = tot/n
                return [subvol]*n
            if tot/(n+1) < max_vol: # if tot <> evenly divided e.g. 417.3
                subvol = tot/(n+1)
                return [subvol]*(n+1) # return # aspiration steps
    else: # if total less than max
        return [tot/n]

def run(protocol: protocol_api.ProtocolContext):

    # LABWARE
    epp_rack = protocol.load_labware('opentrons_24_tuberack_eppendorf_2ml_safelock_snapcap', '1')
    tiprack300 = protocol.load_labware('opentrons_96_filtertiprack_200ul', '8')
    tiprack20 = protocol.load_labware('opentrons_96_filtertiprack_20ul', '9')
    tempdeck = protocol.load_module('tempdeck', '10') # leaving on so I don't have to move off 
    plate = protocol.load_labware('corning_96_wellplate_360ul_flat', '3')
    reagent_rack = protocol.load_labware('opentrons_6_tuberack_nest_50ml_conical', '2')

    # PIPETTES
    p300 = protocol.load_instrument(
        'p300_single_gen2', 'left', tip_racks=[tiprack300]
    )
    p20 = protocol.load_instrument(
        'p20_single_gen2', 'right', tip_racks=[tiprack20]
    )
     
    # REAGENTS
    #reagent_rack
    water = reagent_rack['A1'] # water or sample; 9338.89ul
    detergent = reagent_rack['A2'] # detergent e.g. Ultralyse 7, Ultralyse X3; 8085.11ul
    luminaseBuffer = reagent_rack['B1'] #Raquel's V2 mix form 22 April 2021; 17424.5ul
    #epp_rack
    dATP = epp_rack['A1'] # ATP Should be at 0.1mM or 100uM; 1584ul
    dLuciferin = epp_rack['B1'] # Luciferin, 10mM stock? 1584ul   
    trash = epp_rack['C1'] # trash; receives some of the blowouts 
    
    
    # lists
    sample_vols = [164.18,156.75,154.69,144.38,123.75,82.50,82.50,55.00,47.14,27.50,15.00,7.86]
    detergents_vols = [0.82, 8.25, 10.31, 20.63, 41.25, 82.50, 82.50, 110.00, 117.86, 137.50, 150.00, 157.14]
    dATP_vol = 15
    luminaseBuffer_vol = 165
    dLuciferin_vol = 15
    rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']

    ##### COMMANDS ######
# Add sample (water)
    p300.pick_up_tip()
    sample_h = fifty_ml_heights(9338.89, 96, 82.50) # volumes are different, so take median
    sample_counter = 0
    for j in range(10): # cols 1..10 can be serviced by p200.
        sample_vol = sample_vols[j]
        for row in rows: # process 8 rows 
            dest = row+str(j+1)
            p300.aspirate(sample_vol, water.bottom(sample_h[sample_counter]))
            p300.dispense(sample_vol, plate[dest].bottom(5))
            p300.blow_out(plate[dest].bottom(7)) 
            p300.touch_tip()
            sample_counter += 1
    p300.drop_tip()
    # last two columns need p20
    p20.pick_up_tip()
    sample_counter = 80 # 8*10+1; offset previous dispenses
    for j in range(10,12): # cols 1..10 can be serviced by p200.
        sample_vol = sample_vols[j]
        for row in rows: # process 8 rows 
            dest = row+str(j+1)
            p20.aspirate(sample_vol, water.bottom(sample_h[sample_counter]))
            p20.dispense(sample_vol, plate[dest].bottom(5))
            p20.blow_out(plate[dest].bottom(7)) 
            p20.touch_tip()
            sample_counter += 1
    p20.drop_tip()

# Add luciferin
    p300.pick_up_tip()
    luciferin_h=tip_heightsEpp(1584, 8, 180) # decrement by rows for multiasp and disp
    luciferin_counter = 0
    luciferin_bolus = 5
    for row in rows: # process 8 rows
        p300.aspirate(dLuciferin_vol*12+luciferin_bolus, dLuciferin.bottom(luciferin_h[luciferin_counter])) #5ul bolus
        for j in range(12): # all cols
            dest = row+str(j+1)
            p300.dispense(dLuciferin_vol, plate[dest].bottom(2))
        luciferin_counter += 1
        p300.dispense(luciferin_bolus, trash.top(-4)) # remove bolus
        p300.blow_out(trash.top(-4))
        p300.touch_tip(trash, v_offset=-4)
    p300.drop_tip()
    
# Add detergent
    # first three columns need p20
    p20.pick_up_tip()
    deterg_h = fifty_ml_heights(8085.11, 96, 82.50) # volumes are different, so take median
    deterg_counter = 0
    for j in range(0,3): # cols 1..3 can be serviced by p200.
        deterg_vol = detergents_vols[j]
        for row in rows: # process 8 rows 
            dest = row+str(j+1)
            p20.aspirate(deterg_vol, detergent.bottom(deterg_h[deterg_counter]))
            p20.dispense(deterg_vol, plate[dest].bottom(5))
            p20.blow_out(plate[dest].bottom(7)) 
            p20.touch_tip()
            deterg_counter += 1
    p20.drop_tip()
    # Last 9 cols need p300
    p300.pick_up_tip()
    deterg_counter = 8*3 # offset previous dispenses
    for j in range(3,12): # cols 1..10 can be serviced by p200.
        deterg_vol = detergents_vols[j]
        for row in rows: # process 8 rows 
            dest = row+str(j+1)
            p300.aspirate(deterg_vol, detergent.bottom(deterg_h[deterg_counter]))
            p300.dispense(deterg_vol, plate[dest].bottom(5))
            p300.blow_out(plate[dest].bottom(7)) 
            p300.touch_tip()
            deterg_counter += 1
    p300.drop_tip()
    
# Add luciferase buffer
    p300.pick_up_tip()
    buffer_h=fifty_ml_heights(17424.5, 96, 165) # decrement by rows for multiasp and disp
    buffer_counter = 0
    for row in rows: # process 8 rows
        for j in range(12): # all cols
            dest = row+str(j+1)
            p300.aspirate(luminaseBuffer_vol, luminaseBuffer.bottom(buffer_h[buffer_counter]))
            p300.dispense(luminaseBuffer_vol, plate[dest].bottom(4))
            buffer_counter += 1
    p300.drop_tip()

# Add ATP to initiate reaction
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