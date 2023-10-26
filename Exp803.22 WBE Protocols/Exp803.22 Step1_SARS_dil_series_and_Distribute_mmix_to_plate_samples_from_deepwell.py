# imports
from opentrons import protocol_api

# metadata
metadata = {
    'protocolName': '#1_N1 Plate--make RNA dil series and Distribute MasterMix to 96w Plate and Add 5ul WBE N1 Samples from 1.5mL Tubes.',
    'author': 'Harley King <harley.king@luminultra.com>',
    'description': 'WBE--Aliquoting SARS-CoV-2 mix to PCR plate and adding 5ul WBE sample extraction from 1.5mL tubes after 15ul mix.',
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
    mix_rack = protocol.load_labware('vwr_24_tuberack_1500ul', '11')
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
    water = water_rack['A1'] # 10.00mL

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
    std1= stds_rack['A1'] # this one should be 300ul aliquot from Twist tube, 20ul into 980ul TE
    std2= stds_rack['B1']
    std3= stds_rack['C1']
    std4= stds_rack['D1']
    std5= stds_rack['A6']
    std6= stds_rack['B6']
    std7= stds_rack['C6']
    std8= stds_rack['D6']
    stds = [std1, std2, std3, std4, std5, std6, std7, std8]
    # LISTS
    rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
    col_offset = 3 # offset for PCR plate. Where do we want to put samples? I like plate middle cols 3, 5, 7, 9
    # tot_ww_plates = [ww_plate1]

    # #### COMMANDS ######    
    # make RNA dilution series for stds.
    # Add water to tubes
    waterH=fifteen_ml_heights(10000, 4*8+1 , 187.5) # 187.5*4=750ul 33*187.5=6187.5
    dispenseH = tip_heights(750, 4, 187.5)
    p300.pick_up_tip()
    p300.mix(3, 200, water.bottom(waterH[0])) # pre-moisten tip
    for i in range(1,8): # don't need to add water to first tube
        std = stds[i]
        for h in range(1,5):
            p300.aspirate(187.5, water.bottom(waterH[4*i+h])) # function of std tube and current step 
            p300.dispense(187.5, std.bottom(dispenseH[-h])) # want to reverse heights
    p300.drop_tip()
   
    # Make std dilution series
    # refer to the helper function for pipetting operations
    def pipette_transfer(source, dest, mix_low, mix_mid, mix_hi):
        p300.pick_up_tip()
        if mix_low: p300.mix(2, 200, source.bottom(4))
        if mix_mid: p300.mix(2, 200, source.bottom(8))
        if mix_hi: p300.mix(5, 200, source.bottom(12))
        p300.aspirate(125, source.bottom(1), rate=0.8)
        p300.touch_tip(v_offset=-3, speed=20)
        p300.dispense(125, dest.bottom(8))
        p300.mix(2, 125, dest.bottom(8))
        p300.blow_out(dest.bottom(14))
        p300.touch_tip(v_offset=-3, speed=20)
        p300.aspirate(125, source.bottom(1), rate=0.85)
        p300.touch_tip(v_offset=-3, speed=20)
        p300.dispense(125, dest.bottom(8))
        p300.mix(2, 125, dest.bottom(8))
        p300.blow_out(dest.bottom(14))
        p300.touch_tip(v_offset=-3, speed=20)
        p300.drop_tip()

    i = 0
    while i < len(stds) - 1:
        if i == 0:  # first tube (std1 to std2)
            pipette_transfer(stds[i], stds[i+1], False, False, False)
        else:
            pipette_transfer(stds[i], stds[i+1], True, True, True)
        i += 1
        if i == len(stds) - 1:  # mixing in the last tube
            p300.pick_up_tip()
            p300.mix(2, 200, stds[-1].bottom(4))
            p300.mix(2, 200, stds[-1].bottom(8))
            p300.mix(5, 200, stds[-1].bottom(12))
            p300.blow_out(stds[-1].bottom(16))
            p300.drop_tip()


    # aspirate mmix to 32 wells in 96w plate; 15*32*1.2 = 578ul, 600ul
    h_list = tip_heights(600, 32, 15)
    well_num = 1
    p20.pick_up_tip()
    p20.mix(2, 20, LU_Mix.bottom(h_list[0]))
    for row in rows: #8 rows
        for col in range(4): #12 cols
            dest = row+str(2*col+col_offset) #A3, A5, A7, A9
            print (h_list[well_num-1])
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
    for std, row in zip(stds, rows):
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


