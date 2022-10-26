# imports
from opentrons import protocol_api

# metadata
metadata = {
    'protocolName': 'Test 5mL Eppendorf tube on 15x15mL rack',
    'author': 'Harley King <harley.king@luminultra.com>',
    'description': 'Does 5mL definition exist?',
    'apiLevel': '2.12'
}
##########################
# functions
# calculates ideal tip height for entering liquid


def run(protocol: protocol_api.ProtocolContext):

    # LABWARE
    # epp_rack = protocol.load_labware('opentrons_24_tuberack_eppendorf_2ml_safelock_snapcap', '5')
    tiprack300 = protocol.load_labware('opentrons_96_filtertiprack_200ul', '8')
    # tiprack20 = protocol.load_labware('opentrons_96_filtertiprack_20ul', '9')
    # tempdeck = protocol.load_module('tempdeck', '10') # leaving on so I don't have to move off 
    # plate = protocol.load_labware('corning_96_wellplate_360ul_flat', '3')
    # reagent_rack = protocol.load_labware('opentrons_6_tuberack_nest_50ml_conical', '6')
    # lurb_rack= protocol.load_labware('opentrons_15_tuberack_nest_15ml_conical', '2')
    lurb_rack= protocol.load_labware('eppendorf5ml_15_tuberack_5000ul', '2')
    # x3_rack= protocol.load_labware('opentrons_15_tuberack_nest_15ml_conical', '6')

    # PIPETTES
    p300 = protocol.load_instrument(
        'p300_single_gen2', 'left', tip_racks=[tiprack300]
    )
     
    # REAGENTS
    # x3 = x3_rack['A1'] # detergent e.g. Ultralyse 7, Ultralyse X3; 8085.11ul
    lurbOne = lurb_rack['A1'] # lurb 1; 15mL tube

    ### COMMANDS ######   
    p300.pick_up_tip()
    p300.move_to(lurbOne.top())
    protocol.delay(seconds=5)
    p300.move_to(lurbOne.top(-5))
    protocol.delay(seconds=5)
    p300.move_to(lurbOne.top(-10))
    protocol.delay(seconds=5)
    p300.move_to(lurbOne.bottom(10))
    protocol.delay(seconds=5)
    p300.move_to(lurbOne.bottom(1))
    protocol.delay(seconds=5)
   
   #test success 20220325_hjk
