# imports
from opentrons import protocol_api

# metadata
metadata = {
    'protocolName': 'Compare Two MasterMixes with Three Assays and Eight Standards in 96w Plate',
    'author': 'Harley King <harley.king@luminultra.com>',
    'description': '18ul mix is dispensed with 2ul stds from two mastermixes in three assays using eight standards. Which mmix is better?',
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
        offset = 8 # model out of range; see sheet
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
    mix_rack = protocol.load_labware('vwr_24_tuberack_1500ul', '4')
    primers_rack = protocol.load_labware('opentrons_24_tuberack_generic_2ml_screwcap', '1')
    stdsOne_rack = protocol.load_labware('vwr_24_tuberack_1500ul', '2')
    stdsTwo_rack = protocol.load_labware('vwr_24_tuberack_1500ul', '3')
    stdsThree_rack = protocol.load_labware('vwr_24_tuberack_1500ul', '6')
    tiprack300 = protocol.load_labware('opentrons_96_filtertiprack_200ul', '8')
    tiprack20 = protocol.load_labware('opentrons_96_filtertiprack_20ul', '9')
    tempdeck = protocol.load_module('tempdeck', '10')
    stds_plate = tempdeck.load_labware('bioer_96_aluminumblock_200ul')

    # PIPETTES
    p300 = protocol.load_instrument(
        'p300_single_gen2', 'left', tip_racks=[tiprack300]
    )
    p20 = protocol.load_instrument(
        'p20_single_gen2', 'right', tip_racks=[tiprack20]
    )

    # mix_rack
    polyMixOne = mix_rack['A1'] # 18*48*(1.2) = 1036.8µl, should include primers
    polyMixTwo = mix_rack['A6'] 
    mmixOneAssayOne=mix_rack['B1']
    mmixOneAssayTwo=mix_rack['C1']
    mmixOneAssayThree=mix_rack['D1']
    mmixTwoAssayOne=mix_rack['B6']
    mmixTwoAssayTwo=mix_rack['C6']
    mmixTwoAssayThree=mix_rack['D6']

    # primer_rack
    FOligoAssayOne=primers_rack['A1']
    ROligoAssayOne=primers_rack['A2']
    FOligoAssayTwo=primers_rack['B1']
    ROligoAssayTwo=primers_rack['B2']
    FOligoAssayThree=primers_rack['C1']
    ROligoAssayThree=primers_rack['C2']

    # CALCS
    mix_per_well = 18 #how much volume (ul) mastermix should be in each well?
    sample_per_well = 2

    # LISTS
    polyMixTubeListOne = [mmixOneAssayOne, mmixOneAssayTwo, mmixOneAssayThree]
    polyMixTubeListTwo = [ mmixTwoAssayOne, mmixTwoAssayTwo, mmixTwoAssayThree]
    polyMixTubeList = [polyMixTubeListOne, polyMixTubeListTwo]
    polyMixList = [polyMixOne, polyMixTwo]
    mmixVol = 18*16*1.1 # the number of wells per assay per mastermix with 10% overage
    primersList = [[FOligoAssayOne,ROligoAssayOne], [FOligoAssayTwo,ROligoAssayTwo], [FOligoAssayThree, ROligoAssayThree]]
    assayOnePrimerConc = 300 # what is the conc in nM of F, R primers?
    assayTwoPrimerConc = 300 
    assayThreePrimerConc = 300 
    primerSourceConc = 100 #100uM
    primersConc = [assayOnePrimerConc, assayTwoPrimerConc, assayThreePrimerConc]

    #### COMMANDS ######
    # PROGRAM OUTLINE #
    # 1.1 Each of 2 polymerase mixes is subdivided into 3 tubes. 
    # 1.2 Two primers are added to generate 6 mmixes
    # 1.3 mix and aliquot to wells
    # 1.4 both 200 and 20ul tips picked up, aspirate 2 well's worth of mastermix and 2 well's worth of template, dispense, mix and add to next well. 

    # 1.1 Each of 2 polymerase mixes is subdivided into 3 tubes. 
    for i, polyMix in enumerate(polyMixList):
        p300.pick_up_tip()
        p300.mix(3, 200, polyMix.bottom(8))
        for j in range(3):
            dest = polyMixTubeList[i][j]
            for j in range(2):
                p300.aspirate(mmixVol/2, polyMix)  # 18*16*1.1 = 316.8/2 = 158.4
                p300.dispense(mmixVol/2, dest.bottom(2+6*j))
        p300.drop_tip()

    # 1.2 Two primers are added to generate 6 mmixes
    for m, (primers, nMConc) in enumerate(zip(primersList, primersConc)):
        p20.pick_up_tip()
        volume = 20*(nMConc/1000)/100*(16*1.1)*2 # amount F primer in mmix * 2 for 2 mixes + 4 as a bolus
        p20.aspirate(volume+2, primers[0]) # F primer with 2 ul bolus
        p20.dispense(volume/2, polyMixTubeList[0][m]) # dispense in mmixOneAssayOne and mmixTwoAssayOne
        p20.dispense(volume/2, polyMixTubeList[1][m])
        p20.drop_tip()
        p20.pick_up_tip()
        volume = 20*(nMConc/1000)/100*(16*1.1)*2 # amount F primer in mmix * 2 for 2 mixes + 4 as a bolus
        p20.aspirate(volume+2, primers[1]) # F primer with 2 ul bolus
        p20.dispense(volume/2, polyMixTubeList[0][m]) # dispense in mmixOneAssayOne and mmixTwoAssayOne
        p20.dispense(volume/2, polyMixTubeList[1][m])
        p20.drop_tip()
        # print (m, primers)

    # for i, polyMix in enumerate(polyMixList):
    #     for j in range(0,6):
    #         if j == 0 or j==3:
    #             p300.pick_up_tip()
    #             p20.pick_up_tip()
    #             p300.mix(3, 200, polyMix.bottom(8))
    #         # else:
    #         #     continue
    #         dest = polyMixTubeList[j]
    #         for k in range(2):
    #             p300.aspirate(18*16*1.1/2, polyMix)  # 18*16*1.1 = 316.8/2 = 158.4
    #             p300.dispense(18*16*1.1/2, dest.bottom(2+6*k))
    #         if j == 2 or j==5:
    #             p300.drop_tip()
    #             p20.drop_tip()
    #         # else:
    #         #     continue
    

    #  for mmix in mixList:
        # mmixH = tip_heights(18*48*1.2,  )

    # # Mix, pipette mastermix containing probe to each well on plate
    # mmixH = multiwell_mix * len(mixOne_wells)*1.1 # 18*4*(1+0.125) = 81 *8 = 648 + 1.1 = 712.8
    # for mmix, wwell in zip(mixList, wellList): # iterate through mastermixes and well list per mix
    #     p300.pick_up_tip()
    #     p300.mix(3, 200, mmix.bottom(10)) #first height
    #     for wellLoc, h in zip(wwell, tip_heights(mmixH, len(std_wells), multiwell_mix)): # iterate through wells and heights for each mix
    #         p300.aspirate(multiwell_mix, mmix.bottom(h), rate=0.75) # 15 * 4 (1.125)= 67.5
    #         protocol.delay(seconds=2) #tip equilibrate
    #         p300.move_to(mmix.bottom(35)) # excess tip fluid condense
    #         protocol.delay(seconds=2) #tip droplets slide
    #         p300.move_to(mmix.bottom(h)) # excess tip fluid condense
    #         p300.touch_tip(v_offset=-4) #touch 4 mm below surface
    #         for volD, heightD in d_dispense(multiwell_mix, 6, 6):
    #             p300.dispense(volD, stds_plate[wellLoc].bottom(heightD))
    #         # p300.dispense(multiwell_mix, stds_plate[well])
    #         p300.blow_out(stds_plate[wellLoc].bottom(12))
    #         p300.move_to(stds_plate[wellLoc].bottom(2))
    #         p300.touch_tip()
    #     p300.drop_tip()

    # # # add pos control stds to into plate wells and dispense into neighboring wells
    # for mmix, wwell in zip(mixList, wellList): # iterate through mastermixes and well list per mix for pos control addition and dispense
    #     for i in range(len(std_wells)): #loop 13x, water tube last
    #         p20.pick_up_tip()
    #         p300.pick_up_tip() #double barrel
    #         p20.aspirate(multisample_mix, std_wells[i].bottom(4)) #aspirate 22.5ul from template into mix well
    #         p20.move_to(std_wells[i].bottom(30))
    #         protocol.delay(seconds=3) #coalescing step
    #         p20.move_to(std_wells[i].bottom(18)) # remove fluid from tip
    #         p20.dispense(multisample_mix, stds_plate[wwell[i]].bottom(2))
    #         p20.mix(4, 10, stds_plate[wwell[i]].bottom(1), rate=0.5) # can't be mixed homogenously with p20 #ivetried
    #         p20.move_to(stds_plate[wwell[i]].bottom(12)) #above mmix solution
    #         protocol.delay(seconds=2) #outside fluid coalesce
    #         p20.blow_out(stds_plate[wwell[i]].bottom(12))
    #         p20.move_to(stds_plate[wwell[i]].bottom(2))
    #         p20.move_to(stds_plate[wwell[i]].bottom(30))  # above plate so tips don't crash Smoothie error?

    #         # mix with p300
    #         p300.move_to(stds_plate[wwell[i]].bottom(30)) # above plate so tips don't crash Smoothie error?
    #         p300.mix(3, 60, stds_plate[wwell[i]].bottom(3)) # mix 90ul mmix with dna
    #         p300.blow_out(stds_plate[wwell[i]].bottom(12))
    #         protocol.delay(seconds=1)
    #         p300.touch_tip(stds_plate[wwell[i]], v_offset=-2, speed=20)
    #         p300.move_to(stds_plate[wwell[i]].bottom(30))
    #         # transfer to adjacent wells
    #         for x in range(1,5): # need int 1, 2, 3 and 4.
    #             p20.move_to(stds_plate[wwell[i]].bottom(30))
    #             p20.aspirate(20, stds_plate[wwell[i]].bottom(1), rate=0.75) # asp from 54ul, dispense to neighbor well
    #             protocol.delay(seconds=2) #equilibrate
    #             # find digits in well, A1 and A10 and puts into list
    #             findNums = [int(i) for i in wwell[i].split()[0] if i.isdigit()]
    #             # joins nums from list [1, 0] -> 10 type = string
    #             colNum = ''.join(map(str, findNums))
    #             # this finds row
    #             row = wwell[i].split()[0][0]
    #             # put it all together into a destination well
    #             dest = row+str(int(colNum)+x) # row + neighbor well i.e. 1, 2
    #             p20.dispense(20, stds_plate[dest].bottom(1), rate=0.75)
    #             p20.touch_tip()
    #         p300.drop_tip()
    #         p20.drop_tip()