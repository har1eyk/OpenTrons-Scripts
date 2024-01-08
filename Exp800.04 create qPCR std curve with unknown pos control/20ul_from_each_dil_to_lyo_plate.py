# imports
from opentrons import protocol_api

# metadata
metadata = {
    'protocolName': 'Add 6-reps, 20ul from a Dilution Series to a Lyophilized BioER Plate.',
    'author': 'Harley King <harley.king@luminultra.com>',
    'description': 'Re-hydrolizes reactions with 20ul from a dilution series to a lyophilized plate.',
    'apiLevel': '2.13'
}
##########################

def run(protocol: protocol_api.ProtocolContext):

    # LABWARE
    stds_rack = protocol.load_labware('vwr_24_tuberack_1500ul', '2')
    tiprack300 = protocol.load_labware('opentrons_96_filtertiprack_200ul', '8')
    tempdeck = protocol.load_module('tempdeck', '10')
    plate = tempdeck.load_labware('bioer_96_aluminumblock_200ul')

    # PIPETTES
    p300 = protocol.load_instrument(
        'p300_single_gen2', 'left', tip_racks=[tiprack300]
    )
    
    
# Revised tube to wells mapping for all tubes
    tube_to_wells_map = {
    'A1': ['A1', 'A2', 'A3', 'A4', 'A5', 'A6'],
    'A2': ['B1', 'B2', 'B3', 'B4', 'B5', 'B6'],
    'A3': ['C1', 'C2', 'C3', 'C4', 'C5', 'C6'],
    'A4': ['D1', 'D2', 'D3', 'D4', 'D5', 'D6'],
    'A5': ['E1', 'E2', 'E3', 'E4', 'E5', 'E6'],
    'A6': ['F1', 'F2', 'F3', 'F4', 'F5', 'F6'],
    'B1': ['G1', 'G2', 'G3', 'G4', 'G5', 'G6'],
    'B2': ['H1', 'H2', 'H3', 'H4', 'H5', 'H6'],
    'B3': ['A7', 'A8', 'A9', 'A10', 'A11', 'A12'],
    'B4': ['B7', 'B8', 'B9', 'B10', 'B11', 'B12'],
    'B5': ['C7', 'C8', 'C9', 'C10', 'C11', 'C12'],
    'B6': ['D7', 'D8', 'D9', 'D10', 'D11', 'D12'],
    'C1': ['E7', 'E8', 'E9', 'E10', 'E11', 'E12'],
    'C2': ['F7', 'F8', 'F9', 'F10', 'F11', 'F12'],
    'C3': ['G7', 'G8', 'G9', 'G10', 'G11', 'G12'],
    'D6': ['H7', 'H8', 'H9', 'H10', 'H11', 'H12']
    }

    # ### COMMANDS ######

    # add 20ul to 6 wells in plate
    # Iterate over the mapping and perform dispensing
    for tube_position, wells in tube_to_wells_map.items():
        tube = stds_rack[tube_position]
        p300.pick_up_tip()
        p300.mix(1, 200, tube.bottom(5))  # Pre-wetting tip
        p300.aspirate(120 + 10, tube.bottom(5))  # Adjust 'extra_volume' as needed
        for well in wells:
            p300.dispense(20, plate[well].bottom(7), rate=0.75)
            p300.touch_tip(plate[well], v_offset=-2, speed=40) # a little bit lower and a little bit slower so the tip doesn't flick into adjacent wells
        p300.drop_tip()

   
