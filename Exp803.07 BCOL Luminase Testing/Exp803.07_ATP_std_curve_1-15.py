# imports
from opentrons import protocol_api

# metadata
metadata = {
    'protocolName': 'Create 96w Plate with Luminase Reagents 200ul ATP Std Curve',
    'author': 'Harley King <harley.king@luminultra.com>',
    'description': 'Create a 96w plate using serial dilution of ATP.',
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

def run(protocol: protocol_api.ProtocolContext):

    # LABWARE
    fuge_rack = protocol.load_labware('opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap', '2')
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
    luminaseBuffer = reagent_rack['B1'] #Raquel's V2 mix form 22 April 2021; 19536ul
    
    std_1 = fuge_rack['A1'] # 900ul Water
    std_2 = fuge_rack['A2'] # 900ul water
    std_3 = fuge_rack['A3'] # 900ul water
    std_4 = fuge_rack['A4'] # 900ul water
    std_5 = fuge_rack['A5'] # 900ul water
    std_6 = fuge_rack['A6'] # 900ul water 
    std_7 = fuge_rack['B1'] # 900ul water
    std_8 = fuge_rack['B2'] # 900ul water
    std_9 = fuge_rack['B3'] # 900ul water
    std_10 = fuge_rack['B4'] # 900ul water
    std_11 = fuge_rack['B5'] # 900ul water
    std_12 = fuge_rack['B6'] # 900ul water
    std_13 = fuge_rack['C1'] # 900ul water
    std_14 = fuge_rack['C2'] # 900ul water
    std_15 = fuge_rack['C3'] # 900ul water
    water = fuge_rack['D6']
    trash = fuge_rack['C6'] # trash; receives some of the blowouts 
    
    # lists
    dATP_vol = 15
    luminaseBuffer_vol = 185
    rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
    std_wells = [std_1, std_2, std_3, std_4, std_5, std_6, std_7, std_8, std_9, std_10, std_11, std_12, std_13, std_14, std_15, water]

    #### COMMANDS ######
# Add luminase buffer containing D-luciferin, reagent and water
    p300.pick_up_tip()
    sample_h = fifty_ml_heights(19536, 96, 185) # volumes are different, so take median
    sample_counter = 0
    for j in range(12): # cols 1..10 can be serviced by p200.
        for row in rows: # process 8 rows 
            dest = row+str(j+1)
            p300.aspirate(luminaseBuffer_vol, luminaseBuffer.bottom(sample_h[sample_counter]))
            p300.dispense(luminaseBuffer_vol, plate[dest].bottom(5))
            p300.blow_out(plate[dest].bottom(5)) 
            p300.move_to(plate[dest].bottom())
    p300.drop_tip()

    protocol.pause('All reagents added but ATP for background calculations. Resume to add ATP.')
# add ATP serial dilutions
    p300.pick_up_tip()
    dATP_bolus = 5
    for j, (tube, row) in enumerate(zip(reversed(std_wells), reversed(2*rows))): #forgive me; loop in reverse; keep tip for speed so low conc to high conc
        p300.aspirate(dATP_vol*6+dATP_bolus, tube.bottom(20)) #5ul bolus
        for i in range(6): # process 6 rows
            dest = row+str(i+7) if j < 8 else row+str(i+1) # going backwards, need to move to 1st half
            p300.dispense(dATP_vol, plate[dest].bottom(2))
        p300.dispense(dATP_bolus, trash.top(-4)) # remove bolus
        p300.blow_out(trash.top(-4))
        p300.touch_tip(trash, v_offset=-4)
    p300.drop_tip()
