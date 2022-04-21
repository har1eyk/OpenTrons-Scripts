# imports
from opentrons import protocol_api

# metadata
metadata = {
    'protocolName': 'Q16--Distribute Mmix and Samples in wells.',
    'author': 'Harley King <harley.king@luminultra.com>',
    'description': 'Duplicating samples and two RNA concentrations for 3 samples.',
    'apiLevel': '2.11'
}
#OVERVIEW
# see Excel sheet for overview. Makes 3 copies for 2, Q16 and 1 Q96 runs

##########################

def run(protocol: protocol_api.ProtocolContext):

    # LABWARE
    fuge_rack = protocol.load_labware('vwr_24_tuberack_1500ul', '2')
    tiprack300 = protocol.load_labware('opentrons_96_filtertiprack_200ul', '8')
    tiprack20 = protocol.load_labware('opentrons_96_filtertiprack_20ul', '9')
    tempdeck = protocol.load_module('tempdeck', '10')
    sectempdeck = protocol.load_module('tempdeck', '4')
    plate = tempdeck.load_labware('opentrons_96_aluminumblock_generic_pcr_strip_200ul')
    stds_rack = sectempdeck.load_labware('opentrons_24_aluminumblock_generic_2ml_screwcap')
    
    # PIPETTES
    p300 = protocol.load_instrument(
        'p300_single_gen2', 'left', tip_racks=[tiprack300]
    )
    p20 = protocol.load_instrument(
        'p20_single_gen2', 'right', tip_racks=[tiprack20]
    )
    
    # REAGENTS
    b_std_1 = stds_rack['A1'] 
    b_std_2 = stds_rack['A2'] 
    b_std_3 = stds_rack['A3'] 
    b_std_4 = stds_rack['A4'] 
    b_std_5 = stds_rack['A5'] 
    b_std_6 = stds_rack['A6']  
    b_std_7 = stds_rack['D1'] 
    
    g_std_1 = stds_rack['B1'] 
    g_std_2 = stds_rack['B2'] 
    g_std_3 = stds_rack['B3'] 
    g_std_4 = stds_rack['B4'] 
    g_std_5 = stds_rack['B5'] 
    g_std_6 = stds_rack['B6']  
    g_std_7 = stds_rack['D2'] 
    
    d_std_1 = stds_rack['C1'] 
    d_std_2 = stds_rack['C2'] 
    d_std_3 = stds_rack['C3'] 
    d_std_4 = stds_rack['C4'] 
    d_std_5 = stds_rack['C5'] 
    d_std_6 = stds_rack['C6']  
    d_std_7 = stds_rack['D3'] 
    
    BioMix = stds_rack['D5'] # BioSellal MasterMix
    LU_Mix = stds_rack['D6'] # LU MasterMix
    
    water = fuge_rack['D6'] # water
    BioPositive = fuge_rack['A1'] # BioSellal Positive Control plasmid
    LUPositive = fuge_rack['A6'] # LU Positive Control plasmid
    
    # Lists
    BioMix_cols = ['1', '3', '5', '7', '9', '11']
    
    beta = [b_std_1, b_std_6, b_std_7] #really gamma
    beta_wells = [['A1', 'A3', 'A5', 'A7', 'A9', 'A11'], ['B1', 'B3', 'B5', 'B7', 'B9', 'B11'], ['G1', 'G5', 'G9']] # triplicate

    gamma = [g_std_1, g_std_6, g_std_7] #really kappa
    gamma_wells = [['C1', 'C3', 'C5', 'C7', 'C9', 'C11'], ['D1', 'D3', 'D5', 'D7', 'D9', 'D11'], ['G3', 'G7', 'G11']]
    
    delta = [d_std_1, d_std_6, d_std_7] #really delta
    delta_wells = [['E1', 'E3', 'E5', 'E7', 'E9', 'E11'], ['F1', 'F3', 'F5', 'F7', 'F9', 'F11'], ['H1', 'H5', 'H9']]
    
    # NEG_wells = ['H1', 'H2', 'H3', 'H7', 'H8', 'H9'] # no room
    BioPositive_wells = ['H3', 'H7', 'H11']
    # LUPositive_wells = ['H10', 'H11', 'H12']

    # #### COMMANDS ######    
    # Transfer BioSellal mmix to cols 1-6
    for col in BioMix_cols:
        p20.transfer(
            15,
            BioMix.bottom(2),
            plate.columns_by_name()[col],
            blow_out=True,
            blowout_location='destination well',
            touch_tip=True,
            new_tip='once'
        )
 
    # Add Beta samples to Mix
    for sample, pos in zip(beta, beta_wells):
        p20.distribute(
            5,
            sample.bottom(2),
            [plate.wells_by_name()[well_name] for well_name in pos],
            new_tip='always'
        )
    # Add Gamma samples to Mix
    for sample, pos in zip(gamma, gamma_wells):
        p20.distribute(
            5,
            sample.bottom(2),
            [plate.wells_by_name()[well_name] for well_name in pos],
            new_tip='always'
        )
    # Add Delta samples to Mix
    for sample, pos in zip(delta, delta_wells):
        p20.distribute(
            5,
            sample.bottom(2),
            [plate.wells_by_name()[well_name] for well_name in pos],
            new_tip='always'
        )
    
    # Add POSITIVE samples to Mix
    p20.distribute(
        5,
        BioPositive.bottom(2),
        [plate.wells_by_name()[well_name] for well_name in BioPositive_wells],
        new_tip='always'
    )
