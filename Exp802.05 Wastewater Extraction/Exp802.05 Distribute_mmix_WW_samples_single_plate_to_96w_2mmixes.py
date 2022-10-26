# imports
from opentrons import protocol_api

# metadata
metadata = {
    'protocolName': 'Distribute Two Mmixes and Wastewater Samples from a Single Plate, Single Column to 96wells.',
    'author': 'Harley King <harley.king@luminultra.com>',
    'description': 'Aliquoting 2 SARS-CoV-2 mixes to plate and then adding 5ul sample extraction from one column on DeepWell plate.',
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
        if h < 3: # prevent negative heights; go to bottom to avoid air aspirant above certain height
            h = 1      
            heights.append(h)
        else:
            heights.append(round(h, 1))
    return heights

def run(protocol: protocol_api.ProtocolContext):

    # LABWARE
    fuge_rack = protocol.load_labware('opentrons_24_tuberack_eppendorf_2ml_safelock_snapcap', '11')
    tiprack20 = protocol.load_labware('opentrons_96_filtertiprack_20ul', '9')
    tempdeck = protocol.load_module('tempdeck', '10')
    # sectempdeck = protocol.load_module('tempdeck', '4')
    pcr_plate = tempdeck.load_labware('abi_96_wellplate_250ul')
    # stds_rack = sectempdeck.load_labware('opentrons_24_aluminumblock_generic_2ml_screwcap')
    ww_plate1 = protocol.load_labware('bioer_96_wellplate_2200ul', '1')
    

    # PIPETTES
    p20 = protocol.load_instrument(
        'p20_single_gen2', 'right', tip_racks=[tiprack20]
    )
    
    # REAGENTS   
    N2 = fuge_rack['A1'] # LU MasterMix
    N1 = fuge_rack['B1'] # water
    LUPositive = fuge_rack['D6'] # LU Positive Control plasmid
    mixes = [N2, N1]
     # LISTS
    rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
    N2_cols = [1, 2, 3, 4, 5, 6]
    N1_cols = [7, 8, 9, 10, 11, 12]

    # #### COMMANDS ######    
    # aspirate mmix to all wells in 96w plate; 15*48 = 720ul*1.1=792
    h_list = tip_heightsEpp(792, 48, 15)
    for y, pcrmix in enumerate(mixes): #12 cols
        p20.pick_up_tip()
        well_num = 1
        for z in range(1,7):
            for row in rows: #8 rows
                # print (y)
                col = 6*y+z
                dest = row+str(col)
                # print ("height is: ", h_list[well_num-1])
                p20.aspirate(15, pcrmix.bottom(h_list[well_num-1]), rate=0.75) #head vol for more accurate pipetting
                protocol.delay(seconds=1) #equilibrate
                p20.move_to(pcrmix.bottom(38))
                protocol.delay(seconds=1) #equilibrate
                p20.touch_tip(v_offset=-4)
                p20.dispense(15, pcr_plate[dest].bottom(1))
                p20.blow_out(pcr_plate[dest].bottom(8))
                p20.touch_tip()
                well_num += 1
        p20.drop_tip()

    tot_ww_plates = [ww_plate1]
    for x, ww_plate in enumerate(tot_ww_plates):
        for col in range(0,1): #samples in col 5, 11
            for row in rows:
                p20.pick_up_tip()
                source = row + str(6*col+5) #A5, B5, C5
                dest1 = row + str(6*x+6*col+1) #A1, #A2, #A3
                dest2 = row + str(6*x+6*col+2)
                dest3 = row + str(6*x+6*col+3)
                dest4 = row + str(6*x+6*col+4)
                dest5 = row + str(6*x+6*col+5)
                dest6 = row + str(6*x+6*col+6)
                dest7 = row + str(6*x+6*col+7)
                dest8 = row + str(6*x+6*col+8)
                dest9 = row + str(6*x+6*col+9)
                dest10 = row + str(6*x+6*col+10)
                dest11 = row + str(6*x+6*col+11)
                dest12 = row + str(6*x+6*col+12)
                p20.aspirate(18, ww_plate[source].bottom(1))
                protocol.delay(seconds=2) #equilibrate
                p20.dispense(5, pcr_plate[dest1].bottom(1))
                p20.touch_tip()    
                p20.dispense(5, pcr_plate[dest2].bottom(1))    
                p20.touch_tip()    
                p20.dispense(5, pcr_plate[dest3].bottom(1))    
                p20.touch_tip()    
                p20.drop_tip()
                p20.pick_up_tip()
                p20.aspirate(18, ww_plate[source].bottom(1))
                protocol.delay(seconds=2) #equilibrate
                p20.dispense(5, pcr_plate[dest4].bottom(1))
                p20.touch_tip()    
                p20.dispense(5, pcr_plate[dest5].bottom(1))
                p20.touch_tip()    
                p20.dispense(5, pcr_plate[dest6].bottom(1))
                p20.touch_tip()    
                p20.drop_tip()

                p20.pick_up_tip()                
                p20.aspirate(18, ww_plate[source].bottom(1))
                protocol.delay(seconds=2) #equilibrate
                p20.dispense(5, pcr_plate[dest7].bottom(1))
                p20.touch_tip()    
                p20.dispense(5, pcr_plate[dest8].bottom(1))    
                p20.touch_tip()    
                p20.dispense(5, pcr_plate[dest9].bottom(1))    
                p20.touch_tip()    
                p20.drop_tip()
                
                p20.pick_up_tip()
                p20.aspirate(18, ww_plate[source].bottom(1))
                protocol.delay(seconds=2) #equilibrate
                p20.dispense(5, pcr_plate[dest10].bottom(1))
                p20.touch_tip()    
                p20.dispense(5, pcr_plate[dest11].bottom(1))    
                p20.touch_tip()    
                p20.dispense(5, pcr_plate[dest12].bottom(1))    
                p20.touch_tip()    
                p20.drop_tip()


