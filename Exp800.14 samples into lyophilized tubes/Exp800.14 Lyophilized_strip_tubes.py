# imports
from opentrons import protocol_api

# metadata
metadata = {
    'protocolName': 'Test qPCR Samples Using Lyophilized Samples in 8-well strips.',
    'author': 'Harley King <harley.king@luminultra.com>',
    'description': 'Add DNA samples to lyophilized 8-well strip tubes.',
    'apiLevel': '2.10'
}
##########################

def run(protocol: protocol_api.ProtocolContext):

    # LABWARE
    fuge_rack = protocol.load_labware('vwr_24_tuberack_1500ul', '1')
    stds_rack = protocol.load_labware('vwr_24_tuberack_1500ul', '2')
    tiprack300 = protocol.load_labware('opentrons_96_filtertiprack_200ul', '8')
    tiprack20 = protocol.load_labware('opentrons_96_filtertiprack_20ul', '9')
    tempdeck = protocol.load_module('tempdeck', '4')
    plate = tempdeck.load_labware('opentrons_96_aluminumblock_generic_pcr_strip_200ul')

    # PIPETTES
    p300 = protocol.load_instrument(
        'p300_single_gen2', 'left', tip_racks=[tiprack300]
    )
    p20 = protocol.load_instrument(
        'p20_single_gen2', 'right', tip_racks=[tiprack20]
    )
    
    # REAGENTS
    #fuge_rack @ position 1
    samp_1 = fuge_rack['B1'] 
    samp_2 = fuge_rack['B2']
    samp_3 = fuge_rack['B3']
    samp_4 = fuge_rack['B4']
    samp_5 = fuge_rack['B5']
    samp_6 = fuge_rack['B6']
    samp_7 = fuge_rack['C1']

    # sds_rack  @ position 2
    WATER = stds_rack['D1'] # 1500ul WATER
    SAMP_1mix = stds_rack['C3'] # empty
    SAMP_2mix = stds_rack['C4'] # empty
    SAMP_3mix = stds_rack['C5'] # empty
    SAMP_4mix = stds_rack['C6'] # empty
    SAMP_5mix = stds_rack['D3'] # empty
    SAMP_6mix = stds_rack['D4'] # empty
    SAMP_7mix = stds_rack['D5'] # empty
    NTC_mix = stds_rack['D6'] # empty, receives sN_mix and WATER as NTC
    
    # user inputs
    num_of_sample_reps = 5
    add_sample_vol = 2
    tot_sample_vol = 20
    add_water_vol = tot_sample_vol-add_sample_vol
    samp_XFR_to_SAMPmix = num_of_sample_reps*add_sample_vol*1.2
    water_XFR_to_SAMPmix = num_of_sample_reps*add_water_vol*1.2

    # p300_max_vol = 200
    # mix_master_tot = 96*18*1.2 # total vol of mastermix
    # mmix_XFR_std_mix = 3*18*1.14 # transfer this amount to the std mix intermediate tubes that will receive DNA
    # std_dna_XFR_to_std_int=3*2*1.14	#transfer this amount DNA to std_int_tubes to mix and aliquot to 3 wells
    # mmix_XFR_samp_wells = 18*12*1.1 # how much mastermix transferred as bolus to well A1, B1..F1 to receive DNA
    
    # lists
    # all_std_tubes = [std_1, std_2, std_3, std_4, std_5, std_6, std_7, std_8, std_9, std_10, std_11, std_12, std_13, std_14, std_15]
    ALL_SAMPs = [samp_1, samp_2, samp_3, samp_4, samp_5, samp_6, samp_7, WATER]
    SAMP_mixes = [SAMP_1mix, SAMP_2mix, SAMP_3mix, SAMP_4mix, SAMP_5mix, SAMP_6mix, SAMP_7mix, NTC_mix]
    SAMP_wells = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
    # ALL_TUBEs = # std_mixes = [std_1mix, std_2mix, std_3mix, std_4mix, std_5mix, std_6mix, std_7mix, NTC_mix]
    # std_wells = ['G1', 'G4', 'G7', 'G10', 'H1', 'H4', 'H7', 'H10']
    # samp_sources = [std_10, std_11, std_12, std_13, std_14, samp_1]
    
    
    # #### COMMANDS ######
    # prepare samples by distributing water to SAMP_mixes
    # p300.pick_up_tip()
    # for mymix in SAMP_mixes:
    #     p300.aspirate(water_XFR_to_SAMPmix, WATER.bottom(2))
    #     protocol.delay(seconds=1) #equilibrate
    #     p300.dispense(water_XFR_to_SAMPmix, mymix)
    #     p300.blow_out(mymix.bottom(10)) #have to bring up or create air bubble at liquid base
    # p300.drop_tip()
    
    # Add sample DNA, mix, distribute to strip tubes
    for i, (sample, mixtube) in enumerate(zip(ALL_SAMPs, SAMP_mixes)):
        p20.pick_up_tip()
        p300.pick_up_tip()
        # p20.aspirate(samp_XFR_to_SAMPmix, sample, rate=0.8) #aspirate from sample at rate = 2ul/sec default=7.56
        protocol.delay(seconds=2) #equilibrate
        # p20.touch_tip()
        # p20.dispense(samp_XFR_to_SAMPmix, mixtube)
        protocol.delay(seconds=1) #equilibrate
        # p20.mix(2, 20, mixtube.bottom(4)) # rinse tip
        # p20.blow_out()
        p300.move_to(mixtube.bottom(40)) #prevent tip from crashing into tube cap
        mix_vol = 0.70*num_of_sample_reps*tot_sample_vol*1.2 # 70% of total vol
        p300.mix(7, 40, mixtube.bottom(2))
        protocol.delay(seconds=2)
        p300.blow_out(mixtube.bottom(10))
        p20.move_to(mixtube.bottom(40))
        # add 20ul to strip tubes in cols 1, 3, 5...etc. Never will be more than 6 strip tubes / 96w holder
        # num_of_sample_reps is another way of stating number of strips
        for x in range(0, num_of_sample_reps): 
            p20.aspirate(20, mixtube, rate=0.3) 
            protocol.delay(seconds=2) #equilibrate
            row = SAMP_wells[i]
            dest = row+str(2*x+1) # need +1 offset for col 
            p20.dispense(20, plate[dest].bottom(6), rate=0.4) # more height so tip doesn't touch pellet
            protocol.delay(seconds=2)
            p20.move_to(plate[dest].bottom(6))
            p20.blow_out()
            p20.touch_tip()
        p300.drop_tip()
        p20.drop_tip()