# imports
from opentrons import protocol_api

# metadata
metadata = {
    'protocolName': 'Distribute Mmix and Samples in 48wells.',
    'author': 'Harley King <harley.king@luminultra.com>',
    'description': 'Testing two mmixes. Distribute 15ul mmix in 48wells and then 5ul sample.',
    'apiLevel': '2.11'
}

##########################

def run(protocol: protocol_api.ProtocolContext):

    # LABWARE
    fuge_rack = protocol.load_labware('vwr_24_tuberack_1500ul', '2')
    tiprack300 = protocol.load_labware('opentrons_96_filtertiprack_200ul', '8')
    tiprack20 = protocol.load_labware('opentrons_96_filtertiprack_20ul', '9')
    tempdeck = protocol.load_module('tempdeck', '10')
    sectempdeck = protocol.load_module('tempdeck', '4')
    plate = tempdeck.load_labware('abi_96_wellplate_250ul')
    stds_rack = sectempdeck.load_labware('opentrons_24_aluminumblock_nest_2ml_screwcap')
    
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
    BioMix_cols = ['1', '2', '3', '4', '5', '6']
    LU_Mix_cols = ['7', '8', '9', '10', '11', '12']
    beta = [b_std_1, b_std_2, b_std_3, b_std_4, b_std_5, b_std_6, b_std_7]
    # beta_Bio_wells = [['A1', 'A4'], ['B1', 'B4'], ['C1', 'C4'], ['D1', 'D4'], ['E1', 'E4'], ['F1', 'F4'], ['G1', 'G4'], ['H1', 'H4']]
    beta_wells = [['A1', 'A4', 'A7', 'A10'], ['B1', 'B4', 'B7', 'B10'], ['C1', 'C4', 'C7', 'C10'], ['D1', 'D4', 'D7', 'D10'], ['E1', 'E4', 'E7', 'E10'], ['F1', 'F4', 'F7', 'F10'], ['G1', 'G4', 'G7', 'G10']]

    gamma = [g_std_1, g_std_2, g_std_3, g_std_4, g_std_5, g_std_6, g_std_7]
    gamma_wells = [['A2', 'A5', 'A8', 'A11'], ['B2', 'B5', 'B8', 'B11'], ['C2', 'C5', 'C8', 'C11'], ['D2', 'D5', 'D8', 'D11'], ['E2', 'E5', 'E8', 'E11'], ['F2', 'F5', 'F8', 'F11'], ['G2', 'G5', 'G8', 'G11'], ['H2', 'H5', 'H8', 'H11']]
    
    delta = [d_std_1, d_std_2, d_std_3, d_std_4, d_std_5, d_std_6, d_std_7]
    delta_wells = [['A3', 'A6', 'A9', 'A12'], ['B3', 'B6', 'B9', 'B12'], ['C3', 'C6', 'C9', 'C12'], ['D3', 'D6', 'D9', 'D12'], ['E3', 'E6', 'E9', 'E12'], ['F3', 'F6', 'F9', 'F12'], ['G3', 'G6', 'G9', 'G12'], ['H3', 'H6', 'H9', 'H12']]

    NEG_wells = ['H1', 'H2', 'H3', 'H7', 'H8', 'H9']
    BioPositive_wells = ['H4', 'H5', 'H6']
    LUPositive_wells = ['H10', 'H11', 'H12']

    # #### COMMANDS ######    
    # Transfer BioSellal mmix to cols 1-6
    # for col in BioMix_cols:
    #     p20.transfer(
    #         15,
    #         BioMix.bottom(2),
    #         plate.columns_by_name()[col],
    #         blow_out=True,
    #         blowout_location='destination well',
    #         touch_tip=True,
    #         new_tip='once'
    #     )
    # # Transfer LU mmix to cols 7-12
    # for col in LU_Mix_cols:
    #     p20.transfer(
    #         15,
    #         LU_Mix.bottom(2),
    #         plate.columns_by_name()[col],
    #         blow_out=True,
    #         blowout_location='destination well',
    #         touch_tip=True,
    #         new_tip='once'
    #     )

    # Add Beta samples to Mix
    for sample, pos in zip(beta, beta_wells):
        p20.distribute(
            5,
            sample.bottom(2),
            [plate.wells_by_name()[well_name] for well_name in pos],
            disposal_volume=0
        )
    # Add Gamma samples to Mix
    for sample, pos in zip(gamma, gamma_wells):
        p20.distribute(
            5,
            sample.bottom(2),
            [plate.wells_by_name()[well_name] for well_name in pos],
            disposal_volume=0
        )
    # Add Delta samples to Mix
    for sample, pos in zip(delta, delta_wells):
        p20.distribute(
            5,
            sample.bottom(2),
            [plate.wells_by_name()[well_name] for well_name in pos],
            disposal_volume=0
        )
    
    # Add POSITIVE samples to Mix
    p20.distribute(
        5,
        BioPositive.bottom(2),
        [plate.wells_by_name()[well_name] for well_name in BioPositive_wells],
        disposal_volume=0
    )
    p20.distribute(
        5,
        LUPositive.bottom(2),
        [plate.wells_by_name()[well_name] for well_name in LUPositive_wells],
        disposal_volume=0
    )
    # Add NEGATIVE samples to mix    
    p20.distribute(
        5,
        water.bottom(2),
        [plate.wells_by_name()[well_name] for well_name in NEG_wells]
    )
