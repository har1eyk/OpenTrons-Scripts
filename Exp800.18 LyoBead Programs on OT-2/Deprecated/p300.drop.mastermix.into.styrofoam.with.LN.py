# imports
from opentrons import protocol_api

# metadata
metadata = {
    'protocolName': 'LyoBead Creation on OT-2 in Styrofoam Container with LN.',
    'author': 'Harley King <harley.king@luminultra.com>',
    'description': 'Drops 15.8ul mastermix dispenses into Syrofoam container.',
    'apiLevel': '2.12'
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
# Calc heights for 50mL conical tubes
def fifty_ml_heights(init_vol, steps, vol_dec):
    vols = []
    heights = []
    # these values originate from Excel spreadsheet "Exp803..."
    b = 0
    m = 0.0024
    if init_vol > 51000:
        offset = 12  # model out of range; see sheet
    else:
        offset = 5  # mm Need to add offset to ensure tip reaches below liquid level
    for i in range(steps):
        x = init_vol-vol_dec*i
        vols.append(x)
        h = m*x+b
        h = h-offset
        if h < 12:  # If less than 5mL remain in 50mL tube, go to bottom for asp
            h = 3
            heights.append(h)
        else:
            heights.append(round(h, 1))
    return heights

def run(protocol: protocol_api.ProtocolContext):

    # LABWARE
    mix_rack = protocol.load_labware('opentrons_10_tuberack_nest_4x50ml_6x15ml_conical', '11') # keep this out of way of styrofoam container
    tiprack300 = protocol.load_labware('opentrons_96_filtertiprack_200ul', '9')
    tempdeck = protocol.load_module('tempdeck', '10') # have this so I don't have to move it off
    alumBlock = tempdeck.load_labware('opentrons_24_aluminumblock_generic_2ml_screwcap')
    # alumBlock = tempdeck.load_labware('opentrons_24_aluminumblock_nest_1.5ml_screwcap')
    # styrofoam container as position 4, 5, 1 and 2. This container overlaps these positions. 
    # cont_pos1 = protocol.load_labware('vwr_24_tuberack_1500ul', '1')
    # cont_pos2 = protocol.load_labware('vwr_24_tuberack_1500ul', '2')
    # cont_pos4 = protocol.load_labware('vwr_24_tuberack_1500ul', '4')
    # cont_pos5 = protocol.load_labware('vwr_24_tuberack_1500ul', '5')
    paraFilm = protocol.load_module('opentrons_96_aluminumblock_generic_pcr_strip_200ul', '3')
    
    # PIPETTES
    p300 = protocol.load_instrument(
        'p300_single_gen2', 'left', tip_racks=[tiprack300]
    )
     
    # REAGENTS 
    # mastermix rack
    # mmix = mix_rack['A3'] # 20mL water in 50mL conical tube, 900*15 = 13500ul: 300*5 = 1500ul = 15mL
    mmix = alumBlock['A1'] # if in 2mL tube, what position on aluminum block
    mmixVol = 1500 # if in 2mL tube, how much mastermix volume
    dispVol = 14.8
    totalLyoBeadCount = mmixVol // dispVol -2 # leave a little mmix in the tube as waste; don't want incomplete aliquot
    
    if totalLyoBeadCount % 8 == 0: # if divides evenly
        totalPipetteRefills = totalLyoBeadCount/8 # how many times does 200ul tip need to refill to complete run?
    else:
        totalPipetteRefills = totalLyoBeadCount // 8 # the // operator gives integer

    # relative dropping positions into tuberacks beginning from position 1->2->4->5
    # dispPos = [cont_pos1['C2'], cont_pos2['C4'], cont_pos5['B4'], cont_pos4['B2']] # dispense in anti-clockwise positions
    rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
    # dispPos = [paraFilmcont_pos1['C2'], cont_pos2['C4'], cont_pos5['B4'], cont_pos4['B2']] # dispense in anti-clockwise positions
    print (totalLyoBeadCount, totalPipetteRefills)

    #### COMMANDS ######
    # turn on robot rail lights
    protocol.set_rail_lights(True) # turn on lights if not on

    p300.pick_up_tip()
    contH = 109 # how many mm above tuberack height is the container height? 110mm is max.
    # mmixH = fifty_ml_heights(17500, 20, 200) 
    mmixH = tip_heights(mmixVol, int(totalPipetteRefills), dispVol*10) #mix volume, total steps = totalPipetteRefills in dispVol*10 pipette volume  
    # prewetting step for tip
    p300.mix(3, 200, mmix.bottom(mmixH[0])) #only need 9 dispenses at this volume: 1 is for burn, next 8 drop in container, last is for accuracy.
    for i in range(int(totalPipetteRefills)):  
        p300.aspirate(dispVol*10, mmix.bottom(mmixH[i]))
        p300.move_to(mmix.bottom(mmixH[i]+20))
        p300.dispense(dispVol, mmix.bottom(mmixH[i]+20)) # dispense dispVol to improve volume accuracy in subsequent dispenses
        protocol.delay(seconds=4) # tip for drops to coalesce
        p300.move_to(mmix.bottom(mmixH[i])) # touch tip to remove droplets
        for _ in range(1): # two loops because 8 dispenses
            for dispNo in range(4): # how many dispenses? (200-dispVol (15.8)= 184.2/15.8 = 11 )
                dest = paraFilm[]
                p300.move_to(dest.bottom(contH)) # move to destination and pause for a few seconds to remove lateral motion
                protocol.delay(seconds=2)
                p300.dispense(dispVol, dest.bottom(contH), rate = 0.08) # want height to above parafilm, but not too high
                p300.move_to(dest.bottom(contH+1))
                p300.move_to(dest.bottom(contH))
        p300.move_to(mmix.bottom(mmixH[i]+10)) # drop waste mix back into tube
        p300.dispense((200-9*dispVol-4*dispVol), mmix.bottom(mmixH[i]+10))
        p300.blow_out(mmix.bottom(mmixH[i]+4))
        p300.move_to(mmix.bottom(mmixH[i])) # touch tip to fluid to remove residual mmix on tubes
    p300.drop_tip()

    