# imports
from opentrons import protocol_api

# metadata
metadata = {
    'protocolName': 'Test Tip Heights with 50mL Conical Tube.',
    'author': 'Harley King <harley.king@luminultra.com>',
    'description': 'Does the 50mL function work correctly for pipette non-submergence?',
    'apiLevel': '2.11'
}


def tip_heights(init_vol, steps, vol_dec):
    vols = []
    heights = []
    # these values originate from Excel spreadsheet "Exp803..."
    p0 = 0.029502064
    p1 = 0.084625954
    p2 = -0.000174864
    p3 = 2.18373E-07
    p4 = -1.30599E-10
    p5 = 2.97839E-14
    if init_vol > 1499:
        offset = 14  # model out of range; see sheet
    else:
        offset = 7  # mm Need to add offset to ensure tip reaches below liquid level
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

def fifty_ml_heights(init_vol, steps, vol_dec):
    vols = []
    heights = []
    # these values originate from Excel spreadsheet "Exp803..."
    b = 0
    m = 0.0024
    if init_vol > 51000:
        offset = 14  # model out of range; see sheet
    else:
        offset = 15  # mm Need to add offset to ensure tip reaches below liquid level
    for i in range(steps):
        x = init_vol-vol_dec*i
        vols.append(x)
        h = m*x+b
        h = h-offset
        if h < 17.5:  # If less than 5mL remain in 50mL tube, go to bottom for asp
            h = 2
            heights.append(h)
        else:
            heights.append(round(h, 1))
    return heights

##########################


def run(protocol: protocol_api.ProtocolContext):

    # LABWARE
    tiprack300 = protocol.load_labware('opentrons_96_filtertiprack_200ul', '8')
    tempdeck = protocol.load_module('tempdeck', '10')
    reagent_rack = protocol.load_labware(
        'opentrons_6_tuberack_nest_50ml_conical', '2')

    # PIPETTES
    p300 = protocol.load_instrument(
        'p300_single_gen2', 'left', tip_racks=[tiprack300]
    )
    # REAGENTS
    rows_on_plate = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']

    # ##### COMMANDS #####
    fifty_h=fifty_ml_heights(32400, 100, 200)
    print (fifty_h)
    p300.pick_up_tip()
    for i in range(100):
        # print ("aspirating height:", fifty_h[i])
        p300.aspirate(200, reagent_rack['A1'].bottom(fifty_h[i]))
        p300.dispense(200, reagent_rack['B3'].bottom(fifty_h[-i]))
        # print ("dispense height:", fifty_h[-i])
    p300.drop_tip()