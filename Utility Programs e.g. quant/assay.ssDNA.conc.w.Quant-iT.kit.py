# imports
from opentrons import protocol_api

# metadata
metadata = {
    'protocolName': 'Serial Diluting Primers and Quantifying with Quant-iT OliGreen ssDNA Assay Kit',
    'author': 'Harley King <harley.king@luminultra.com>',
    'description': 'Test unknown primer concentration with standard curve and intercalating dye.',
    'apiLevel': '2.8'
}
##########################
def run(protocol: protocol_api.ProtocolContext):

    # labware
    fuge_rack = protocol.load_labware('opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap', '6')
    tiprack300 = protocol.load_labware('opentrons_96_tiprack_300ul', '8')
    tiprack20 = protocol.load_labware('opentrons_96_tiprack_20ul', '7')

    # pipettes
    p300 = protocol.load_instrument(
        'p300_single_gen2', 'left', tip_racks=[tiprack300]
    )
    p20 = protocol.load_instrument(
        'p20_single_gen2', 'right', tip_racks=[tiprack20]
    )
    
    # reagent locations
    te_bufr = fuge_rack['D1']
    te_bufr_2 = fuge_rack['D2']
    OliGreen = fuge_rack['A1']
    ssDNA_std = fuge_rack['C1']
    liquid_trash = fuge_rack['B1']
    std_1 = fuge_rack['A3']
    std_2 = fuge_rack['A4']
    std_3 = fuge_rack['A5']
    std_4 = fuge_rack['A6']
    std_5 = fuge_rack['B3']
    std_6 = fuge_rack['B4']
    std_7 = fuge_rack['B5']
    std_8 = fuge_rack['B6']
    blank_std = fuge_rack['A2']
    all_stds = [std_1, std_2, std_3, std_4, std_5, std_6, std_7, std_8]
    # samples
    sample_1 = fuge_rack['C4']
    sample_1_dil = fuge_rack['C5']
    sample_1_dil_half = fuge_rack['C6']
    sample_2 = fuge_rack['D4']
    sample_2_dil = fuge_rack['D5']
    sample_2_dil_half = fuge_rack['D6']
    vol_from_sample = 10 # how much primer vol (ul) to add to 125ul TE buffer
    vol_from_std = 20 # how much ssDNA standard to add to 125ul TE buffer
    all_samples = [sample_1_dil, sample_1_dil_half, sample_2_dil, sample_2_dil_half]
    all_stds_samples = (all_stds + all_samples)
    all_stds_samples_bl = all_stds_samples + [blank_std]
    # all_stds_bl = all_stds + [blank_std]
    # all_stds_bl_r = all_stds_bl
    # all_stds_bl_r.reverse()
    
    ###### commands ######
    ## MAKE STDS
    # add 125ul TE buffer to blank, 115ul to std_1 tube and various to samples
    p300.pick_up_tip()
    # blank
    p300.aspirate(125, te_bufr)
    p300.dispense(125, blank_std) # make blank std
    # add 120ul to std_1
    p300.aspirate(150, te_bufr) 
    p300.dispense(150-vol_from_std, std_1) # make std_1
    # add TE buffer to sample_1 tubes
    p300.aspirate(250-vol_from_sample, te_bufr_2) # account for sample vol added to this tube for dil
    p300.dispense(250-vol_from_sample, sample_1_dil) # make sample_1 dil
    p300.aspirate(125, te_bufr_2)
    p300.dispense(125, sample_1_dil_half) # make sample_1 dil in half
    # add TE buffer to sample_2 tubes
    p300.aspirate(250-vol_from_sample, te_bufr_2) 
    p300.dispense(250-vol_from_sample, sample_2_dil) # make sample_2 dil
    p300.aspirate(125, te_bufr_2)
    p300.dispense(125, sample_2_dil_half) # make sample_2 dil in half
    # p300.drop_tip() # in trash
    
    # transfer 125ul to all std tubes, std_1 tot vol = 240
    p300.transfer(125, te_bufr, all_stds, new_tip='never') # transfer 125ul to all std tubes
    p300.blow_out(liquid_trash)
    p300.drop_tip()

    # dil ssDNA_std by adding 10ul to std_1
    # std_1 tot vol = 240+10 =250ul
    p20.transfer(
        vol_from_std,
        ssDNA_std.bottom(3),
        std_1.bottom(3),
        mix_before=(2, 20),
        mix_after=(2,20),
        blow_out=True)

    # serially dilute; must start with well A3, hi conc
    p300.pick_up_tip()
    for i in range(len(all_stds)-1): # loop through stds: asp, disp and mix
        p300.mix(3, 225, all_stds[i])
        p300.aspirate(125, all_stds[i])
        p300.dispense(125, all_stds[i+1])
    p300.transfer(125, std_8, liquid_trash, mix_before=(4, 100), new_tip='never') # remove 125 from 250ul total vol
    p300.drop_tip()
        # p300.transfer(125, all_stds[i], all_stds[i+1], mix_before=(2, 100), mix_after=(2,100))

    # dilute unknown samples e.g. primers
    p20.transfer(
        vol_from_sample,
        sample_1.bottom(3),
        sample_1_dil.bottom(3),
        mix_before=(2, 10),
        blow_out=True,
        mix_after=(2, 20))
    p20.transfer(
        vol_from_sample,
        sample_2.bottom(3),
        sample_2_dil.bottom(3),
        mix_before=(2, 10),
        blow_out=True,
        mix_after=(2,20))
    
    # serially dilute samples with vol from above
    # need to step by 2 so I don't have sample_1_dil_half mixing with sample_2_dil as in list
    # just want 0->1 and 2->3 not 1->2
    for i in range(0, len(all_samples)-1, 2): 
        p300.pick_up_tip()
        p300.mix(3, 225, all_samples[i])
        p300.aspirate(125, all_samples[i])
        p300.dispense(125, all_samples[i+1])
        p300.mix(3, 225, all_samples[i+1])
        p300.aspirate(125, all_samples[i+1]) # remove 125 from 250ul total vol
        p300.dispense(125, liquid_trash)
        p300.drop_tip()
    # p300.transfer(125, sample_2_dil, sample_2_dil_half, mix_before=(4, 125), blow_out=True, mix_after=(4, 125))

    ## add OliGreen to stds and samples, mix
    # each sample needs a new tip
    p300.transfer(
        125,
        OliGreen,
        all_stds_samples_bl,
        mix_before=(1, 100),
        blow_out=True,
        mix_after=(3,225),
        new_tip='always')    
