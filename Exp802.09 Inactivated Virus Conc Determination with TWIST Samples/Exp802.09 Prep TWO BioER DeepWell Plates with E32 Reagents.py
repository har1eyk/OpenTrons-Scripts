# imports
from opentrons import protocol_api
from opentrons.commands.commands import blow_out

# metadata
metadata = {
    'protocolName': 'Prep BioER Deepwell Plate for E32 Extraction.',
    'author': 'Harley King <harley.king@luminultra.com>',
    'description': 'Making a BioER plate with beads, lysis buffer, wash1-3 and NFW.',
    'apiLevel': '2.11'
}
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
    mag_rack = protocol.load_labware('opentrons_24_tuberack_eppendorf_2ml_safelock_snapcap', '7')
    tiprack300 = protocol.load_labware('opentrons_96_filtertiprack_200ul', '8')
    tempdeck = protocol.load_module('tempdeck', '10')
    deep_plate1 = protocol.load_labware('bioer_96_wellplate_2200ul', '1')
    deep_plate2 = protocol.load_labware('bioer_96_wellplate_2200ul', '4')
    reagent_rack = protocol.load_labware('opentrons_6_tuberack_nest_50ml_conical', '2')

    # PIPETTES
    p300 = protocol.load_instrument(
        'p300_single_gen2', 'left', tip_racks=[tiprack300]
    )
    # REAGENTS   
    # the magnetic beads are undiluted in 2mL Epp snap-cap tube
    mag_beads = mag_rack['A1']#50mL | 40 *32 = 1280*1.2 = 1536 | undiluted beads
    # These are on 6-well, 50mL rack
    lysis_buffer = reagent_rack['A1'] #50mL 400 * 32 =12800*1.2 = 15360
    nfw = reagent_rack['A3'] #50mL | 100*32 = 3200*1.2 = 3840 + dilution for beads = 360*32 =11520*1.2=13824 = 17664
    wash_sol_one = reagent_rack['B1'] #50mL | 1000 *32 = 32000*1.2 = 38400
    wash_sol_two = reagent_rack['B2'] #50mL | 1000 *32 = 32000*1.2 = 38400
    wash_sol_three_etoh = reagent_rack['B3'] #50mL | 1000 *32 = 32000*1.2 = 38400


    # CALCS
    lysis_buffer_per_well = 400
    mag_beads_per_well = 40
    water_for_mag_bead_dil_per_well = 360
    wash_one_sol_per_well = 1000
    wash_two_sol_per_well = 1000
    wash_three_etoh_per_well = 1000
    elution_buffer_per_well = 100
    # COLUMNS
    mag_bead_columns = ['6','12']
    lysis_buffer_columns = ['1', '7']
    elution_columns = ['5', '11']
    wash_one_sol_columns = ['2', '8']
    wash_two_sol_columns = ['3', '9']
    wash_three_etoh_columns = ['4', '10']

   
    # LISTS
    tot_sample_plates = [deep_plate1, deep_plate2]
    rows_on_plate = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
        
    ##### COMMANDS ###### 
    # magnetic beads transfer
    # the beads should not be diluted!
    p300.pick_up_tip()  
    mag_h = tip_heightsEpp(1536, 32, 40) #32*40  = 1280*1.2 = 1536
    counter = 0
    for plate in tot_sample_plates:
        p300.mix(2, 200, mag_beads.bottom(4))
        p300.mix(2, 200, mag_beads.bottom(8))
        p300.mix(3, 200, mag_beads.bottom(12))
        p300.mix(3, 200, mag_beads.bottom(16))
        p300.mix(4, 200, mag_beads.bottom(20)) #challenging to homogenize beads; needs several mixing steps
        for col in mag_bead_columns:
            for row in rows_on_plate:
                p300.mix(1, 200, mag_beads.bottom(4))
                p300.mix(1, 200, mag_beads.bottom(mag_h[counter]))
                dest = row+str(col)
                p300.aspirate(mag_beads_per_well, mag_beads.bottom(mag_h[counter]), rate=0.5)
                p300.touch_tip()
                p300.dispense(mag_beads_per_well, plate[dest].bottom(5))
                p300.blow_out(plate[dest].bottom(5))
                p300.touch_tip(plate[dest].bottom(5))
                counter +=1
    p300.drop_tip()    
    # dilute the mag beads 1:10 with water
    water_h = fifty_ml_heights(17664, 34*2, 180) #32*360 = 11520
    water_counter = 0
    p300.pick_up_tip()  
    for plate in tot_sample_plates:
        for col in mag_bead_columns:
            for row in rows_on_plate:
                dest = row+str(col)
                p300.aspirate(water_for_mag_bead_dil_per_well/2, nfw.bottom(water_h[water_counter]))
                p300.dispense(water_for_mag_bead_dil_per_well/2, plate[dest].bottom(25))
                p300.aspirate(water_for_mag_bead_dil_per_well/2, nfw.bottom(water_h[water_counter]))
                p300.dispense(water_for_mag_bead_dil_per_well/2, plate[dest].bottom(25))
                p300.blow_out(plate[dest].bottom(25))
                p300.touch_tip()
                water_counter +=1
    p300.drop_tip() 

    # wash buffer 1 
    wash_one_h = fifty_ml_heights(38400, 32*5, 200) #32*1000 = 32000
    wash_one_counter = 0
    p300.pick_up_tip()   
    for plate in tot_sample_plates:
        for col in wash_one_sol_columns:
            for row in rows_on_plate:
                dest = row+str(col)
                for i in range(5):
                    p300.aspirate(wash_one_sol_per_well/5, wash_sol_one.bottom(wash_one_h[wash_one_counter]))
                    p300.dispense(wash_one_sol_per_well/5, plate[dest].bottom(25))
                    p300.blow_out(plate[dest].bottom(25))
                    p300.touch_tip()
                    wash_one_counter +=1
    p300.drop_tip()  

    # wash buffer 2 
    p300.pick_up_tip()   
    wash_two_h= fifty_ml_heights(38400, 32*5, 200) #32*1000 = 32000
    wash_two_counter = 0
    for plate in tot_sample_plates:
        for col in wash_two_sol_columns:
            for row in rows_on_plate:
                dest = row+str(col)
                for i in range(5):
                    p300.aspirate(wash_two_sol_per_well/5, wash_sol_two.bottom(wash_two_h[wash_two_counter]), rate=0.75) #slower due to ethanol
                    p300.dispense(wash_two_sol_per_well/5, plate[dest].bottom(25))
                    p300.blow_out(plate[dest].bottom(25))
                    p300.touch_tip()
                    wash_two_counter +=1
    p300.drop_tip()  
    
    # wash buffer 3
    p300.pick_up_tip()
    wash_three_h = fifty_ml_heights(38400, 32*5, 200) #32*1000 = 32000
    wash_three_counter = 0   
    for plate in tot_sample_plates:
        for col in wash_three_etoh_columns:
            for row in rows_on_plate:
                dest = row+str(col)
                for i in range(5):
                    p300.aspirate(wash_three_etoh_per_well/5, wash_sol_three_etoh.bottom(wash_three_h[wash_three_counter]), rate=0.65) #slower due to ethanol
                    p300.dispense(wash_three_etoh_per_well/5, plate[dest].bottom(25))
                    p300.blow_out(plate[dest].bottom(25))
                    p300.touch_tip()
                    wash_three_counter +=1
    p300.drop_tip()  

# lysis buffer
    ly_h = fifty_ml_heights(15360, 32*2, 200) #32*400 = 128000
    ly_h_counter = 0
    p300.pick_up_tip()   
    for plate in tot_sample_plates:
        for col in lysis_buffer_columns:
            for row in rows_on_plate:
                dest = row+str(col)
                p300.aspirate(lysis_buffer_per_well/2, lysis_buffer.bottom(ly_h[ly_h_counter]), rate=0.75)
                p300.dispense(lysis_buffer_per_well/2, plate[dest].bottom(10))
                p300.blow_out(plate[dest].bottom(20))
                p300.aspirate(lysis_buffer_per_well/2, lysis_buffer.bottom(ly_h[ly_h_counter]), rate=0.75)
                p300.dispense(lysis_buffer_per_well/2, plate[dest].bottom(15))
                p300.blow_out(plate[dest].bottom(20))
                p300.touch_tip()
                ly_h_counter +=1
    p300.drop_tip()    

    # elution buffer (NFW)
    # pipette this solution last to avoid evaporative losses
    p300.pick_up_tip()
    NFW_counter = 0
    NFW_h = fifty_ml_heights(6144, 32, 100) #32*100 = 3200
    for plate in tot_sample_plates:
        for col in elution_columns:
            for row in rows_on_plate:
                dest = row+str(col)
                p300.aspirate(elution_buffer_per_well, nfw.bottom(NFW_h[NFW_counter]))
                p300.dispense(elution_buffer_per_well, plate[dest].bottom(20))
                p300.blow_out(plate[dest].bottom(20))
                p300.touch_tip() #every drop important
                NFW_counter +=1
    p300.drop_tip() 