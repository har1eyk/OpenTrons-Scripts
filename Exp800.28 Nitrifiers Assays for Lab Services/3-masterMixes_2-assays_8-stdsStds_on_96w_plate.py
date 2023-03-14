# imports
from opentrons import protocol_api

# metadata
metadata = {
    'protocolName': 'Compare Three MasterMixes with Two Assays and Eight Standards in 96w Plate',
    'author': 'Harley King <harley.king@luminultra.com>',
    'description': '18ul mix is dispensed with 2ul stds from two mastermixes in two assays using eight standards. Which mmix is better?',
    'apiLevel': '2.13'
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
        if h < 3: # prevent negative heights; go to bottom to avoid air aspirant above certain height
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
    # stdsThree_rack = protocol.load_labware('vwr_24_tuberack_1500ul', '6')
    tiprack300 = protocol.load_labware('opentrons_96_filtertiprack_200ul', '8')
    tiprack20 = protocol.load_labware('opentrons_96_filtertiprack_20ul', '9')
    tempdeck = protocol.load_module('tempdeck', '10')
    plate = tempdeck.load_labware('bioer_96_aluminumblock_200ul')

    # PIPETTES
    p300 = protocol.load_instrument(
        'p300_single_gen2', 'left', tip_racks=[tiprack300]
    )
    p20 = protocol.load_instrument(
        'p20_single_gen2', 'right', tip_racks=[tiprack20]
    )

    # mix_rack
    polyMixOne = mix_rack['A1'] # 18*32*(1.2) = 691.2 µl, should not include primers
    polyMixTwo = mix_rack['A3'] # 691.2ul
    polyMixThree = mix_rack['A6'] # 691.2ul
    
    mmixOneAssayOne=mix_rack['B1'] # empty tube but will hold 18*16*1.1 = 316.8ul
    mmixOneAssayTwo=mix_rack['C1'] # empty
    
    mmixTwoAssayOne=mix_rack['B3'] # empty
    mmixTwoAssayTwo=mix_rack['C3'] # empty

    mmixThreeAssayOne=mix_rack['B6'] # empty
    mmixThreeAssayTwo=mix_rack['C6'] # empty
    
    # primer_rack
    FOligoAssayOne=primers_rack['A1']
    ROligoAssayOne=primers_rack['A2']
    FOligoAssayTwo=primers_rack['B1']
    ROligoAssayTwo=primers_rack['B2']

    # stds racks
    stdOne_1 = stdsOne_rack['A1'] # diluted standard
    stdOne_2 = stdsOne_rack['A2']
    stdOne_3 = stdsOne_rack['A3']
    stdOne_4 = stdsOne_rack['A4']
    stdOne_5 = stdsOne_rack['A5']
    stdOne_6 = stdsOne_rack['A6'] 
    stdOne_7 = stdsOne_rack['B1']
    stdOne_8 = stdsOne_rack['B2']
    
    stdTwo_1 = stdsTwo_rack['A1'] # diluted standard
    stdTwo_2 = stdsTwo_rack['A2']
    stdTwo_3 = stdsTwo_rack['A3']
    stdTwo_4 = stdsTwo_rack['A4']
    stdTwo_5 = stdsTwo_rack['A5']
    stdTwo_6 = stdsTwo_rack['A6'] 
    stdTwo_7 = stdsTwo_rack['B1']
    stdTwo_8 = stdsTwo_rack['B2']

    # CALCS
    mix_per_well = 18 #how much volume (ul) mastermix should be in each well?
    sample_per_well = 2

    # LISTS
    polyMixTubeListOne = [mmixOneAssayOne, mmixOneAssayTwo]
    polyMixTubeListTwo = [ mmixTwoAssayOne, mmixTwoAssayTwo]
    polyMixTubeListThree = [ mmixThreeAssayOne, mmixThreeAssayTwo]
    polyMixTubeList = [polyMixTubeListOne, polyMixTubeListTwo, polyMixTubeListThree]
    polyMixList = [polyMixOne, polyMixTwo, polyMixThree]
    mmixVol = 18*16*1.125 # 316.8ul, the number of wells per assay per mastermix with 10% overage
    primersList = [[FOligoAssayOne,ROligoAssayOne], [FOligoAssayTwo,ROligoAssayTwo]]
    assayOnePrimerConc = 300 # what is the conc in nM of F, R primers?
    assayTwoPrimerConc = 300 
    primersConc = [assayOnePrimerConc, assayTwoPrimerConc]
    oneStds = [stdOne_1, stdOne_2, stdOne_3, stdOne_4, stdOne_5, stdOne_6, stdOne_7, stdOne_8]
    twoStds = [stdTwo_1, stdTwo_2, stdTwo_3, stdTwo_4, stdTwo_5, stdTwo_6, stdTwo_7, stdTwo_8]
    allStds = [oneStds, twoStds]
    rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
    
    #### COMMANDS ######
    # PROGRAM OUTLINE #
    # 1.1 Each of 2 polymerase mixes is subdivided into 3 tubes. 
    # 1.2 Two primers are added to generate 6 mmixes
    # 1.3 mix and aliquot 36 and 4ul to wells
    # 1.3 dispense, mix and add to next well. 

    # 1.1 Each of 2 polymerase mixes is subdivided into 3 tubes. 
    for i, polyMix in enumerate(polyMixList): #three polymerase mixes
        p300.pick_up_tip()
        p300.mix(3, 200, polyMix.bottom(4))
        for j in range(2):
            dest = polyMixTubeList[i][j] # i = 3, len(polyMixList), j = 2, # of tubes
            for j in range(2):
                p300.aspirate(mmixVol/2, polyMix.bottom(2), rate=0.6)  # 18*16*1.125 = 316.8/2 = 158.4
                p300.move_to(polyMix.top(-3))
                protocol.delay(seconds=2)
                p300.touch_tip(polyMix, v_offset=-3, speed=40)
                p300.dispense(mmixVol/2, dest.bottom(2+6*j))
        p300.drop_tip()

    # 1.2 Two primers are added to generate 6 mmixes
    # the primers are the IDT tubes. Tip doesn't reach bottom, may need some exploring here if liquid level becomes low, or move to 1.5mL tubes? 230215 hjk
    for m, (primers, nMConc) in enumerate(zip(primersList, primersConc)): # 2 sets of primers
        p20.pick_up_tip()
        
        volume = 20*(nMConc/1000)/100*(16*1.125)*3 # amount F primer in mmix * 3 for 3 mixes 
        p20.aspirate(volume+2, primers[0].bottom(1)) # F primer with 2 ul bolus
        p20.dispense(volume/3, polyMixTubeList[0][m].bottom(4)) # dispense in mmixOneAssayOne and mmixTwoAssayOne, mmixThreeAssayOne
        p20.dispense(volume/3, polyMixTubeList[1][m].bottom(4)) # dispense in middle of volume
        p20.dispense(volume/3, polyMixTubeList[2][m].bottom(4))
        p20.drop_tip()
        p20.pick_up_tip()
        volume = 20*(nMConc/1000)/100*(16*1.125)*3 # amount F primer in mmix * 2 for 2 mixes + 4 as a bolus
        p20.aspirate(volume+2, primers[1].bottom(1)) # F primer with 2 ul bolus
        p20.dispense(volume/3, polyMixTubeList[0][m].bottom(4)) # dispense in mmixOneAssayOne and mmixTwoAssayOne
        p20.dispense(volume/3, polyMixTubeList[1][m].bottom(4))
        p20.dispense(volume/3, polyMixTubeList[2][m].bottom(4))
        p20.drop_tip()
    
    # 1.3 Mix and aliquot to wells
    for q, mmixTubes in enumerate(polyMixTubeList): # 3 mastermix types
        for r, mmixTube in enumerate(mmixTubes): # 2 mastermix assay tubes
            mmixH = tip_heights(18*16*1.125, 8, 36) # 316.8ul) #18*16*1.1 # 316.8ul
            print ("mmixH:", mmixH)
            for n in range(8):
                p300.pick_up_tip()
                p20.pick_up_tip()
                if n==0:
                    p300.mix(2, 200, mmixTube.bottom(4))
                    p300.mix(2, 200, mmixTube.bottom(6))
                    p300.mix(2, 200, mmixTube.bottom(8))
                p300.aspirate(36, mmixTube.bottom(mmixH[n]), rate=0.6)
                p20.aspirate(4, allStds[r][n].bottom(2))
                dest = plate[rows[n]+str(r+1+2*q+5*r)]
                p300.dispense(36, dest.bottom(3), rate=0.75)
                p20.dispense(4, dest.bottom(2))
                p20.mix(2, 4, dest.bottom(2))
                p300.mix(2, 35, dest.bottom(2))
                p300.blow_out(dest.bottom(5))
                p20.aspirate(20, dest.bottom(2))
                nextDisp = plate[rows[n]+str(r+1+2*q+5*r+1)] # adding to next column over.
                p20.dispense(20, nextDisp.bottom(2), rate=0.75)
                p20.blow_out(nextDisp.bottom(5))
                p300.drop_tip()
                p20.drop_tip()
