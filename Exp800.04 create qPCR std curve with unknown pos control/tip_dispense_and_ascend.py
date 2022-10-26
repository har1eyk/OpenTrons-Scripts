# imports
from opentrons import protocol_api

# metadata
metadata = {
    'protocolName': 'Can a tip dispense and ascend?',
    'author': 'Harley King <harley.king@luminultra.com>',
    'description': 'Testing whether a OT-2 tip can ascend while dispensing.',
    'apiLevel': '2.12'
}
##########################
# functions
# calculates ideal tip height for entering liquid
def d_dispense(vol:int, steps:int, height:float):
    # what is the height of total volume?
    lowestHeight = 1 # don't go lower than this
    heightIncrement = (height-lowestHeight)/steps
    heightList = list(range(1,steps)) # make a list from 1..steps
    heightArray =[1] + [1+x*heightIncrement for x in heightList]
    volArray = [vol/steps]*steps
    return zip(volArray, heightArray)

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
    fuge_rack = protocol.load_labware('vwr_24_tuberack_1500ul', '1')
    # mix_rack = protocol.load_labware('vwr_24_tuberack_1500ul', '2')
    tiprack300 = protocol.load_labware('opentrons_96_filtertiprack_200ul', '8')
    # tiprack20 = protocol.load_labware('opentrons_96_filtertiprack_20ul', '9')
    tempdeck = protocol.load_module('tempdeck', '10')
    stds_plate = tempdeck.load_labware('abi_96_wellplate_250ul')
    
    # PIPETTES
    p300 = protocol.load_instrument(
        'p300_single_gen2', 'left', tip_racks=[tiprack300]
    )
    # p20 = protocol.load_instrument(
    #     'p20_single_gen2', 'right', tip_racks=[tiprack20]
    # )
     
    # REAGENTS 
    mix = fuge_rack['D5']
    testTube = fuge_rack['D1']
    # testTube = fuge_rack['D1']

    # COMMANDS
    p300.pick_up_tip()
    p300.aspirate(200, mix.bottom(10))
    for volD, heightD in d_dispense(200, 10, 12):
        p300.dispense(volD, testTube.bottom(heightD))
    p300.drop_tip()