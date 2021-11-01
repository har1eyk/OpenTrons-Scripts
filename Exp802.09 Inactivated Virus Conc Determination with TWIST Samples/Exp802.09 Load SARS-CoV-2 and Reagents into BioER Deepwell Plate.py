# not complete

# # imports
# from opentrons import protocol_api

# # metadata
# metadata = {
#     'protocolName': 'Load Samples and Reagents into BioER Deepwell Plate.',
#     'author': 'Harley King <harley.king@luminultra.com>',
#     'description': 'Taking series dilution of SARS-CoV-2 and adding it to BioER 96w Deepwell plate for processsing on E32.',
#     'apiLevel': '2.11'
# }

# ##########################
# def tip_heightsEpp(init_vol, steps, vol_dec):
#     vols = []
#     heights = []
#     # these values originate from Excel spreadsheet "Exp803..."
#     p0=-0.272820744
#     p1=0.019767959
#     p2=2.00442E-06
#     p3=-8.99691E-09
#     p4=6.72776E-12
#     p5=-1.55428E-15
#     if init_vol > 2000:
#         offset = 12 # model out of range; see sheet
#     else:
#         offset = 11 #mm Need to add offset to ensure tip reaches below liquid level
#     for i in range(steps):
#         x = init_vol-vol_dec*i
#         vols.append(x)
#         h = p5*x**5+p4*x**4+p3*x**3+p2*x**2+p1*x**1 + p0
#         h = h-offset
#         if h < 6: # prevent negative heights; go to bottom to avoid air aspirant above certain height
#             h = 1        
#             heights.append(h)
#         else:
#             heights.append(round(h, 1))
#     return heights
# def tip_heights(init_vol, steps, vol_dec):
#     vols = []
#     heights = []
#     # these values originate from Excel spreadsheet "Exp803..."
#     p0=0.029502064
#     p1=0.084625954
#     p2=-0.000174864
#     p3=2.18373E-07
#     p4=-1.30599E-10
#     p5=2.97839E-14
#     if init_vol > 1499:
#         offset = 14 # model out of range; see sheet
#     else:
#         offset = 7 #mm Need to add offset to ensure tip reaches below liquid level
#     for i in range(steps):
#         x = init_vol-vol_dec*i
#         vols.append(x)
#         h = p5*x**5+p4*x**4+p3*x**3+p2*x**2+p1*x**1 + p0
#         h = h-offset
#         if h < 10: # prevent negative heights; go to bottom to avoid air aspirant above certain height
#             h = 1       
#             heights.append(h)
#         else:
#             heights.append(round(h, 1))
#     return heights

# # splits aspiration volume into equal parts 
# # returns list with equal volumes
# def split_asp(tot, max_vol):
#     n =1
#     if tot/n > max_vol: # if total greater than max
#        while tot/n > max_vol: # increment n until some tot/n < max_vol
#             n+=1
#             if tot/n == max_vol: # if tot evently divided e.g. 1000
#                 subvol = tot/n
#                 return [subvol]*n
#             if tot/(n+1) < max_vol: # if tot <> evenly divided e.g. 417.3
#                 subvol = tot/(n+1)
#                 return [subvol]*(n+1) # return # aspiration steps
#     else: # if total less than max
#         return [tot/n]
        
# def run(protocol: protocol_api.ProtocolContext):

#     # LABWARE
#     sample_rack = protocol.load_labware('opentrons_24_tuberack_eppendorf_2ml_safelock_snapcap', '11')
#     stds_rack = protocol.load_labware('vwr_24_tuberack_1500ul', '2')
#     tiprack300 = protocol.load_labware('opentrons_96_filtertiprack_200ul', '8')
#     tiprack20 = protocol.load_labware('opentrons_96_filtertiprack_20ul', '9')
#     tempdeck = protocol.load_module('tempdeck', '10')
#     # pcr_plate = tempdeck.load_labware('abi_96_wellplate_250ul')
#     deep_plate1 = protocol.load_labware('bioer_96_wellplate_2200ul', '1')
#     deep_plate2 = protocol.load_labware('bioer_96_wellplate_2200ul', '4')

#     # PIPETTES
#     p20 = protocol.load_instrument(
#         'p20_single_gen2', 'right', tip_racks=[tiprack20]
#     )
#     p300 = protocol.load_instrument(
#         'p300_single_gen2', 'left', tip_racks=[tiprack300]
#     )
#     # REAGENTS   
#     s_std_1 = sample_rack['A1'] 
#     s_std_2 = sample_rack['A2'] 
#     s_std_3 = sample_rack['A3'] 
#     s_std_4 = sample_rack['A4'] 
#     s_std_5 = sample_rack['A5'] 
#     s_std_6 = sample_rack['A6']  
#     s_std_7 = sample_rack['B1'] 
#     s_std_8 = sample_rack['B2'] 
        
#     # CALCS
#     sample_vol_per_well = 300
#     lysis_buffer_per_well = 400
#     etoh_vol_per_well = 400
#     wash_one_sol_per_well = 1000
#     wash_two_sol_per_well = 1000
#     wash_three_etoh_per_well = 1000
#     elution_buffer_per_well = 100
#     magnetic_beads_per_well = 40
#     p300_max_vol = 200
   
#     # LISTS
#     rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
#     tot_sample_plates = [deep_plate1, deep_plate2]
#     all_samples = [s_std_1, s_std_2, s_std_3, s_std_4, s_std_5, s_std_6, s_std_7, s_std_8]

#     # USER INPUTS
#     tot_samples = 8
#     multiples_of_eight = 3

        
#     # #### COMMANDS ######    
#     # move 300ul of SARS dilutions from  to deepwell plate
#     for sample in all_samples: #loop through all samples
#         p300.pick_up_tip()
#         s_h_list = tip_heights(900, 6, sample_vol_per_well) # 900, 3, 300
#         # s_vols_list = split_asp(sample_vol_per_well, p300_max_vol) #split 300 into 2 equal asp/dispense steps
#         for k in range(multiples_of_eight): # loop through all destinations
#             dest = 
#             for j in range (2): # loop through twice for 300ul
#                 source = sample
#                 # dest = tot_ww_plates[j*(j-1)][]
#                 dest = tot_sample_plates[0]['A1']
#                 p300.aspirate(150, source.bottom(s_h_list[j]))
#                 p300.dispense(150, dest.bottom(2))
#                 p300.blow_out(dest.bottom(14))
#                 p300.touch_tip()
#         p300.drop_tip()
    


#     # well_num = 1
#     # p20.pick_up_tip()
#     # for row in rows: #8 rows
#     #     for col in range(1,13): #12 cols
#     #         dest = row+str(col)
#     #         p20.aspirate(15, LU_Mix.bottom(h_list[well_num-1]), rate=0.75)
#     #         protocol.delay(seconds=1) #head vol for more accurate pipetting
#     #         p20.move_to(LU_Mix.bottom(38))
#     #         protocol.delay(seconds=1) #equilibrate
#     #         p20.touch_tip(v_offset=-4)
#     #         p20.dispense(15, pcr_plate[dest].bottom(1))
#     #         p20.blow_out(pcr_plate[dest].bottom(8))
#     #         p20.touch_tip()
#     #         well_num += 1
#     # p20.drop_tip()

#     # for x, ww_plate in enumerate(tot_ww_plates):
#     #     for col in range(0,2):
#     #         for row in rows:
#     #             p20.pick_up_tip()
#     #             source = row + str(6*col+5) #A5, B5, C5
#     #             dest1 = row + str(6*x+3*col+1) #A1, #A2, #A3
#     #             dest2 = row + str(6*x+3*col+2)
#     #             dest3 = row + str(6*x+3*col+3)
#     #             p20.aspirate(18, ww_plate[source].bottom(1), rate=0.75)
#     #             protocol.delay(seconds=2) #equilibrate
#     #             p20.touch_tip()
#     #             p20.dispense(5, pcr_plate[dest1].bottom(1))
#     #             p20.touch_tip()    
#     #             p20.dispense(5, pcr_plate[dest2].bottom(1))    
#     #             p20.touch_tip()    
#     #             p20.dispense(5, pcr_plate[dest3].bottom(1))    
#     #             p20.touch_tip()    
#     #             p20.drop_tip()


