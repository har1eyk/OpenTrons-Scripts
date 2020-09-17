# imports
from opentrons import labware, instruments

# metadata
metadata = {
    'protocolName': 'Setting up PCR Reaction for BSCI:414 students',
    'author': 'Harley King <harley@umd.edu>',
    'description': 'Students specify a sets of primers for a list of six, OpenTrons does the pipetting.',
}

# labware
plate = labware.load('96-flat', '1')
fuge_race = labware.load('24_tube_rack', '2')
tiprack = labware.load('opentrons_96_tiprack_300ul', '5')
tiprack = labware.load(('opentrons_96_tiprack_10ul', '4'))

# pipettes
pipette = instruments.P300_Single(mount='right', tip_racks=[tiprack])

# commands
pipette.transfer(100, plate.wells('A1'), plate.wells('B2'))