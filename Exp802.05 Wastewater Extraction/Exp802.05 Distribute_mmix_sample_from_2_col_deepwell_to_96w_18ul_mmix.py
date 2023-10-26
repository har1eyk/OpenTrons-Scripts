# imports
from opentrons import protocol_api

# metadata
metadata = {
    'protocolName': 'Distribute Mmix and Wastewater Samples from 2 Col on Deepwell to 96w Plate.',
    'author': 'Harley King <harley.king@luminultra.com>',
    'description': 'Aliquoting SARS-CoV-2 mix to PCR plate and adding 2ul sample extraction from 2 col deepwell plate after 18ul mix.',
    'apiLevel': '2.11'
}

##########################
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
        if h < 7: # prevent negative heights; go to bottom to avoid air aspirant above certain height
            h = 1        
            heights.append(h)
        else:
            heights.append(round(h, 1))
    return heights

def run(protocol: protocol_api.ProtocolContext):

    # LABWARE
    fuge_rack = protocol.load_labware('opentrons_24_tuberack_eppendorf_2ml_safelock_snapcap', '11')
    # sample_rack = protocol.load_labware('vwr_24_tuberack_1500ul', '4')
    tiprack20 = protocol.load_labware('opentrons_96_filtertiprack_20ul', '9')
    tempdeck = protocol.load_module('tempdeck', '10')
    # pcr_plate = tempdeck.load_labware('abi_96_wellplate_250ul')
    pcr_plate = tempdeck.load_labware('bioer_96_aluminumblock_200ul')
    ww_plate1 = protocol.load_labware('bioer_96_wellplate_2200ul', '1')

    # PIPETTES
    p20 = protocol.load_instrument(
    'p20_single_gen2', 'right', tip_racks=[tiprack20]
    )
    
    # REAGENTS   
    LU_Mix = fuge_rack['A1'] # LU MasterMix
    
    # LISTS
    rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
    tot_ww_plates = [ww_plate1]
    sample_cols = [5, 11]

    # #### COMMANDS ######    
    # aspirate mmix to all wells in 96w plate; 18*96 = 1.1=1584
    h_list = tip_heightsEpp(1901, 96, 18)
    well_num = 1
    p20.pick_up_tip()
    for row in rows: #8 rows
        for col in range(1,13): #12 cols
            dest = row+str(col)
            p20.aspirate(18, LU_Mix.bottom(h_list[well_num-1]), rate=0.75)
            protocol.delay(seconds=1) #head vol for more accurate pipetting
            p20.move_to(LU_Mix.bottom(38))
            protocol.delay(seconds=1) #equilibrate
            p20.touch_tip(v_offset=-4)
            p20.dispense(18, pcr_plate[dest].bottom(1))
            p20.blow_out(pcr_plate[dest].bottom(8))
            p20.touch_tip()
            well_num += 1
    p20.drop_tip()
    # pipette well-to-well from BioER to PCR plate
    # use same tip for tech replicates (in columns)
    for x, ww_plate in enumerate(tot_ww_plates):
        for y, col in enumerate(sample_cols):
            for row in rows:
                p20.pick_up_tip()
                source = row + str(col) #A5, B5, C5
                dest1 = row + str(col-4) #A1, #A2, #A3
                dest2 = row + str(col-3) #A1, #A2, #A3
                dest3 = row + str(col-2) #A1, #A2, #A3
                dest4 = row + str(col-1) #A1, #A2, #A3
                dest5 = row + str(col) #A1, #A2, #A3
                dest6 = row + str(col+1) #A1, #A2, #A3
                p20.aspirate(15, ww_plate[source].bottom(2), rate=0.75) #2*6+3bolus = 15
                p20.move_to(ww_plate[source].bottom(3)) #avoid tip jamming bottom unable to aspirate
                protocol.delay(seconds=2) #equilibrate
                p20.touch_tip()
                p20.dispense(2, pcr_plate[dest1].bottom(1))
                p20.touch_tip()
                p20.dispense(2, pcr_plate[dest2].bottom(1))
                p20.touch_tip()
                p20.dispense(2, pcr_plate[dest3].bottom(1))
                p20.touch_tip()
                p20.dispense(2, pcr_plate[dest4].bottom(1))
                p20.touch_tip()
                p20.dispense(2, pcr_plate[dest5].bottom(1))
                p20.touch_tip()
                p20.dispense(2, pcr_plate[dest6].bottom(1))
                p20.touch_tip()
                p20.drop_tip()


