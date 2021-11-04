# imports
from opentrons import protocol_api
from opentrons.commands.commands import blow_out

# metadata
metadata = {
    'protocolName': 'Prep 48 5mL Tubes with Mag Beads.',
    'author': 'Harley King <harley.king@luminultra.com>',
    'description': 'Prep 48 5mL Tubes with Mag Beads',
    'apiLevel': '2.11'
}

# Calc heights for 1.5mL Tube
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
    if init_vol > 1499:
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

##########################       
def run(protocol: protocol_api.ProtocolContext):

    # LABWARE
    mag_rack = protocol.load_labware('vwr_24_tuberack_1500ul', '6')
    tiprack300 = protocol.load_labware('opentrons_96_filtertiprack_200ul', '8')
    tempdeck = protocol.load_module('tempdeck', '10') # don't want to have to move it off the platform
    rack_plate1 = protocol.load_labware('eppendorf5ml_15_tuberack_5000ul', '1')
    rack_plate2 = protocol.load_labware('eppendorf5ml_15_tuberack_5000ul', '2')
    rack_plate3 = protocol.load_labware('eppendorf5ml_15_tuberack_5000ul', '4')
    rack_plate4 = protocol.load_labware('eppendorf5ml_15_tuberack_5000ul', '5')
    reagent_rack = protocol.load_labware('opentrons_6_tuberack_nest_50ml_conical', '3')

    # PIPETTES
    p300 = protocol.load_instrument(
        'p300_single_gen2', 'left', tip_racks=[tiprack300]
    )
    # REAGENTS   
    # the magnetic beads are undiluted in 1.5mL snap-cap tube
    mag_beads = mag_rack['A1'] # 48 *20 = 960*1.1 = 1056 | undiluted beads
    # This is on 6-well, 50mL rack
    lysis_buffer1 = reagent_rack['A1'] #50mL 2.5mL*15 =37.5*1.1 = 41.25mL
    lysis_buffer2 = reagent_rack['A2'] #50mL 2.5mL*15 =37.5*1.1 = 41.25mL
    lysis_buffer3 = reagent_rack['A3'] #30mL 2.5mL*15 =37.5*1.1 = 41.25mL
    lysis_buffer4 = reagent_rack['B1'] #30mL 2.5mL*3 =7.5*1.1 = 8.25mL

    # CALCS
    lysis_buffer_per_well = 2500 #ul
    mag_beads_per_well = 20 #ul
    
    # LISTS
    tot_racks = [rack_plate1, rack_plate2, rack_plate3]
    tot_buffers = [lysis_buffer1, lysis_buffer2, lysis_buffer3]
    last_rack = [rack_plate4]
    last_buffer = [lysis_buffer4] 
    rows_on_plate = ['A', 'B', 'C'] # 5x3

        
    #### COMMANDS ###### 
    # Buffer to 3 racks, 45 tubes
    for rack, buffer in zip(tot_racks, tot_buffers):
        p300.pick_up_tip()   
        buffer_h = fifty_ml_heights(41250, 195, 200)  #filling a 2.5mL with 0.2ml pipette = 12.5 *15 tubes = 187.5|13*15=195
        buffer_counter = 0
        for row in rows_on_plate:
            for col in range(5): #begins at 0
                dest = rack[row+str(col+1)] # 
                for i in range(13): #12 times per tube 2500ul/200ul = 12.5ul per tube
                    p300.aspirate(200, buffer.bottom(buffer_h[buffer_counter]))
                    p300.dispense(200, dest.top())
                    p300.blow_out(dest.top()) # for this much vol, blowout enough
                    # p300.touch_tip()
                    # p300.move_to(dest.top())
                    buffer_counter +=1
                p300.aspirate(100, buffer.bottom(buffer_h[buffer_counter-1])) # list end if I don't subtract 1
                p300.dispense(100, dest.top())
                p300.blow_out(dest.top())
                # p300.touch_tip()
        p300.drop_tip()  
    
    # Buffer to last rack, 3 tubes
    for rack, buffer in zip(last_rack, last_buffer):
        p300.pick_up_tip()   
        buffer_h = fifty_ml_heights(8250, 39, 200) #filling a 2.5mL with 0.2ml pipette = 12.5 *3 tubes = 187.5|13*3=39
        buffer_counter = 0
        for col in range(3): #3 tubes in single row
            dest = rack['A'+str(col+1)] # 
            for i in range(13): #12 times per tube 2500ul/200ul = 12.5ul per tube
                p300.aspirate(200, buffer.bottom(buffer_h[buffer_counter]))
                p300.dispense(200, dest.top())
                p300.blow_out(dest.top())
                # p300.touch_tip()
                buffer_counter +=1
            p300.aspirate(100, buffer.bottom(buffer_h[buffer_counter-1]))
            p300.dispense(100, dest.top())
            p300.blow_out(dest.top())
            # p300.touch_tip()
        p300.drop_tip() 

    
    # magnetic beads transfer, the beads should not be diluted!
    # future work: consider aliquoting 5x and pipetting across tubes in row rather than singly
    p300.pick_up_tip()  
    mag_h = tip_heights(1056, 48, 20) 
    counter = 0
    p300.mix(3, 200, mag_beads.bottom(12))
    p300.mix(2, 200, mag_beads.bottom(4))
    p300.mix(2, 200, mag_beads.bottom(8))
    p300.mix(3, 200, mag_beads.bottom(12))
    p300.mix(5, 200, mag_beads.bottom(16))
    p300.mix(5, 200, mag_beads.bottom(21)) #need several mixing steps to homogenize beads
    for rack in tot_racks:
        for row in rows_on_plate:
            for col in range(5) :
                p300.mix(2, 200, mag_beads.bottom(mag_h[counter]))
                dest = rack[row+str(col+1)]
                p300.aspirate(mag_beads_per_well, mag_beads.bottom(mag_h[counter]), rate=0.75)
                p300.touch_tip()
                p300.dispense(mag_beads_per_well, dest.bottom(28)) #want beads to come in contact with the fluid, 2.5mL in 5mL tube
                p300.blow_out(dest.top())
                p300.touch_tip()
                p300.move_to(dest.top())
                counter +=1
    for rack in last_rack:
        for col in range(3):
            p300.mix(2, 200, mag_beads.bottom(mag_h[counter]))
            dest = rack['A'+str(col+1)]
            p300.aspirate(mag_beads_per_well, mag_beads.bottom(mag_h[counter]), rate=0.75)
            p300.touch_tip()
            p300.dispense(mag_beads_per_well, dest.bottom(28))
            p300.blow_out(dest.top())
            p300.touch_tip()
            p300.move_to(dest.top())
            counter +=1
    p300.drop_tip()    
