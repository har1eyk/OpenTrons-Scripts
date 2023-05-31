# imports
from opentrons import protocol_api

# metadata
metadata = {
    'protocolName': 'Add 18ul Mix and 2ul Sample to Test LOD Using Opt Fwd and Rev and Prove Concentrations. No std curve.',
    'author': 'Harley King <harley.king@luminultra.com>',
    'description': 'Creates a 96w plate of optimal primer and probe concentrations to qPCR samples. No std curve is created.',
    'apiLevel': '2.14'
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
        offset = 11 #mm Need to add offset to ensure tip reaches below liquid level
    for i in range(steps):
        x = init_vol-vol_dec*i
        vols.append(x)
        h = p5*x**5+p4*x**4+p3*x**3+p2*x**2+p1*x**1 + p0
        h = h-offset
        if h < 8: # prevent negative heights; go to bottom to avoid air aspirant above certain height
            h = 0        
            heights.append(h)
        else:
            heights.append(round(h, 1))
    return heights

#
    n =1
    if tot/n > max_vol: # if total greater than max
       while tot/n > max_vol: # increment n until some tot/n < max_vol
            n+=1
            if tot/n == max_vol: # if tot evently divided e.g. 1000
                subvol = tot/n
                return [subvol]*n
            if tot/(n+1) < max_vol: # if tot <> evenly divided e.g. 417.3
                subvol = tot/(n+1)
                return [subvol]*(n+1) # return # aspiration steps
    else: # if total less than max
        return [tot/n]

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
    samp_1 = fuge_rack['B1'] # e.g. 0.625uM # empty
    samp_2 = fuge_rack['B1'] # e.g. 1.25uM # empty
    samp_3 = fuge_rack['B1'] # e.g. 2.5uM # empty
    samp_4 = fuge_rack['B1'] # e.g. 5.0uM # empty
    samp_5 = fuge_rack['B2'] # e.g. 7.5uM # empty
    samp_6 = fuge_rack['B2'] # e.g. 10uM # empty
    samp_7 = fuge_rack['B2'] # e.g. 10uM # empty
    samp_8 = fuge_rack['B2'] # e.g. 10uM # empty
    
    # user inputs
    rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
    samp_sources = [samp_1, samp_2, samp_3, samp_4, samp_5, samp_6, samp_7, samp_8]
    
    # ### COMMANDS ######
    # OVERVIEW
    # 1.1 add 18ul MMIX to 96 wells
    # 1.2 2ul added to every sample, row-by-row
    
    # 1.1 add 18ul MMIX to 96 wells
    p20.pick_up_tip()
    tubeH = tip_heightsEpp(1800, 96, 18)
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
    for sample, row in zip(samp_sources, rows):
        for col in range(0,12,6):
            p20.pick_up_tip()
            p20.mix(1,20, sample.bottom(2)) # pre-wetting tip is more accurate
            p20.aspirate(18, sample.bottom(2))
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
