# imports
from opentrons import protocol_api

# metadata
metadata = {
    'protocolName': '#2_N2--Use RNA dil series and Distribute MasterMix to 96w Plate and Add 5ul WBE N2 Samples from 1.5mL Tubes.',
    'author': 'Harley King <harley.king@luminultra.com>',
    'description': 'WBE--Aliquoting SARS-CoV-2 mix to PCR plate and adding 5ul WBE sample extraction and stds from 1.5mL tubes after 15ul mix.',
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

def run(protocol: protocol_api.ProtocolContext):

    # LABWARE
    mix_rack = protocol.load_labware('opentrons_24_tuberack_eppendorf_2ml_safelock_snapcap', '11')
    sample_rack = protocol.load_labware('vwr_24_tuberack_1500ul', '4')
    stds_rack = protocol.load_labware('vwr_24_tuberack_1500ul', '5') # this is where the N1, N2 standards go

    tiprack20 = protocol.load_labware('opentrons_96_filtertiprack_20ul', '9')
    tempdeck = protocol.load_module('tempdeck', '10')
    # pcr_plate = tempdeck.load_labware('abi_96_wellplate_250ul')
    pcr_plate = tempdeck.load_labware('bioer_96_aluminumblock_200ul')
    # ww_plate1 = protocol.load_labware('bioer_96_wellplate_2200ul', '1')

    # PIPETTES
    p20 = protocol.load_instrument(
    'p20_single_gen2', 'right', tip_racks=[tiprack20]
    )
    
    # REAGENTS   
    LU_Mix = mix_rack['A1'] # LU MasterMix
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
    std1= stds_rack['A1']
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


