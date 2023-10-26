# imports
from opentrons import protocol_api

# metadata
metadata = {
    'protocolName': '#3_OC43--make gRNA dil series and Distribute MasterMix to 96w Plate and Add 5ul WBE OC43 and MLR Samples from 1.5mL Tubes.',
    'author': 'Harley King <harley.king@luminultra.com>',
    'description': 'WBE--Aliquoting OC43 mix to PCR plate and adding 5ul WBE sample extraction from 1.5mL tubes after 15ul mix.',
    'apiLevel': '2.13'
}

##########################
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
        offset =6 #mm Need to add offset to ensure tip reaches below liquid level
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
# calculate water level heights in 15mL tube
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
# prtocol
def run(protocol: protocol_api.ProtocolContext):

    # LABWARE
    mix_rack = protocol.load_labware('opentrons_24_tuberack_eppendorf_2ml_safelock_snapcap', '11')
    sample_rack = protocol.load_labware('vwr_24_tuberack_1500ul', '4')
    stds_rack = protocol.load_labware('vwr_24_tuberack_1500ul', '5') # this is where the N1, N2 standards go
    tiprack300 = protocol.load_labware('opentrons_96_filtertiprack_200ul', '8')
    tiprack20 = protocol.load_labware('opentrons_96_filtertiprack_20ul', '9')
    tempdeck = protocol.load_module('tempdeck', '10')
    # pcr_plate = tempdeck.load_labware('abi_96_wellplate_250ul')
    pcr_plate = tempdeck.load_labware('bioer_96_aluminumblock_200ul')
    # ww_plate1 = protocol.load_labware('bioer_96_wellplate_2200ul', '1')
    water_rack = protocol.load_labware('opentrons_10_tuberack_falcon_4x50ml_6x15ml_conical', '3')

    # PIPETTES
    p300 = protocol.load_instrument(
        'p300_single_gen2', 'left', tip_racks=[tiprack300]
    )
    p20 = protocol.load_instrument(
    'p20_single_gen2', 'right', tip_racks=[tiprack20]
    )
    
    # REAGENTS   
    LU_Mix = mix_rack['A1'] # LU MasterMix
    water = water_rack['A1'] # 5mL
    

    # SAMPLES
    samp1 = sample_rack['A1']
    samp2 = sample_rack['B1']
    samp3 = sample_rack['C1']
    samp4 = sample_rack['D1']
    samp5 = sample_rack['A6']
    samp6 = sample_rack['B6']
    samp7 = sample_rack['C6'] 
    samp8 = sample_rack['D6'] 
    samples = [samp1, samp2, samp3, samp4, samp5, samp6, samp7, samp8]
    # STANDARDS
    std1= stds_rack['A1'] # this one should contain about 2.1e5 OC43
    std2= stds_rack['B1']
    std3= stds_rack['C1']
    std4= stds_rack['D1']
    std5= stds_rack['A6']
    std6= stds_rack['B6']
    mlr_1 = stds_rack['C6'] # MLR diluted 1:10, 0.5ng/ul
    mlr_2   = stds_rack['D6'] # MLR undiluted 5ng/ul
    stds = [std1, std2, std3, std4, std5, std6]
    all_stds_and_mlr = [std1, std2, std3, std4, std5, std6, mlr_1, mlr_2]
    # LISTS
    rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
    col_offset = 3 # offset for PCR plate. Where do we want to put samples? I like plate middle cols 3, 5, 7, 9
    # tot_ww_plates = [ww_plate1]

    # #### COMMANDS ######    
    # aspirate mmix to 32 wells in 96w plate; 15*32*1.2 = 578ul, 600ul
    h_list = tip_heights(600, 32, 15)
    well_num = 1
    p20.pick_up_tip()
    p20.mix(2, 20, LU_Mix.bottom(h_list[0]))
    for row in rows: #8 rows
        for col in range(4): #12 cols
            dest = row+str(2*col+col_offset) #A3, A5, A7, A9
            # print (h_list[well_num-1])
            p20.aspirate(15, LU_Mix.bottom(h_list[well_num-1]), rate=0.75)
            protocol.delay(seconds=1) #head vol for more accurate pipetting
            p20.move_to(LU_Mix.bottom(38))
            protocol.delay(seconds=1) #equilibrate
            p20.touch_tip(v_offset=-4)
            p20.dispense(15, pcr_plate[dest].bottom(1))
            p20.blow_out(pcr_plate[dest].bottom(8))
            p20.touch_tip()
            well_num += 1
    p20.drop_tip()

    # make OC43 dilution series for stds.
    # Add water to tubes for OC43 dilution series
    waterH=fifteen_ml_heights(5000, 6, 45) # 187.5*4=750ul 33*187.5=6187.5
    print ("water heights", waterH)
    p300.pick_up_tip()
    p300.mix(3, 200, water.bottom(waterH[0])) # pre-moisten tip
    for i in range(1,6): # don't need to add water to first tube
        std = stds[i]
        for h in range(1):
            p300.aspirate(60, water.bottom(waterH[i])) # function of std tube and current step 
            p300.dispense(45, std.bottom(1)) 
            protocol.delay(seconds=1)
            p300.move_to(std.bottom(6)) # move up
            protocol.delay(seconds=1)
            p300.move_to(std.bottom(1)) # touch liquid to remove droplets
            print ("added", 45, "ul from water to ", std)
            p300.dispense(15, water.bottom(waterH[i])) 
    p300.drop_tip()
   
    # Make OC43 std dilution series
    for i in range(len(stds)-1):
        if i == 0: # first tube
            p20.pick_up_tip()
            p20.mix (2, 20, stds[i].bottom(1)) # mix low, only ~50ul, sometimes less
            p20.aspirate(5, stds[i].bottom(1), rate=0.8) # 2*150 = 250
            p20.touch_tip(v_offset=-3, speed=80)
            p20.dispense(5, stds[i+1].bottom(2))
            p20.mix(3, 20, stds[i+1].bottom(2))  # wash tip
            p20.blow_out(stds[i+1].bottom(3))  # blow out just below the surface
            p20.touch_tip(v_offset=-3, speed=80)
            p20.drop_tip()
        else: # 2nd, 3rd, 4th, 5th, 6th tubes
            p20.pick_up_tip()
            p20.mix (2, 20, stds[i].bottom(1)) # mix low, only ~50ul, sometimes less
            p20.aspirate(5, stds[i].bottom(1), rate=0.8) # 2*150 = 250
            p20.touch_tip(v_offset=-3, speed=80)
            p20.dispense(5, stds[i+1].bottom(2))
            p20.mix(3, 20, stds[i+1].bottom(2))  # wash tip
            p20.blow_out(stds[i+1].bottom(3))  # blow out just below the surface
            p20.touch_tip(v_offset=-3, speed=80)
            p20.drop_tip()
        if i == len(stds)-1: # last tube
            p20.pick_up_tip()
            p20.mix(3, 20, stds[-1].bottom(2))  # mix low
            p20.touch_tip(v_offset=-3, speed=80)
            p20.drop_tip()

    # pipette from 1.5mL tube containing samples from deepwell plate
    # use same tip for duplicates (in columns)
    for sample, row in zip(samples, rows):
        p20.pick_up_tip()
        dest1 = row + str(col_offset) #A3, 
        dest2 = row + str(col_offset+2) #A5
        p20.aspirate(12, sample.bottom(1), rate=0.75) #2*6+3bolus = 15
        p20.touch_tip()
        p20.dispense(5, pcr_plate[dest1].bottom(1))
        p20.touch_tip()
        p20.dispense(5, pcr_plate[dest2].bottom(1))
        p20.touch_tip()
        p20.drop_tip()

    # pipette from 1.5mL tube containing stds
    # use same tip for duplicates (in columns)
    for std, row in zip( all_stds_and_mlr, rows):
        p20.pick_up_tip()
        dest1 = row + str(col_offset+4) #A3, 
        dest2 = row + str(col_offset+6) #A5
        p20.aspirate(12, std.bottom(1), rate=0.75) #2*6+3bolus = 15
        p20.touch_tip()
        p20.dispense(5, pcr_plate[dest1].bottom(1))
        p20.touch_tip()
        p20.dispense(5, pcr_plate[dest2].bottom(1))
        p20.touch_tip()
        p20.drop_tip()


