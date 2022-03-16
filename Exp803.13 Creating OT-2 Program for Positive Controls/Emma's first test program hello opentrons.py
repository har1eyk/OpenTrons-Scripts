# imports
from opentrons import protocol_api

# metadata
metadata = {
    'protocolName': 'Move 100ul',
    'author': 'Emma Rentkiewicz <emma.rentkiewicz@luminultra.com>',
    'description': 'Move 100ul from one 1.5ml tube to another 1.5ml tube',
    'apilevel': '2.12'
}
############
# functions

def run(protocol: protocol_api.ProtocolContext):

    # LABWARE
    rack_1 = protocol.load_labware('opentrons_24_tuberack_nest_1.5ml_screwcap', '1')
    tiprack300 = protocol.load_labware('opentrons_96_filtertiprack_200ul', '11')

    # PIPETTES
    p300 = protocol.load_instrument(
        'p300_single_gen2', 'left', tip_racks=[tiprack300]
    )

    # FLUID
    fluid = rack_1['A1']

    # user imputs
    fluid_vol = 100 #ul
    all_racks = [rack_1]
    rack_rows = ['D']
    rack_cols = ['6']

    # Commands
    # distribute fluid from A1 to D6
    p300.pick_up_tip()
    for rack in all_racks:
        for i in range(6): # columns
            if i==6:
                p300.aspirate(fluid_vol, fluid)
             for j in range(4): # rows
                 dest = rack[rack_rows[j] + rack_cols[i]]
                 p300.dispense(fluid_vol, dest.bottom(2))
    p300.drop_tip()


    