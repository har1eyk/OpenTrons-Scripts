# imports
from opentrons import protocol_api

# metadata
metadata = {
    'protocolName': 'Create Amplification Curve using Pos Control Dilution Series with 15ul MasterMix and Two MasterMixes',
    'author': 'Harley King <harley.king@luminultra.com>',
    'description': 'Create a 4-rep pos control amplification in a 96w plate.',
    'apiLevel': '2.12'
}
##########################
# functions
# returns zipped array of volumes and heights for
# simultaneous dispensing and tip ascension
# to reduce chance of air pocket formation
def d_dispense(vol:int, steps:int, height:float):
    # what is the height of total volume?
    lowestHeight = 1 # don't go lower than this
    heightIncrement = (height-lowestHeight)/steps
    heightList = list(range(1,steps)) # make a list from 1..steps
    heightArray =[1] + [1+x*heightIncrement for x in heightList]
    volArray = [vol/steps]*steps
    return zip(volArray, heightArray)

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

def run(protocol: protocol_api.ProtocolContext):

    # LABWARE
    mix_rack = protocol.load_labware('vwr_24_tuberack_1500ul', '1')
    fuge_rack = protocol.load_labware('vwr_24_tuberack_1500ul', '2')
    tiprack300 = protocol.load_labware('opentrons_96_filtertiprack_200ul', '8')
    tiprack20 = protocol.load_labware('opentrons_96_filtertiprack_20ul', '9')
    tempdeck = protocol.load_module('tempdeck', '10')
    stds_plate = tempdeck.load_labware('abi_96_wellplate_250ul')
    
    # PIPETTES
    p300 = protocol.load_instrument(
        'p300_single_gen2', 'left', tip_racks=[tiprack300]
    )
    p20 = protocol.load_instrument(
        'p20_single_gen2', 'right', tip_racks=[tiprack20]
    )
     
    # REAGENTS 
    std_1 = fuge_rack['A1'] # diluted standard
    std_2 = fuge_rack['A2']
    std_3 = fuge_rack['A3']
    std_4 = fuge_rack['A4']
    std_5 = fuge_rack['A5']
    std_6 = fuge_rack['A6'] 
    std_7 = fuge_rack['B1']
    std_8 = fuge_rack['B2']

    # pos_control = fuge_rack['D1'] # pos control @1uM
    water = fuge_rack['D6'] # 1500ul water
    
    # mix_rack
    mmixOne = mix_rack['A1'] # 15*40*1.125 = 675µl
    mmixTwo = mix_rack['A6'] # 15*40*1.125 = 675µl
    # CALCS
    mix_per_well = 15 #how much volume (ul) mastermix should be in each well?
    overage = 0.125 # e.g. twenty percent waste as decimal
    reps = 4 #how many replicates of each std?
    multiwell_mix = mix_per_well*reps*(1+overage) # 15*4*(1+0.125) = 67.5ul
    sample_per_well = 5
    multisample_mix = sample_per_well*reps*(1+overage) # 5*4*(1+0.125) = 22.5
    # LISTS
    mixOne_wells=['A1', 'B1', 'C1', 'D1', 'E1', 'F1', 'G1', 'H1']
    mixTwo_wells=['A6', 'B6', 'C6', 'D6', 'E6', 'F6', 'G6', 'H6']
    std_wells = [std_1, std_2, std_3, std_4, std_5, std_6, std_7, std_8]
    mixList = [mmixOne, mmixTwo]
    wellList = [mixOne_wells, mixTwo_wells]

    #### COMMANDS ######
    # Mix, pipette mastermix containing probe to each well on plate 
    for mmix, wwell in zip(mixList, wellList): # iterate through mastermixes and well list per mix
        p300.pick_up_tip()
        p300.mix(3, 200, mmix.bottom(20)) #first height
        for wellLoc, h in zip(wwell, tip_heights(675, len(std_wells), multiwell_mix)): # iterate through wells and heights for each mix
            p300.aspirate(multiwell_mix, mmix.bottom(h), rate=0.75) # 15 * 4 (1.125)= 67.5
            protocol.delay(seconds=2) #tip equilibrate
            p300.move_to(mmix.bottom(35)) # excess tip fluid condense 
            protocol.delay(seconds=2) #tip droplets slide
            p300.move_to(mmix.bottom(h)) # excess tip fluid condense 
            p300.touch_tip(v_offset=-4) #touch 4 mm below surface
            for volD, heightD in d_dispense(multiwell_mix, 6, 6):
                p300.dispense(volD, stds_plate[wellLoc].bottom(heightD))
            # p300.dispense(multiwell_mix, stds_plate[well])
            p300.blow_out(stds_plate[wellLoc].bottom(12))
            p300.move_to(stds_plate[wellLoc].bottom(2))
            p300.touch_tip()
        p300.drop_tip()
    
    # # add pos control stds to into plate wells and dispense into neighboring wells
    for mmix, wwell in zip(mixList, wellList): # iterate through mastermixes and well list per mix for pos control addition and dispense
        for i in range(len(std_wells)): #loop 13x, water tube last
            p20.pick_up_tip()
            p300.pick_up_tip() #double barrel
            p300.aspirate(multisample_mix, std_wells[i].bottom(4)) #aspirate 22.5ul from template into mix well
            p300.move_to(std_wells[i].bottom(30))
            protocol.delay(seconds=3) #coalescing step
            p300.move_to(std_wells[i].bottom(18)) # remove fluid from tip
            p300.dispense(multisample_mix, stds_plate[wwell[i]].bottom(2))
            p300.mix(4, 50, stds_plate[wwell[i]].bottom(1), rate=0.5) # can't be mixed homogenously with p20 #ivetried
            p300.move_to(stds_plate[wwell[i]].bottom(12)) #above mmix solution
            protocol.delay(seconds=2) #outside fluid coalesce 
            p300.blow_out(stds_plate[wwell[i]].bottom(12))
            p300.move_to(stds_plate[wwell[i]].bottom(2)) #above mmix solution

            # transfer to adjacent wells
            for x in range(1,5): # need int 1, 2, 3 and 4.
                p20.aspirate(20, stds_plate[wwell[i]].bottom(1), rate=0.75) # asp from 54ul, dispense to neighbor well
                protocol.delay(seconds=2) #equilibrate
                # find digits in well, A1 and A10 and puts into list
                findNums = [int(i) for i in wwell[i].split()[0] if i.isdigit()]
                # joins nums from list [1, 0] -> 10 type = string
                colNum = ''.join(map(str, findNums))
                # this finds row
                row = wwell[i].split()[0][0]
                # put it all together into a destination well
                dest = row+str(int(colNum)+x) # row + neighbor well i.e. 1, 2
                p20.dispense(20, stds_plate[dest].bottom(1), rate=0.75)
                p20.touch_tip()
            p300.drop_tip()
            p20.drop_tip()