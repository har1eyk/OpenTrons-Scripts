# imports
from opentrons import protocol_api

# metadata
metadata = {
    'protocolName': 'Test new ABI 96w plate definition. HK 20220825.',
    'author': 'Harley King <harley.king@luminultra.com>',
    'description': 'Made a new plate definition. Want to test it.',
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
    # mix_rack = protocol.load_labware('vwr_24_tuberack_1500ul', '1')
    # fuge_rack = protocol.load_labware('vwr_24_tuberack_1500ul', '2')
    tiprack300 = protocol.load_labware('opentrons_96_filtertiprack_200ul', '8')
    tiprack20 = protocol.load_labware('opentrons_96_filtertiprack_20ul', '9')
    tempdeck = protocol.load_module('tempdeck', '1')
    stds_plate = tempdeck.load_labware('abi_96_wellplate_250ul')
    
    # PIPETTES
    p300 = protocol.load_instrument(
        'p300_single_gen2', 'left', tip_racks=[tiprack300]
    )
    p20 = protocol.load_instrument(
        'p20_single_gen2', 'right', tip_racks=[tiprack20]
    )
     
    
    # # add pos control stds to PROBE mmxs into plate wells and dispense into neighboring wells
    # for i in range(len()): #loop 13x, water tube last
    p20.pick_up_tip()
    p300.pick_up_tip() #double barrel
    p20.move_to(stds_plate['A1'].top())
    protocol.delay(seconds=2)
    p20.move_to(stds_plate['A1'].bottom(5))    
    protocol.delay(seconds=2)
    p20.move_to(stds_plate['A1'].bottom(1))    
    protocol.delay(seconds=10)
    p20.move_to(stds_plate['A1'].bottom(40))    
    p300.move_to(stds_plate['A1'].top())
    protocol.delay(seconds=2)
    p300.move_to(stds_plate['A1'].bottom(5))    
    protocol.delay(seconds=2)
    p300.move_to(stds_plate['A1'].bottom(1))    
    protocol.delay(seconds=10)
    p300.move_to(stds_plate['A1'].bottom(40))
    p300.drop_tip()
    p20.drop_tip()