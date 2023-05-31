# imports
from re import I
from opentrons import protocol_api

# metadata
metadata = {
    'protocolName': 'Distribute 20ul Water Each Well in 96w Plate.',
    'author': 'Harley King <harley.king@luminultra.com>',
    'description': 'Resuspending lyophilized pellet in 96w plate with 20ul water.',
    'apiLevel': '2.13'
}

##########################
# Calc heights for 50mL conical tubes
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

def run(protocol: protocol_api.ProtocolContext):

    # EXPERIMENT OUTLINE
    # This experiment tests if dextran concentrations in the LyoReady Mastermix affects the qPCR results.
    # Dextran is in 50mL tube
    # LyoReady mastermix (or other) are added to 12, 1.5mL tubes chilled in temp module. EAch column is a concentration of Dextran. 12 different concentrations.
    # To these tubes dextran and water are added, mixed and aliquoted to PCR plate.

    # LABWARE
    tiprack300 = protocol.load_labware('opentrons_96_filtertiprack_200ul', '8')
    # tiprack20 = protocol.load_labware('opentrons_96_filtertiprack_20ul', '9')
    
    tempdeck = protocol.load_module('tempdeck', '1')
    plate = tempdeck.load_labware('bioer_96_aluminumblock_200ul')
    
    # alumBlock = protocol.load_labware('opentrons_24_tuberack_nest_1.5ml_snapcap', '2')
    water_rack = protocol.load_labware('opentrons_10_tuberack_nest_4x50ml_6x15ml_conical', '2')

    # reagent_rack = protocol.load_labware('opentrons_10_tuberack_nest_4x50ml_6x15ml_conical', '2')

    # PIPETTES
    p300 = protocol.load_instrument(
        'p300_single_gen2', 'left', tip_racks=[tiprack300]
    )
    
    # REAGENTS   
    
    water = water_rack['A3'] # 50mL tube with 30mL NFW water
    waste = water_rack['A1'] # 5mL empty eppendorf tube for waste. 
    
    # USER INPUT
    water_beg_vol = 30000 # water volume in ul

    # LISTS
    rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']

    # #### COMMANDS ######    
    # 1.1 Add 20ul NFW to each well in plate
    
    # 1.1 Add 20ul of water to each well in plate
    h_list = fifty_ml_heights(30000, 12, 180)
    p300.pick_up_tip()
    p300.mix(3, 200, water.bottom(h_list[0]))
    for col in range(12):
        p300.aspirate(8*20+20, water.bottom(h_list[col])) # 8*14*excess = 120.96ul
        for row in rows:
            dest = plate[row+str(col+1)]
            p300.dispense(20, dest.bottom(3))
        p300.dispense(20, waste.center())
        p300.blow_out()
        p300.touch_tip(waste, speed=50, v_offset=-5)
            
    p300.drop_tip()


    
