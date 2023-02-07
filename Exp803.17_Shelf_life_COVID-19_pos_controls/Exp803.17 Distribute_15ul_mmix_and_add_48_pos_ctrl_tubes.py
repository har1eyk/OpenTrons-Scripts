# imports
from re import I
from opentrons import protocol_api

# metadata
metadata = {
    'protocolName': 'Distribute 15ul COVID-19 RT qPCR mmix and Add 12 Pos Ctrl Tubes x 4 Temps.',
    'author': 'Harley King <harley.king@luminultra.com>',
    'description': 'Aliquoting COVID-19 to PCR plate and adding 5ul pos ctrl DNA from 48 tubes.',
    'apiLevel': '2.13'
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

def run(protocol: protocol_api.ProtocolContext):

    # LABWARE
    tiprack20 = protocol.load_labware('opentrons_96_filtertiprack_20ul', '9')
    
    tempdeck = protocol.load_module('tempdeck', '10')
    pcr_plate = tempdeck.load_labware('bioer_96_aluminumblock_200ul')
    
    # tempdeckTwo = protocol.load_module('tempdeck', '7')
    # alumBlock = tempdeckTwo.load_labware('opentrons_24_aluminumblock_generic_2ml_screwcap')

    # mmix_rack = protocol.load_labware('vwr_24_tuberack_1500ul', '4')
    mmix_rack = protocol.load_labware('opentrons_24_tuberack_eppendorf_2ml_safelock_snapcap', '4')
    tempOne_rack = protocol.load_labware('opentrons_24_tuberack_nest_1.5ml_screwcap', '1')
    tempTwo_rack = protocol.load_labware('opentrons_24_tuberack_nest_1.5ml_screwcap', '2')
    tempThree_rack = protocol.load_labware('opentrons_24_tuberack_nest_1.5ml_screwcap', '3')
    tempFour_rack = protocol.load_labware('opentrons_24_tuberack_nest_1.5ml_screwcap', '5')
    tempFive_rack = protocol.load_labware('opentrons_24_tuberack_nest_1.5ml_screwcap', '6')

    # PIPETTES
    p20 = protocol.load_instrument(
        'p20_single_gen2', 'right', tip_racks=[tiprack20]
    )
    
    # PLATE OUTLINE
    # this outline done by Kaveh, 20221220

# +---+---------------------+---------------------+---------------------+---------------------+--------------------+--------------------+--------------------+--------------------+--------------------+--------------------+--------------------+-------------------+
# | + |          1          |          2          |          3          |          4          |         5          |         6          |         7          |         8          |         9          |         10         |         11         |        12         |
# +---+---------------------+---------------------+---------------------+---------------------+--------------------+--------------------+--------------------+--------------------+--------------------+--------------------+--------------------+-------------------+
# | A | 100⁰C Tube 1 8hr    | 100⁰C Tube 1 8hr    | 100⁰C Tube 2 8hr    | 100⁰C Tube 2 8hr    | 90⁰C Tube 1 8hr    | 90⁰C Tube 1 8hr    | 90⁰C Tube 2 8hr    | 90⁰C Tube 2 8hr    | 80⁰C Tube 1 8hr    | 80⁰C Tube 1 8hr    | 80⁰C Tube 2 8hr    | 80⁰C Tube 2 8hr   |
# | B | 100⁰C Tube 1 24hr   | 100⁰C Tube 1 24hr   | 100⁰C Tube 2 24hr   | 100⁰C Tube 2 24hr   | 90⁰C Tube 1 24hr   | 90⁰C Tube 1 24hr   | 90⁰C Tube 2 24hr   | 90⁰C Tube 2 24hr   | 80⁰C Tube 1 24hr   | 80⁰C Tube 1 24hr   | 80⁰C Tube 2 24hr   | 80⁰C Tube 2 24hr  |
# | C | 100⁰C Tube 1 48hr   | 100⁰C Tube 1 48hr   | 100⁰C Tube 2 48hr   | 100⁰C Tube 2 48hr   | 90⁰C Tube 1 48hr   | 90⁰C Tube 1 48hr   | 90⁰C Tube 2 48hr   | 90⁰C Tube 2 48hr   | 80⁰C Tube 1 48hr   | 80⁰C Tube 1 48hr   | 80⁰C Tube 2 48hr   | 80⁰C Tube 2 48hr  |
# | D | 100⁰C Tube 1 72hr   | 100⁰C Tube 1 72hr   | 100⁰C Tube 2 72hr   | 100⁰C Tube 2 72hr   | 90⁰C Tube 1 72hr   | 90⁰C Tube 1 72hr   | 90⁰C Tube 2 72hr   | 90⁰C Tube 2 72hr   | 80⁰C Tube 1 72hr   | 80⁰C Tube 1 72hr   | 80⁰C Tube 2 72hr   | 80⁰C Tube 2 72hr  |
# | E | 100⁰C Tube 1 96hr   | 100⁰C Tube 1 96hr   | 100⁰C Tube 2 96hr   | 100⁰C Tube 2 96hr   | 90⁰C Tube 1 96hr   | 90⁰C Tube 1 96hr   | 90⁰C Tube 2 96hr   | 90⁰C Tube 2 96hr   | 80⁰C Tube 1 96hr   | 80⁰C Tube 1 96hr   | 80⁰C Tube 2 96hr   | 80⁰C Tube 2 96hr  |
# | F | 100⁰C Tube 1 104hr  | 100⁰C Tube 1 104hr  | 100⁰C Tube 2 104hr  | 100⁰C Tube 2 104hr  | 90⁰C Tube 1 104hr  | 90⁰C Tube 1 104hr  | 90⁰C Tube 2 104hr  | 90⁰C Tube 2 104hr  | 80⁰C Tube 1 104hr  | 80⁰C Tube 1 104hr  | 80⁰C Tube 2 104hr  | 80⁰C Tube 2 104hr |
# | G | 70⁰C Tube 1 8hr     | 70⁰C Tube 1 8hr     | 70⁰C Tube 2 8hr     | 70⁰C Tube 2 8hr     | 70⁰C Tube 1 24hr   | 70⁰C Tube 1 24hr   | 70⁰C Tube 2 24hr   | 70⁰C Tube 2 24hr   | 70⁰C Tube 1 48hr   | 70⁰C Tube 1 48hr   | 70⁰C Tube 2 48hr   | 70⁰C Tube 2 48hr  |
# | H | 70⁰C Tube 1 96hr    | 70⁰C Tube 1 96hr    | 70⁰C Tube 2 96hr    | 70⁰C Tube 2 96hr    | 70⁰C Tube 1 104hr  | 70⁰C Tube 1 104hr  | 70⁰C Tube 2 104hr  | 70⁰C Tube 2 104hr  | Room Temp Tube 1   | Room Temp Tube 1   | Room Temp Tube 2   | Room Temp Tube 2  |
# +---+---------------------+---------------------+---------------------+---------------------+--------------------+--------------------+--------------------+--------------------+--------------------+--------------------+--------------------+-------------------+
       
    # tube_rack
    LU_Mix = mmix_rack['A1'] # LU MasterMix; must be in the same tubes as the a_stds, "2mL generic screw cap" 15*96*1.1ul = 1710ul
    
    # #### COMMANDS ######    
    #-------OVERVIEW----------#
    # Part 1: Add COVID mmix to all wells in 96w plate
    # Part 2.1: Add the first three pos control to the top part A-F of the plate
    # Part 2.2: Add the last pos control to the bottom part G-H of the plate
    # Part 2.3: Add the RT controls to wells H9-H12
    
    # PART 1
    # aspirate mmix to all wells in 96w plate; 15*96 = 1440ul*1.10=1584ul
    rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
    h_list = tip_heightsEpp(1584, 96, 15)
    well_num = 1
    p20.pick_up_tip()
    p20.mix(3, 20, LU_Mix.bottom(h_list[well_num-1]))
    for row in rows: #8 rows
        for col in range(1,13): #12 cols
            dest = row+str(col)
            p20.aspirate(15, LU_Mix.bottom(h_list[well_num-1]), rate=0.75)
            protocol.delay(seconds=1) #head vol for more accurate pipetting
            p20.move_to(LU_Mix.bottom(38))
            protocol.delay(seconds=2) #equilibrate
            p20.touch_tip(v_offset=-3, speed=30)
            p20.dispense(15, pcr_plate[dest].bottom(3))
            p20.blow_out(pcr_plate[dest].bottom(8))
            protocol.delay(seconds=1) #equilibrate
            p20.move_to(pcr_plate[dest].bottom(3)) # touch to remove fluid from tip
            well_num += 1
    p20.drop_tip()
    
    # PART 2.1
    # add 5ul of pos control timeseries to each well in 96w plate
    tubePositionsRepOne= ['A1', 'A2', 'A3', 'A4', 'A5', 'A6'] # 8hr, 24hr, 48hr, 72hr, 96hr, 104hr rep 1
    tubePositionsRepTwo= ['B1', 'B2', 'B3', 'B4', 'B5', 'B6'] # 8hr, 24hr, 48hr, 72hr, 96hr, 104hr rep 2
   
    racks = [tempOne_rack, tempTwo_rack, tempThree_rack]
    tubePositions = [tubePositionsRepOne, tubePositionsRepTwo]
    q = 0 # column counter
    for rack in (racks):
        for posList in (tubePositions):
            for r, tube in enumerate(posList):
                # print ("row =", rows[r], "col =", q, "pos =", pos)
                p20.pick_up_tip()
                source = rack[tube]
                p20.mix(1, 20, source.bottom(2))
                p20.aspirate(17, source.bottom(2))
                p20.dispense(5, source.bottom(2)) # dispense 1x back into tube
                protocol.delay(seconds=1)
                destOne = pcr_plate[rows[r]+str(q+1)] # combined[q]]
                destTwo = pcr_plate[rows[r]+str(q+2)] # combined[q+1]]
                p20.dispense(5, destOne.bottom(3))
                p20.dispense(5, destTwo.bottom(3))
                p20.drop_tip()
            q = q+2
    
    # PART 2.2
    # adding 5ul of fourth series to the bottom part of the plate.
    # easier to just write out the locations.
    fourthTempTubePositionsRepOne= ['A1', 'A2', 'A3', 'A4', 'A6'] # 8hr, 24hr, 48hr, 72hr, 104hr rep 1; removing 1st rep of 96hr to make room for RT controls
    fourthTempTubePositionsRepTwo= ['B1', 'B2', 'B3', 'B5', 'B6'] # 8hr, 24hr, 48hr, 96hr, 104hr rep 2; removing 2nd rep of 72hr to make room for RT controls
    tempFourRepOneDest = ['G1', 'G2', 'G5', 'G6', 'G9', 'G10', 'H1', 'H2', 'H5', 'H6'] # removing 1st replicate of 96hr to make room for RT controls
    tempFourRepTwoDest = ['G3', 'G4', 'G7', 'G8', 'G11', 'G12', 'H3', 'H4', 'H7', 'H8'] # removing 2nd replicate of 72hr to make room for RT controls
    fourthTempPositions = [fourthTempTubePositionsRepOne, fourthTempTubePositionsRepTwo]
    fourthTempDestinations = [tempFourRepOneDest, tempFourRepTwoDest]
    
    for y, posList in enumerate(fourthTempPositions): # need enumerator to select the correct destination list
        x = 0 # counter for tubePositions
        for pos in (posList):
            p20.pick_up_tip()
            source = tempFour_rack[pos]
            p20.mix(1, 20, source.bottom(2))
            p20.aspirate(17, source.bottom(2))
            p20.dispense(5, source.bottom(2)) # dispense 1x back into tube
            protocol.delay(seconds=1)
            destOne = pcr_plate[fourthTempDestinations[y][x]] 
            destTwo = pcr_plate[fourthTempDestinations[y][x+1]] 
            p20.dispense(5, destOne.bottom(3))
            p20.dispense(5, destTwo.bottom(3))
            p20.drop_tip()
            x = x+2

    # PART 2.3
    # adding 5ul of RT pos controls to the bottom part of the plate.
    # easier to just write out the locations.
    rTTubePositionsRepOne= ['A1'] # RT rep 1; removing 1st rep of 96hr to make room for RT controls
    rTTubePositionsRepTwo= ['B1'] # RT rep 2; removing 2nd rep of 72hr to make room for RT controls
    rTRepOneDest = ['H9', 'H10'] # rep 1 destinations
    rTRepTwoDest = ['H11', 'H12'] # rep 2 destinations
    rTPositions = [rTTubePositionsRepOne, rTTubePositionsRepTwo]
    rTDestinations = [rTRepOneDest, rTRepTwoDest]
    
    for w, rtList in enumerate(rTPositions): # need enumerator to select the correct destination list
        z = 0 # counter for tubePositions
        for rtpos in (rtList):
            p20.pick_up_tip()
            source = tempFive_rack[rtpos]
            p20.mix(1, 20, source.bottom(2))
            p20.aspirate(17, source.bottom(2))
            p20.dispense(5, source.bottom(2)) # dispense 1x back into tube
            protocol.delay(seconds=1)
            destOne = pcr_plate[rTDestinations[w][z]] 
            destTwo = pcr_plate[rTDestinations[w][z+1]] 
            p20.dispense(5, destOne.bottom(3))
            p20.dispense(5, destTwo.bottom(3))
            p20.drop_tip()
            z = z+2
