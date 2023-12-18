# imports
from opentrons import protocol_api

# metadata
metadata = {
    'protocolName': 'Make an qKit-Anda-Modified Extraction Plate for dPCR.',
    'author': 'Harley King <harley.king@luminultra.com>',
    'description': 'Uses qKit reagents to make a plate according to Anda modified specifications. This reduces the risk and incidence of contamination.',
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
        offset = 8 #mm Need to add offset to ensure tip reaches below liquid level
    for i in range(steps):
        x = init_vol-vol_dec*i
        vols.append(x)
        h = p5*x**5+p4*x**4+p3*x**3+p2*x**2+p1*x**1 + p0
        h = h-offset
        if h < 6: # prevent negative heights; go to bottom to avoid air aspirant above certain height
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
    # don't need this but keeping on deck so we don't have to move it off
    tempdeck = protocol.load_module('temperature module gen2', '10')
    # plate = tempdeck.load_labware('bioer_96_aluminumblock_200ul')

    tiprack300 = protocol.load_labware('opentrons_96_filtertiprack_200ul', '8')
    sampleRack = protocol.load_labware('vwr_24_tuberack_1500ul', '1')
    deepwell = protocol.load_labware('bioer_96_wellplate_2200ul', '2')
    reagents = protocol.load_labware('opentrons_10_tuberack_nest_4x50ml_6x15ml_conical', '3')
    mag_beads_rack = protocol.load_labware('vwr_24_tuberack_1500ul', '5')
    
    # PIPETTES
    p300 = protocol.load_instrument(
        'p300_single_gen2', 'left', tip_racks=[tiprack300]
    )
     
    # REAGENTS 
    binding_buffer= reagents['A3']
    wash_buffer_1 = reagents['A4']
    wash_buffer_2 = reagents['B3']
    elution_buffer = reagents['B4']
    mag_beads = mag_beads_rack['D1']


    # USER INPUTS
    numColumnSet = 1 # How many columns sets to prepare on a plate. 1 column set = columns 1-6.
    salmonDnaVol = 1 # (ul)
    binding_bufferVol = 900 #(ul)
    wash_buffer_1Vol = 900
    wash_buffer_2Vol = 900
    mag_beadVol = 25
    elution_buffer = 100
    rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
    
    #### COMMANDS ######
    # turn on robot rail lights
    protocol.set_rail_lights(True) # turn on lights if not on

    # add elution_buffer to column 2 and column 3

    # add wash_buffer_1 to column 4

    # add wash_buffer_2 to column 5 and 6

    # add 25ul concentrated magnetic beads to column 2 and column 3

    # add 1ul Salmon DNA to column 2 and column 3


    

 