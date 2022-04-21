# imports
from opentrons import protocol_api

# metadata
metadata = {
    'protocolName': 'Move 100ul',
    'author': 'Emma Rentkiewicz <emma.rentkiewicz@luminultra.com>',
    'description': 'Move 100ul from one 1.5ml tube to another 1.5ml tube',
    'apiLevel': '2.12'
}
############
# functions

def run(protocol: protocol_api.ProtocolContext):

    # LABWARE
    rack_1 = protocol.load_labware('opentrons_24_tuberack_nest_1.5ml_screwcap', '1')
    tiprack20 = protocol.load_labware('opentrons_96_filtertiprack_20ul', '2')

    # PIPETTES
    # p300 = protocol.load_instrument(
    #     'p300_single_gen2', 'left', tip_racks=[tiprack300]
    # )
    p20 = protocol.load_instrument(
        'p20_single_gen2', 'right', tip_racks=[tiprack20]
    )

    # FLUID
    fluid = rack_1['A1']
    emmaTube = rack_1['D6']

    # user imputs
    fluid_vol = 100 #ul

    # Commands
    # distribute fluid from A1 to D6
    p20.pick_up_tip()
    p20.aspirate(15, fluid)
    p20.dispense(15, emmaTube)
    p20.drop_tip()


    