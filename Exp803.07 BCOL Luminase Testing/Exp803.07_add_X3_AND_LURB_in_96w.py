# imports
from opentrons import protocol_api

# metadata
metadata = {
    'protocolName': 'Create 96w Plate with 50ul X3 and 100ul LURB from 15mL Tubes',
    'author': 'Harley King <harley.king@luminultra.com>',
    'description': 'Create a 96w plate with X3 and LURB.',
    'apiLevel': '2.12'
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
        offset = 10  # model out of range; see sheet
    else:
        offset = 5  # mm Need to add offset to ensure tip reaches below liquid level
    for i in range(steps):
        x = init_vol-vol_dec*i
        vols.append(x)
        h = m*x+b
        h = h-offset
        if h < 12:  # If less than 5mL remain in 50mL tube, go to bottom for asp
            h = 2
            heights.append(h)
        else:
            heights.append(round(h, 1))
    return heights
# calculates ideal tip height for entering liquid in 15mL tube
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
    # epp_rack = protocol.load_labware('opentrons_24_tuberack_eppendorf_2ml_safelock_snapcap', '5')
    tiprack300 = protocol.load_labware('opentrons_96_filtertiprack_200ul', '8')
    # tiprack20 = protocol.load_labware('opentrons_96_filtertiprack_20ul', '9')
    # tempdeck = protocol.load_module('tempdeck', '10') # leaving on so I don't have to move off 
    plate = protocol.load_labware('corning_96_wellplate_360ul_flat', '3')
    # reagent_rack = protocol.load_labware('opentrons_6_tuberack_nest_50ml_conical', '6')
    # lurb_rack= protocol.load_labware('opentrons_15_tuberack_nest_15ml_conical', '2')
    x3_rack= protocol.load_labware('opentrons_15_tuberack_nest_15ml_conical', '6')
    lurb_rack= protocol.load_labware('eppendorf5ml_15_tuberack_5000ul', '2')

    # PIPETTES
    p300 = protocol.load_instrument(
        'p300_single_gen2', 'left', tip_racks=[tiprack300]
    )
     
    # REAGENTS
    x3 = x3_rack['A1'] # detergent e.g. Ultralyse 7, Ultralyse X3; 8085.11ul
    lurbOne = lurb_rack['A1'] # lurb 1; 15mL tube
    lurbTwo = lurb_rack['A2'] # lurb 1; 15mL tube
    lurbThree = lurb_rack['A3'] # lurb 1; 15mL tube
    lurbFour = lurb_rack['A4'] # lurb 1; 15mL tube
    lurbFive = lurb_rack['A5'] # lurb 1; 15mL tube
    lurbSix = lurb_rack['B1'] # lurb 1; 15mL tube
    lurbSeven = lurb_rack['B2'] # lurb 1; 15mL tube
    lurbEight = lurb_rack['B3'] # lurb 1; 15mL tube
    lurbNine = lurb_rack['B4'] # lurb 1; 15mL tube
    lurbTen = lurb_rack['B5'] # lurb 1; 15mL tube
    lurbEleven = lurb_rack['C1'] # lurb 1; 15mL tube
    lurbTwelve = lurb_rack['C2'] # lurb 1; 15mL tube
        
    # lists
    rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
    lurb_list = [lurbOne, lurbTwo, lurbThree, lurbFour, lurbFive, lurbSix, lurbSeven, lurbEight, lurbNine, lurbTen, lurbEleven, lurbTwelve]
    lurb_vol = 100
    x3_vol = 50
    lurb_source_vol = 12000

    ### COMMANDS ######   
    # Add detergent
    p300.pick_up_tip()
    x3_h_list = fifteen_ml_heights(5000, 48, 100) # 15mL tube
    print (x3_h_list)
    x3_counter =0
    x3_h = x3_h_list[x3_counter]
    p300.aspirate(30, x3.bottom(x3_h)) #aspirate a bolus for reproducibility
    for r in range(1,13): # all cols in plate
        for k in range(0,8): # all rows in list
            if k==0 or k==2 or k==4 or k==6:
                # p300.blow_out(x3.bottom(x3_h+10))
                p300.aspirate(x3_vol*2, x3.bottom(x3_h)) #slower, but if vol *4 then detergent creates bubbles.
                p300.move_to(x3.bottom(x3_h+10)) # move above liquid level and wait for droplet coalescence
                protocol.delay(seconds=2)
                p300.move_to(x3.bottom(x3_h)) # touch tip to fluid to clear droplets
                print ("Height is:", x3_h)
                x3_counter += 1
                x3_h = x3_h_list[x3_counter-1]
            dest = rows[k]+str(r)
            p300.dispense(x3_vol, plate[dest])
            p300.move_to(plate[dest].bottom(10)) # bring tip above fluid 
            # if k==1 or k==3 or k==5 or k==7: # last dispenses
            #     # p300.blow_out(plate[dest].bottom(10)) #blow creates bubbles and this creates inconsistencies
            #     p300.move_to(plate[dest].bottom(1))
            p300.move_to(plate[dest].bottom(1)) # bring tip to fluid to remove droplets
    p300.drop_tip()
    
    # # Add luciferase buffer
    # p300.pick_up_tip()
    # # lurb_h_list = fifteen_ml_heights(lurb_source_vol, 4, 200) # 15mL tube
    # for r in range(1,13): # all cols in plate
    #     # lurb_counter =0 # reset counter for each column
    #     # lurb_h = lurb_h_list[lurb_counter] # lurb height for tip
    #     lurb = lurb_list[r-1] # which lurb tube in list
    #     for k in range(0,8): # all rows in list
    #         if k==0 or k==2 or k==4 or k==6: #aspirate every other row
    #             p300.aspirate(lurb_vol*2, lurb.bottom(2))
    #             p300.move_to(lurb.bottom(2)) # move above liquid level and wait for droplet coalescence
    #             p300.move_to(lurb.bottom(2)) # touch tip to fluid to clear droplets
    #             # lurb_counter += 1
    #         dest = rows[k]+str(r)
    #         p300.dispense(lurb_vol, plate[dest])
    #         p300.move_to(plate[dest].bottom(10)) # bring tip above fluid 
    #         if k==1 or k==3 or k==5 or k==7: # last dispenses in row
    #             p300.blow_out(plate[dest].bottom(10))
    #             # p300.move_to(x3.bottom(x3_h))
    #         p300.move_to(plate[dest].bottom(3)) # bring tip above fluid 
    # p300.drop_tip()
