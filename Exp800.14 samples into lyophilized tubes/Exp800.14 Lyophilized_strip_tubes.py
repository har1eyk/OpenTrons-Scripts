# imports
from opentrons import protocol_api

# metadata
metadata = {
    'protocolName': 'Test qPCR Samples Using Lyophilized Samples in 8-well strips.',
    'author': 'Harley King <harley.king@luminultra.com>',
    'description': 'Add DNA samples to lyophilized 8-well strip tubes.',
    'apiLevel': '2.9'
}
##########################

def run(protocol: protocol_api.ProtocolContext):

    # LABWARE
    fuge_rack = protocol.load_labware('vwr_24_tuberack_1500ul', '1')
    stds_rack = protocol.load_labware('vwr_24_tuberack_1500ul', '2')
    tiprack300 = protocol.load_labware('opentrons_96_filtertiprack_200ul', '8')
    tiprack20 = protocol.load_labware('opentrons_96_filtertiprack_20ul', '9')
    tempdeck = protocol.load_module('tempdeck', '10')
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
    WATER = fuge_rack['A1'] # 1500ul WATER

    # sds_rack  @ position 2
    SAMP_1mix = stds_rack['C3'] # empty
    SAMP_2mix = stds_rack['C4'] # empty
    SAMP_3mix = stds_rack['C5'] # empty
    SAMP_4mix = stds_rack['C6'] # empty
    SAMP_5mix = stds_rack['D3'] # empty
    SAMP_6mix = stds_rack['D4'] # empty
    SAMP_7mix = stds_rack['D5'] # empty
    NTC_mix = stds_rack['D6'] # empty, receives sN_mix and WATER as NTC
    
    # user inputs
    num_of_sample_reps = 4
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
    p300.pick_up_tip()
    for mymix in SAMP_mixes:
        p300.aspirate(water_XFR_to_SAMPmix, WATER.bottom(3))
        protocol.delay(seconds=2) #equilibrate
        p300.dispense(water_XFR_to_SAMPmix, mymix)
    p300.drop_tip()
    
    # Add sample DNA, mix, distribute to strip tubes
    for i, sample, mixtube in enumerate(zip(ALL_SAMPs, SAMP_mixes)):
        p20.pick_up_tip()
        p300.pick_up_tip()
        p20.aspirate(samp_XFR_to_SAMPmix, sample, rate=3.0) #aspirate from sample at rate = 2ul/sec default=7.56
        protocol.delay(seconds=2) #equilibrate
        p20.touch_tip()
        p20.dispense(samp_XFR_to_SAMPmix, mixtube, rate=4.0)
        p20.mix(2, 20, mixtube.bottom(4)) # rinse tip
        p20.blow_out()
        p300.move_to(mixtube.bottom(40)) #prevent tip from crashing into tube cap
        p300.mix(3, 50, mixtube.bottom(3))
        protocol.delay(seconds=2)
        p300.blow_out(mixtube.bottom(10))
        p20.move_to(mixtube.bottom(40))
        # add 20ul to strip tubes in cols 1, 3, 5...etc. Never will be more than 6 strip tubes / 96w holder
        # num_of_sample_reps is another way of stating number of strips
        for x in range(0, num_of_sample_reps): 
            p20.aspirate(20, mixtube, rate=3.0) 
            protocol.delay(seconds=2) #equilibrate
            row = SAMP_wells[i]
            dest = row+(x+1) # need +1 offset for col 
            p20.dispense(20, plate[dest].bottom(2), rate=4.0)
            protocol.delay(seconds=2)
            p20.move_to(plate[dest].bottom(6))
            p20.blow_out()
            p20.touch_tip()
        p300.drop_tip()
        p20.drop_tip()
        

    # # # make pos control standards
    # # # transfer from pos_control to make std_1
    # # pos_control_height = tip_heights(400,1,10)
    # # p20.transfer(
    # #     10,
    # #     pos_control.bottom(pos_control_height[0]), #1uM
    # #     std_1.bottom(20),
    # #     mix_after=(2, 20), # remove residual fluid from tip
    # #     touch_tip=True
    # # )
    
    # # # serial dilutions in microfuge tubes, 10% diliutions
    # # p300.pick_up_tip()
    # # for i in range(len(all_std_tubes)-1): #don't want out of range because i + 1
    # #     p300.well_bottom_clearance.aspirate = 15 #mm come up for mixing 
    # #     p300.well_bottom_clearance.dispense = 15 #mm 
    # #     last_std_tube = len(all_std_tubes)-1 # (int) position of last std tube; last tube = WATER
    # #     if i==0 or i==last_std_tube: # first or last std tube; not WATER
    # #         p300.mix(3, 200, all_std_tubes[i]) # need to add mixes to first and last tubes
    # #     p300.mix(3, 200, all_std_tubes[i])
    # #     # p300.well_bottom_clearance.aspirate = 10 #mm 
    # #     p300.flow_rate.aspirate = 40 #slow aspirate; no air
    # #     p300.aspirate(100,all_std_tubes[i])
    # #     p300.touch_tip()
    # #     p300.flow_rate.dispense = 40 #slow dispense
    # #     p300.dispense(100, all_std_tubes[i+1])
    # #     p300.flow_rate.aspirate = 92.86 #default
    # #     p300.flow_rate.dispense = 92.86 #default
    # #     p300.mix(3, 200,all_std_tubes[i+1]) #remove residual inside tip
    # #     # p300.move_to(std_wells[i+1].bottom(15)) #come up for blowout
    # #     p300.blow_out()
    # #     protocol.delay(seconds=2) #wait for bubbles to subside
    # # p300.well_bottom_clearance.dispense = 1 #mm default
    # # p300.well_bottom_clearance.aspirate = 1 #mm default
    # # p300.drop_tip()

    # # # Mastermix contains primers and probe. Everything except DNA. Aliquot to 6 tubes.
    # # # transfer sN_mix to intermediate tubes (std_mixes)
    # # p300.pick_up_tip()
    # # p300.flow_rate.aspirate = 92.86 #default
    # # p300.flow_rate.dispense = 92.86 #default
    # # mmix_h = tip_heightsEpp(mix_master_tot, len(std_mixes), mmix_XFR_std_mix)
    # # # print ("mix_master_tot", mix_master_tot)
    # # # print (len(std_mixes))
    # # # print (mmix_XFR_std_mix)
    # # # print ("mmix_h", mmix_h)
    # # p300.mix(6, 200, MIX_master.bottom(mmix_h[0])) # top tip height
    # # p300.flow_rate.aspirate = 30
    # # p300.flow_rate.dispense = 40
    # # # p300.well_bottom_clearance.aspirate = std_mix_heights[0] #mm 
    # # for i, tube in enumerate(std_mixes):
    # #     # p300.well_bottom_clearance.aspirate = h #mm
    # #     p300.aspirate(mmix_XFR_std_mix, MIX_master.bottom(mmix_h[i])) # 18 * 3 * 1.12-0.05= 54 + 6 =60ul
    # #     protocol.delay(seconds=2) #tip equilibrate
    # #     p300.move_to(MIX_master.bottom(35)) # excess tip fluid condense 
    # #     protocol.delay(seconds=3) #tip droplets slide
    # #     p300.touch_tip()
    # #     p300.dispense(mmix_XFR_std_mix, tube.bottom(4))
    # #     p300.blow_out(tube.bottom(8))
    # # p300.drop_tip()
    # # p300.flow_rate.aspirate = 92.86 #reset to default
    # # p300.flow_rate.dispense = 92.86 #reset to default
   
    # # # transfer std DNA into intermediate std_mixes tubes and then to plate
    # # for std, intTube, well in zip(std_tubes, std_mixes, std_wells):
    # #     p20.pick_up_tip()
    # #     p300.pick_up_tip()
    # #     p20.flow_rate.aspirate = 4
    # #     p20.flow_rate.dispense = 4
    # #     p20.well_bottom_clearance.aspirate = 20
    # #     p20.aspirate(std_dna_XFR_to_std_int, std) #aspirate from std_1 into std_mix (intermediate tube) e.g. 6.42 ul
    # #     protocol.delay(seconds=2) #equilibrate
    # #     p20.touch_tip()
    # #     p20.well_bottom_clearance.dispense = 3
    # #     p20.dispense(std_dna_XFR_to_std_int, intTube)
    # #     # p20.move_to(intTube.bottom(3))
    # #     p20.flow_rate.aspirate = 7.56
    # #     p20.flow_rate.dispense = 7.56
    # #     p20.mix(2, 20, intTube.bottom(3)) #ensure vol in tip in intTube and washed
    # #     p20.blow_out()
    # #     p300.move_to(intTube.bottom(40)) #prevent tip from crashing into tube cap
    # #     p300.mix(3, 50, intTube.bottom(3))
    # #     protocol.delay(seconds=2)
    # #     # p300.move_to(intTube.bottom(10)) #prevent air bubbles in mmix during blow out
    # #     p300.blow_out(intTube.bottom(10))
    # #     p20.move_to(intTube.bottom(40))
    # #     p20.flow_rate.aspirate = 4
    # #     p20.flow_rate.dispense = 4
    # #     for x in range(0,3): # need int 1, 2, and 3
    # #         p20.aspirate(20, intTube.bottom(2)) 
    # #         protocol.delay(seconds=2) #equilibrate
    # #         # find digits in well, G1 and G10 and puts into list
    # #         findNums = [int(i) for i in well.split()[0] if i.isdigit()]
    # #         # joins nums from list [1, 0] -> 10 type = string
    # #         colNum = ''.join(map(str, findNums))
    # #         # this finds row
    # #         row = well.split()[0][0]
    # #         dest = row+str(int(colNum)+x) # row + neighbor well i.e. 1, 2
    # #         p20.dispense(20, plate[dest].bottom(2))
    # #         protocol.delay(seconds=2)
    # #         p20.move_to(plate[dest].bottom(6))
    # #         p20.blow_out()
    # #         # p20.touch_tip()
    # #     p300.drop_tip()
    # #     p20.drop_tip()
    # # p20.flow_rate.aspirate = 7.56
    # # p20.flow_rate.dispense = 7.56
    # # p20.well_bottom_clearance.dispense = 1
    # # p20.well_bottom_clearance.aspirate = 1

    # # transfer mastermix bolus to beginning wells to receive sample
    # samp_h = tip_heightsEpp(mix_master_tot-mmix_XFR_std_mix, len(samp_wells), mmix_XFR_samp_wells)
    # p300.pick_up_tip()
    # for i, well in enumerate(samp_wells):
    #     vols = split_asp(mmix_XFR_samp_wells, p300_max_vol) #split 237.60 into 2 asp steps
    #     for j, vol in enumerate(vols): # loop through each vol
    #         p300.flow_rate.aspirate = 40 #default
    #         p300.flow_rate.dispense = 40 #default
    #         p300.aspirate(vol, MIX_master.bottom(samp_h[i]))
    #         protocol.delay(seconds=2)
    #         p300.dispense(vol, plate[well].bottom(4*j+5))
    #         protocol.delay(seconds=1)
    #         p300.blow_out(plate[well].bottom(14))
    #         p300.touch_tip()
    # p300.drop_tip()

    # # add dna to first wells, mix, and aliquot to neighbors
    # # six samples, can be changed in the user inputs
    # samp_dna_XFR_to_wells = 12*2*1.1 # 26.4
    # for i, (sample, well) in enumerate(zip(samp_sources, samp_wells)):
    #     p300.pick_up_tip()
    #     p20.pick_up_tip()
    #     p300.flow_rate.aspirate = 92.86 
    #     p300.flow_rate.dispense = 92.86
    #     p300.mix(3, 200, sample) # mix the sample
    #     p300.flow_rate.aspirate = 30
    #     p300.flow_rate.dispense = 40
    #     p300.aspirate(samp_dna_XFR_to_wells, sample.bottom(2)) # sample vol may vary. Goto bottom.
    #     p300.move_to(sample.bottom(25)) # relieve pressure if tip at bottom
    #     protocol.delay(seconds=2)
    #     p300.touch_tip()
    #     p300.dispense(samp_dna_XFR_to_wells, plate[well].bottom(3))
    #     p300.flow_rate.aspirate = 92.86 
    #     p300.flow_rate.dispense = 92.86
    #     p300.mix(3, 200, plate[well].bottom(5)) # vol = 26.4 + 237.6 = 264
    #     p300.flow_rate.aspirate = 30 
    #     p300.flow_rate.dispense = 40
    #     p300.mix(1, 200, plate[well].bottom(3))
    #     p300.move_to(plate[well].bottom(14))
    #     protocol.delay(seconds=2)
    #     p300.blow_out(plate[well].bottom(16))
    #     p300.touch_tip()
    #     for x in range(1,12): # need int 1, 2, and 12
    #         # find digits in well, G1 and G10 and puts into list
    #         findNums = [int(d) for d in well.split()[0] if d.isdigit()]
    #         # joins nums from list [1, 0] -> 10 type = string
    #         colNum = ''.join(map(str, findNums))
    #         # this finds row
    #         row = well.split()[0][0]
    #         dest = row+str(int(colNum)+x) # row + neighbor well i.e. 1, 2
    #         p20.flow_rate.aspirate = 7.56
    #         p20.flow_rate.dispense = 7.56
    #         p20.aspirate(20, plate[well])
    #         p20.move_to(plate[well].bottom(16)) 
    #         protocol.delay(seconds=2) #equilibrate
    #         p20.touch_tip()
    #         p20.dispense(20, plate[dest].bottom(2))
    #         protocol.delay(seconds=1)
    #         # p20.move_to(plate[dest].bottom(4))
    #         p20.blow_out(plate[dest].bottom(6))
    #     p20.drop_tip()
    #     p300.drop_tip()