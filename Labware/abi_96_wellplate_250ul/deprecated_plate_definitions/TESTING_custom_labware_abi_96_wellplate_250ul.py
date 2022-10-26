# imports
from opentrons import protocol_api

# metadata
metadata = {
    'protocolName': 'Testing Custom Labware ABI Prism Plate 96w',
    'author': 'Harley King <harley.king@luminultra.com>',
    'description': 'Testing custom labware ABI 96w optical plate after adding as custom labware.',
    'apiLevel': '2.9'
}
##########################
def run(protocol: protocol_api.ProtocolContext):

    # LABWARE
    fuge_rack = protocol.load_labware('opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap', '4')
    tiprack300 = protocol.load_labware('opentrons_96_tiprack_300ul', '8')
    tiprack20 = protocol.load_labware('opentrons_96_tiprack_20ul', '9')
    tempdeck = protocol.load_module('tempdeck', '10')
    sample_plate = tempdeck.load_labware('abi_96_wellplate_250ul')

    # PIPETTES
    p300 = protocol.load_instrument(
        'p300_single_gen2', 'left', tip_racks=[tiprack300]
    )
    p20 = protocol.load_instrument(
        'p20_single_gen2', 'right', tip_racks=[tiprack20]
    )
     
    # REAGENTS
    water = fuge_rack['C1']

    ###### COMMANDS ######
    # dispense 20ul into A1, checking bottom clearance
    p20.pick_up_tip()
    p20.well_bottom_clearance.aspirate = 2
    p20.aspirate(20, water)
    p20.well_bottom_clearance.dispense = 3
    p20.dispense(20, sample_plate['A1'])
    p20.drop_tip()

    # dispense 20ul into B1 using 300ul tip, checking bottom clearance
    p300.pick_up_tip()
    p300.well_bottom_clearance.aspirate = 2
    p300.aspirate(20, water)
    p300.well_bottom_clearance.dispense = 0
    p300.dispense(20, sample_plate['B1'])
    p300.drop_tip()

    # dispense 20ul into each well in row A
    col = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']
    p300.pick_up_tip()
    p300.well_bottom_clearance.aspirate = 2
    p300.aspirate(260, water)
    for well in col:
        pos = 'A'+ well
        p300.well_bottom_clearance.dispense = 0
        p300.dispense(20, sample_plate[pos])
        p300.touch_tip()
    p300.drop_tip()
