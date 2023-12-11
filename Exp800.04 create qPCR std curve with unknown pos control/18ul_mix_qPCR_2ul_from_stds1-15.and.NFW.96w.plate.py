# imports
from opentrons import protocol_api

# metadata
metadata = {
    'protocolName': 'Add 18ul Mix and 2ul Sample from tubes 1-15 including NFW control.',
    'author': 'Harley King <harley.king@luminultra.com>',
    'description': 'Creates a 96w plate of 18ul of mastermix. Adds 2ul from a dilution series.',
    'apiLevel': '2.13'
}
##########################
# functions
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
        offset = 7 #mm Need to add offset to ensure tip reaches below liquid level
    for i in range(steps):
        x = init_vol-vol_dec*i
        vols.append(x)
        h = p5*x**5+p4*x**4+p3*x**3+p2*x**2+p1*x**1 + p0
        h = h-offset
        if h < 4: # prevent negative heights; go to bottom to avoid air aspirant above certain height
            h = 0        
            heights.append(h)
        else:
            heights.append(round(h, 1))
    return heights

def run(protocol: protocol_api.ProtocolContext):

    # LABWARE
    mix_rack = protocol.load_labware('eppendorf_24_tuberack_2000ul', '7')
    fuge_rack = protocol.load_labware('vwr_24_tuberack_1500ul', '2')
    # tiprack300 = protocol.load_labware('opentrons_96_filtertiprack_200ul', '8')
    tiprack20 = protocol.load_labware('opentrons_96_filtertiprack_20ul', '9')
    tempdeck = protocol.load_module('tempdeck', '10')
    # plate = tempdeck.load_labware('amplifyt_96_aluminumblock_300ul')
    plate = tempdeck.load_labware('bioer_96_aluminumblock_200ul')

    # PIPETTES
    # p300 = protocol.load_instrument(
    #     'p300_single_gen2', 'left', tip_racks=[tiprack300]
    # )
    p20 = protocol.load_instrument(
        'p20_single_gen2', 'right', tip_racks=[tiprack20]
    )
   # mix_rack
    mmix = mix_rack['D1'] # 96*18*1.2 = 2073.6 
    # WATER = mix_rack['A1'] # 1500ul WATER
       
    #fuge_rack
    std_1 = fuge_rack['A1'] # e.g. 0.625uM # empty
    std_2 = fuge_rack['A2'] # e.g. 1.25uM # empty
    std_3 = fuge_rack['A3'] # e.g. 2.5uM # empty
    std_4 = fuge_rack['A4'] # e.g. 5.0uM # empty
    std_5 = fuge_rack['A5'] # e.g. 7.5uM # empty
    std_6 = fuge_rack['A6'] # e.g. 10uM # empty
    std_7 = fuge_rack['B1'] # e.g. 10uM # empty
    std_8 = fuge_rack['B2'] # e.g. 10uM # empty
    std_9 = fuge_rack['B3'] # e.g. 0.625uM # empty
    std_10 = fuge_rack['B4'] # e.g. 1.25uM # empty
    std_11 = fuge_rack['B5'] # e.g. 2.5uM # empty
    std_12 = fuge_rack['B6'] # e.g. 5.0uM # empty
    std_13 = fuge_rack['C1'] # e.g. 7.5uM # empty
    std_14 = fuge_rack['C2'] # e.g. 10uM # empty
    std_15 = fuge_rack['C3'] # e.g. 10uM # empty
    nfw = fuge_rack['D6'] # e.g. 10uM # empty
    
    # user inputs
    rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
    samp_sources = [std_1, std_2, std_3, std_4, std_5, std_6, std_7, std_8, 
                    std_9, std_10, std_11, std_12, std_13, std_14, std_15, nfw]
    
    # ### COMMANDS ######
    # OVERVIEW
    # 1.1 add 18ul MMIX to 96 wells
    # 1.2 2ul added to every sample, row-by-row
    
    # 1.1 add 18ul MMIX to 96 wells
    p20.pick_up_tip()
    tubeH = tip_heightsEpp(2000, 96, 18) #shan't go higher than 2000ul 
    print ("tubeHeights:", tubeH)
    h_counter = 0
    p20.mix(2, 20, mmix.bottom(tubeH[h_counter]))
    for row in rows:
       for col in range(12):
           p20.aspirate(18, mmix.bottom(tubeH[h_counter]))
           protocol.delay(seconds=1) #equilibrate
           # p20.move_to(mmix.bottom(tubeH[h_counter]+10)) # suspend above mix; droplets coalesce
           p20.move_to(mmix.top(-4)) # suspend above mix; droplets coalesce
           protocol.delay(seconds=2)
           p20.touch_tip(v_offset=-4, speed=40)
           # p20.move_to(mmix.bottom(tubeH[h_counter])) # remove fluid my dipping in mix
           dest = row + str(col+1)
           p20.dispense(18, plate[dest].bottom(3))
           p20.blow_out(plate[dest].bottom(8))
           p20.move_to(plate[dest].bottom(3)) # remove traces of mmix
           h_counter +=1
    p20.drop_tip()
    
    # 1.2 2ul added to every sample, row-by-row
    source_counter = 0 # a counter to iterate through the source tubes
    for row in rows:
        for col in range(0,12,6):
            sample = samp_sources[source_counter] # this selects the source tube e.g. stds
            p20.pick_up_tip()
            p20.mix(2,20, sample.bottom(2)) # pre-wetting tip is more accurate
            p20.aspirate(16, sample.bottom(2))
            destOne = row + str(col+1)
            destTwo = row + str(col+2)
            destThree = row + str(col+3)
            destFour = row + str(col+4)
            destFive = row + str(col+5)
            destSix = row + str(col+6)
            p20.dispense(2, plate[destOne].bottom(2))
            p20.dispense(2, plate[destTwo].bottom(2))
            p20.dispense(2, plate[destThree].bottom(2))
            p20.dispense(2, plate[destFour].bottom(2))
            p20.dispense(2, plate[destFive].bottom(2))
            p20.dispense(2, plate[destSix].bottom(2))
            p20.drop_tip()
            source_counter +=1
