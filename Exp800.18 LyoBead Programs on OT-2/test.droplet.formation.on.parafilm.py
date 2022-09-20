# imports
from opentrons import protocol_api

# metadata
metadata = {
    'protocolName': 'Droplet Formation on Parafilm.',
    'author': 'Harley King <harley.king@luminultra.com>',
    'description': 'Tests droplet volume dispenses on parafilm on temp module.',
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
    pos_rack = protocol.load_labware('vwr_24_tuberack_1500ul', '2')
    mix_rack = protocol.load_labware('opentrons_10_tuberack_nest_4x50ml_6x15ml_conical', '3')
    tiprack300 = protocol.load_labware('opentrons_96_filtertiprack_200ul', '8')
    tiprack20 = protocol.load_labware('opentrons_96_filtertiprack_20ul', '9')
    tempdeck = protocol.load_module('tempdeck', '1') # have this so I don't have to move it off
    plate = tempdeck.load_labware('abi_96_wellplate_250ul') # not a plate; parafilm
    
    # PIPETTES
    p300 = protocol.load_instrument(
        'p300_single_gen2', 'left', tip_racks=[tiprack300]
    )
    p20 = protocol.load_instrument(
        'p20_single_gen2', 'right', tip_racks=[tiprack20]
    )
     
    # REAGENTS 
    # water rack
    mmix = mix_rack['A3'] # 20mL water in 50mL conical tube, 900*15 = 13500ul: 300*5 = 1500ul = 15mL
    # Positive Control Rack 
    empty_tube = pos_rack['A1'] # empty tube. The droplet forms above this tube. Need this tube to easily program heights.
    rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
    dispVolList = [14.8, 14.9, 15.0, 15.2, 15.4, 15.6, 15.8, 16.0]
    #### COMMANDS ######
    # turn on robot rail lights
    protocol.set_rail_lights(True)

    p300.pick_up_tip()
    # prewetting step for tip
    mmixH = fifty_ml_heights(17500, 20, 200) 
    p300.mix(3, 200, mmix.bottom(mmixH[0]))
    for h, (row, vol) in enumerate(zip(rows, dispVolList)):
        p300.aspirate(200, mmix.bottom(mmixH[h]))
        p300.move_to(mmix.bottom(mmixH[h]+20))
        p300.dispense(10, mmix.bottom(mmixH[h]+20)) # dispense 10ul to improve volume accuracy
        protocol.delay(seconds=3) # tip for drops to coalesce
        p300.move_to(mmix.bottom(mmixH[h])) # touch tip to remove droplets
        for dispNo in range (10): # how many dispenses? 
            dest = row+str(dispNo+1)
            p300.dispense(vol, plate[dest].bottom(20), rate = 0.1) # want height to above parafilm, but not too high
            p300.move_to(plate[dest].bottom(21))
            p300.move_to(plate[dest].bottom(20))
        p300.move_to(empty_tube.center())
        p300.dispense((190-10*dispNo), empty_tube.center())
        p300.blow_out()
        p300.touch_tip(empty_tube, v_offset=-0.3)
    p300.drop_tip()

    # repeat with P20
    # p20.aspirate(20, mmix.bottom(mmixH[0]))
    # p20.move_to(empty_tube.bottom(70))
    # for r in range(10): #
    #     modRate = r/10 # dispense rate needs to be decimal 0..1
    #     print ("Dispensing 20ul at rate = ", r, "%")
    #     p20.dispense(20, empty_tube.bottom(70), rate = modRate)
    # p20.drop_tip()
    
    # turn off robot rail lights
    # protocol.set_rail_lights(False)