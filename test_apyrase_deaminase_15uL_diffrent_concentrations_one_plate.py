from opentrons import protocol_api

# metadata
metadata = {
    'protocolName': 'Create 96w Plate with Luminase Reagents 200ul ATP Std Curve and 2 MMixes',
    'author': 'Harley King <harley.king@luminultra.com>',
    'description': 'Create a 96w plate using serial dilution of ATP using 2 master mixes.',
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
    fuge_rack = protocol.load_labware('opentrons_24_tuberack_eppendorf_2ml_safelock_snapcap', '2')
    #fuge_rack = protocol.load_labware('opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap', '2')
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
    #fuge_rack
    adil_1 = fuge_rack ['A1']
    adil_2 = fuge_rack ['A2']
    adil_3 = fuge_rack ['A3']
    adil_4 = fuge_rack ['A4']
    ddil_1 = fuge_rack ['B1']
    ddil_2 = fuge_rack ['B2']
    ddil_3 = fuge_rack ['B3']
    ddil_4 = fuge_rack ['B4']
    trash = fuge_rack ['D6']
    lurb_nl = fuge_rack ['C1']
    water = reagent_rack ['B1']
    lurb = reagent_rack ['A1']
   
    #lists
    treat_vol = 15
    buf_vol = 185
    trxn_vol = 200
    rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
    bcol = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    ucol = [1, 2, 3, 4, 5]
    tcol = [6, 7, 8, 9, 10]
    bwlcol = [11]
    wcol = [12]
    apyr_treat = [adil_1, adil_2, adil_3, adil_4]
    deam_treat = [ddil_1, ddil_2, ddil_3, ddil_4,]

    ####COMMANDS###
    # adds buffer to most wells 
    sample_h = fifty_ml_heights(18000, 80, 185) # volumes are different, so take median
    sample_counter = 0
    for col in bcol: 
        p300.pick_up_tip()
        for row in rows:  
            dest = row+str(col)
            p300.aspirate(buf_vol, lurb.bottom(sample_h[sample_counter]))
            p300.dispense(buf_vol, plate[dest].bottom(5))
            p300.blow_out(plate[dest].bottom(5)) 
            p300.move_to(plate[dest].bottom())
            sample_counter += 1
        p300.drop_tip()
    
    # adds water to untreated wells
    sample_counter = 0
    sample_h = fifty_ml_heights(5000, 40, 15) # volumes are different, so take median
    for row in rows:    
        p300.pick_up_tip()
        p300.aspirate(80, water)
        for col in ucol: 
            dest = row+str(col)
            p300.dispense(treat_vol, plate[dest].bottom(5))
            p300.move_to(plate[dest].bottom())
        p300.drop_tip()
        sample_counter += 1

    # adds deaminase to wells 
    sample_counter = 0
    for row in rows[::2]:    
        p300.pick_up_tip()
        p300.aspirate(90, deam_treat[sample_counter])
        for col in tcol: 
            dest = row+str(col)
            p300.dispense(treat_vol, plate[dest].bottom(5))
            p300.move_to(plate[dest].bottom())
        p300.dispense(15, trash)
        p300.drop_tip()
        sample_counter += 1
        if sample_counter == 4:
            break

    #adds apyrase to wells
    sample_counter = 0
    for row in rows[1::2]:    
        p300.pick_up_tip()
        p300.aspirate(90, apyr_treat[sample_counter])
        for col in tcol: 
            dest = row+str(col)
            p300.dispense(treat_vol, plate[dest].bottom(5))
            p300.move_to(plate[dest].bottom())
        p300.dispense(15, trash)
        p300.drop_tip()
        sample_counter += 1
        if sample_counter == 4:
            break

    #adds luminase buffer without luciferase
    p300.pick_up_tip()
    sample_counter = 0
    for col in bwlcol: 
        for row in rows:  
            dest = row+str(col)
            p300.aspirate(buf_vol, lurb_nl)
            p300.dispense(buf_vol, plate[dest].bottom(5))
            p300.blow_out(plate[dest].bottom(5)) 
            p300.move_to(plate[dest].bottom())
            sample_counter += 1
    p300.drop_tip()

    # adds  water to buffer without luciferase wells
    p300.pick_up_tip()
    sample_counter = 0
    sample_h = fifty_ml_heights(4400, 8, 15) # volumes are different, so take median
    for col in bwlcol: 
        p300.aspirate(135, water)
        for row in rows:    
            dest = row+str(col)
            p300.dispense(treat_vol, plate[dest].bottom(5))
            p300.move_to(plate[dest].bottom())
        p300.dispense(15, trash)
        sample_counter += 1
    p300.drop_tip()
  
    #add water to final column 
    p300.pick_up_tip()
    sample_h = fifty_ml_heights(4280, 8, 185) # volumes are different, so take median
    sample_counter = 0
    for col in wcol: 
        for row in rows:  
            dest = row+str(col)
            p300.aspirate(trxn_vol, water.bottom(sample_h[sample_counter]))
            p300.dispense(trxn_vol, plate[dest].bottom(5))
            p300.blow_out(plate[dest].bottom(5)) 
            p300.move_to(plate[dest].bottom())
            sample_counter += 1
    p300.drop_tip()


