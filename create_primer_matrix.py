# imports
from opentrons import protocol_api

# metadata
metadata = {
    'protocolName': 'Create Primer Conc Matrix for Optimization',
    'author': 'Harley King <harley.king@luminultra.com>',
    'description': 'Create a fwd, rev primer conc matrix to optimize conc.',
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
    
    ###### commands ######
    
    # reagent locations
    pos_control = fuge_rack['A1']
    liquid_trash = fuge_rack['B1']
    water = fuge_rack['C1']
    mmix = fuge_rack['D1']
    
    fwd_10uM = fuge_rack['B2']
    rev_10uM = fuge_rack['D2']
    mmix_NTC = fuge_rack['C2']

    fwd_1 = fuge_rack['A4'] # e.g. 0.625uM
    fwd_2 = fuge_rack['A5'] # e.g. 1.25uM
    fwd_3 = fuge_rack['A6'] # e.g. 2.5uM
    fwd_4 = fuge_rack['B4'] # e.g. 5.0uM
    fwd_5 = fuge_rack['B5'] # e.g. 7.5uM
    fwd_6 = fuge_rack['B6'] # e.g. 10uM

    mmx_rev_1 = fuge_rack['C4'] # e.g. 0.625uM
    mmx_rev_2 = fuge_rack['C5'] # e.g. 1.25uM
    mmx_rev_3 = fuge_rack['C6'] # e.g. 2.5uM
    mmx_rev_4 = fuge_rack['D4'] # e.g. 5.0uM
    mmx_rev_5 = fuge_rack['D5'] # e.g. 7.5uM
    mmx_rev_6 = fuge_rack['D6'] # e.g. 10uM
    

    ## make stds
    # add TE buffer to tubes, make blank
    # p300.pick_up_tip()
    # p300.aspirate(125, te_bufr)
    # p300.dispense(125, blank_std) # make blank std
    # p300.aspirate(150, te_bufr) 
    # p300.dispense(125, std_1) # make std_1
    # # add TE buffer to sample_1 tubes
    # p300.aspirate(250-vol_from_sample, te_bufr_2) 
    # p300.dispense(250-vol_from_sample, sample_1_dil) # make sample_1 dil
    # p300.aspirate(125, te_bufr_2)
    # p300.dispense(125, sample_1_dil_half) # make sample_1 dil in half
    # # add TE buffer to sample_2 tubes
    # p300.aspirate(250-vol_from_sample, te_bufr_2) 
    # p300.dispense(250-vol_from_sample, sample_2_dil) # make sample_2 dil
    # p300.aspirate(125, te_bufr_2)
    # p300.dispense(125, sample_2_dil_half) # make sample_2 dil in half
    # # p300.drop_tip() # in trash
    
    # # transfer 125ul to all std tubes
    # p300.transfer(125, te_bufr, all_stds, new_tip='never') # transfer 125ul to all std tubes
    # # for i in range(len(all_stds)):
    #     # p300.transfer(125, te_bufr, all_stds[i]) # add 125ul from te_bufr tube to all std tubes
    # # p300.pick_up_tip()
    # p300.blow_out(liquid_trash)
    # p300.drop_tip()

    # # add ssDNA_std
    # p20.transfer(
    #     5,
    #     ssDNA_std.bottom(3),
    #     std_1.bottom(3),
    #     mix_before=(2, 20),
    #     mix_after=(2,20),
    #     blow_out=True)

    # # serially dilute; must start with well A3, hi conc
    # p300.pick_up_tip()
    # for i in range(len(all_stds)-1): # loop through stds: asp, disp and mix
    #     p300.mix(3, 225, all_stds[i])
    #     p300.aspirate(125, all_stds[i])
    #     p300.dispense(125, all_stds[i+1])
    # p300.transfer(125, std_8, liquid_trash, mix_before=(4, 100), new_tip='never') # remove 125 from 250ul total vol
    # p300.drop_tip()
    #     # p300.transfer(125, all_stds[i], all_stds[i+1], mix_before=(2, 100), mix_after=(2,100))

    # # dilute unknown primers
    # p20.transfer(
    #     vol_from_sample,
    #     sample_1.bottom(3),
    #     sample_1_dil.bottom(3),
    #     mix_before=(2, 10),
    #     blow_out=True,
    #     mix_after=(2, 20))
    # p20.transfer(
    #     vol_from_sample,
    #     sample_2.bottom(3),
    #     sample_2_dil.bottom(3),
    #     mix_before=(2, 10),
    #     blow_out=True,
    #     mix_after=(2,20))
    # # serially dilute samples with vol from above
    # # need to step by 2 so I don't have sample_1_dil_half mixing with sample_2_dil as in list
    # # just want 0->1 and 2->3 not 1->2
    # for i in range(0, len(all_samples)-1, 2): 
    #     p300.pick_up_tip()
    #     p300.mix(3, 225, all_samples[i])
    #     p300.aspirate(125, all_samples[i])
    #     p300.dispense(125, all_samples[i+1])
    #     p300.mix(3, 225, all_samples[i+1])
    #     p300.aspirate(125, all_samples[i+1]) # remove 125 from 250ul total vol
    #     p300.dispense(125, liquid_trash)
    #     p300.drop_tip()
    # # p300.transfer(125, sample_2_dil, sample_2_dil_half, mix_before=(4, 125), blow_out=True, mix_after=(4, 125))

    # ## add OliGreen to stds and samples, mix
    # # each sample needs a new tip
    # p300.transfer(
    #     125,
    #     OliGreen,
    #     all_stds_samples_bl,
    #     mix_before=(1, 100),
    #     blow_out=True,
    #     mix_after=(3,225),
    #     new_tip='always')    
