# all_fwd = ['first', 'second', 'third', 'four', 'five', 'six']
plate_row = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
plate_col_group1 = ['1', '2', '3']
plate_col_group2 = ['4', '5', '6']
plate_col_group3 = ['7', '8', '9']
plate_col_group4 = ['10', '11']
plate_col_group5 = ['12']

plate_col_lists = [plate_col_group1, plate_col_group2, plate_col_group3, plate_col_group4, plate_col_group5]
# plate_col_first_8 = ['1', '2', '3', '4', '5', '6', '7', '8']

# opentrons needs format in 'A1', 'A2', 'A3'

# print (plate_col_first_8[])

for h in range(3): # loop through all the plate_col group lists
    for i in range(8): # loop through the rows
        print ("add tip")
        for j in range(3): # loop through the wells, 3 wells per tip
            # print (plate_row[i] + plate_col_first_8[i])
            # source = deep well plate
            sourceWell = plate_row[i] + plate_col_lists[h][j]
            # dest = qPCR plate
            destWell = plate_row[i] + plate_col_lists[h][j]
            print ("transfer from " + sourceWell + " to " + destWell)
        print ("Drop tip")

# for i in range(8):
#     print ("add tip")
#     for j in range(3):
#         # print (plate_row[i] + plate_col_first_8[i])
#         # source = deep well plate
#         sourceWell = plate_row[i] + plate_col_group2[j]
#         # dest = qPCR plate
#         destWell = plate_row[i] + plate_col_group2[j]
#         print ("transfer from " + sourceWell + " to " + destWell)
#     print ("Drop tip")

# for i in range(8):
#     print ("add tip")
#     for j in range(3):
#         # print (plate_row[i] + plate_col_first_8[i])
#         # source = deep well plate
#         sourceWell = plate_row[i] + plate_col_group3[j]
#         # dest = qPCR plate
#         destWell = plate_row[i] + plate_col_group3[j]
#         print ("transfer from " + sourceWell + " to " + destWell)
#     print ("Drop tip")

# h  i   j    Result
# 0   0   0    A1
# 0   0   1    A2
# 0   0   2    A3
# 0   1   0    B1
# 0   1   1    B2
# 0   1   2    B3
# 0   2   0    C1
# 0   2   1    C2
# 0   2   2    C3
# 0   3   0    D1
# 0   3   1    D2
# 0   3   2    D3
# 0   4   0    E1
# 0   4   1    E2
# 0   4   2    E3
# 0   5   0    F1
# 0   5   1    F2
# 0   5   2    F3
# 0   6   0    G1
# 0   6   1    G2
# 0   6   2    G3
# 0   7   0    H1
# 0   7   1    H2
# 0   7   2    H3
# 1   0   0    A4
# 1   0   1    A5
# 1   0   2    A6
# 1   1   0    B4
# 1   1   1    B5
# 1   1   2    B6

    





# for i in range(len(all_fwd)-1):
#     # print (i)
#     # print (len(all_fwd))
#     print (all_fwd[i])
#     print (all_fwd[i+1])
#     if i == len(all_fwd)-2:
#         # print ("hooray")
#         print (all_fwd[i+1])


# wells = ['A09', 'B9', 'C2']
# sybr_wells=['A1', 'B1', 'C1', 'D1', 'E1', 'F1', 'G1', 'A4', 'B4', 'C4', 'D4', 'E4']
# probe_wells=['A7', 'B7', 'C7', 'D7', 'E7', 'F7', 'G7', 'A10', 'B10', 'C10', 'D10', 'E10']
# mm_Sybr = ['D1'] # 684ul
# mm_Probe =['D2'] # 684ul
# std_wells = [std_1, std_2, std_3, std_4, std_5, std_6, std_7, std_8, std_9, std_10, std_11, std_12]
# probe_wells=['A1', 'B1', 'C1', 'D1', 'E1', 'F1', 'G1', 'H1', 'A6', 'B6', 'C6', 'D6', 'E6']
# std_wells = [std_1, std_2, std_3, std_4, std_5, std_6, std_7, std_8, std_9, std_10, std_11, std_12, water]
# for i in range(len(probe_wells)):
#     print (i)
# calculates ideal tip height for entering liquid
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
#     offset = 12 #mm Need to add offset to ensure tip reaches below liquid level
#     for i in range(steps):
#         x = init_vol-vol_dec*i
#         vols.append(x)
#         h = p5*x**5+p4*x**4+p3*x**3+p2*x**2+p1*x**1 + p0
#         h = h-offset
#         if h < 0: # prevent negative heights
#             h = 0        
#             heights.append(h)
#         else:
#             heights.append(round(h, 1))
#     return heights

# p300_max_vol = 200


# num_of_sample_reps = 6 # min:1 | max:6
# # samp_wells = ['A1', 'B1', 'C1', 'D1', 'E1', 'F1']
# samp_sources = ['samp_1', 'samp_2', 'samp_3', 'samp_4', 'samp_5', 'samp_6', 'samp_7', 'samp_8']
# SAMP_mixes = ['SAMP_1mix', 'SAMP_2mix', 'SAMP_3mix', 'SAMP_4mix', 'SAMP_5mix', 'SAMP_6mix', 'SAMP_7mix', 'NTC_mix']


# # def plate_disp(plate, sample, row, dest):
# #     print ("Dispensing ", sample, " into ", plate, " at ", dest)

# holderList = ['holder_1', 'holder_2']
# all_stds = ['std_1', 'std_2', 'std_3', 'std_4', 'std_5', 'std_6', 'std_7', 'std_8', 'std_9', 'std_10', 'std_11', 'std_12', 'std_13', 'std_14', 'std_15', 'water']
# dest_rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'] # easier to add rows for stds rather than repeat

# for i, (stdtube, row) in enumerate(zip(all_stds, dest_rows)): #loop through all std tubes
#     start = 0
#     stop = num_of_sample_reps # max is 6 reps
#     if i <= 7: # stds 1..8 go in first column i.e. don't go to next holder
#         holder = holderList[0]
#     else: # stds 8..15, NTC
#         holder = holderList[1]
#     for y in range(start, stop):
#         source = stdtube
#         col = 2*y+1
#         dest = row+str(col)
#         print ("std:", stdtube, "start:", start, "stop:", stop)
#         print ("Aspirating from", source, "and dispensing into", holder, dest)

rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']

# #### COMMANDS ######    
# aspirate mmix to all wells in 96w plate; 15*96 = 1440ul*1.2=1728
# h_list = tip_heightsEpp(1728, 96, 15)
# well_num = 1
# # p20.pick_up_tip()
# for row in rows: #8 rows
#     for col in range(1,13): #12 cols
#         dest = row+str(col)
#         print ("dest is:", dest, well_num)
#         well_num += 1

# for i in range(0,3):
#     print ("i", i)

# for i, (sample, mixtube) in enumerate(zip(samp_sources, SAMP_mixes)):
    # print (sample, mixtube)
    # p20.pick_up_tip()
    # p300.pick_up_tip()
    # p20.aspirate(samp_XFR_to_SAMPmix, sample, rate=3.0) #aspirate from sample at rate = 2ul/sec default=7.56
    # protocol.delay(seconds=2) #equilibrate
    # p20.touch_tip()
    # p20.dispense(samp_XFR_to_SAMPmix, mixtube, rate=4.0)
    # p20.mix(2, 20, mixtube.bottom(4)) # rinse tip
    # p20.blow_out()
    # p300.move_to(mixtube.bottom(40)) #prevent tip from crashing into tube cap
    # p300.mix(3, 50, mixtube.bottom(3))
    # protocol.delay(seconds=2)
    # p300.blow_out(mixtube.bottom(10))
    # p20.move_to(mixtube.bottom(40))
    # add 20ul to strip tubes in cols 1, 3, 5...etc. Never will be more than 6 strip tubes / 96w holder
    # num_of_sample_reps is another way of stating number of strips

            
        # print ("dest:", dest)
        # print ("x:", x)
    #     p20.dispense(20, plate[dest].bottom(2), rate=4.0)
    #     protocol.delay(seconds=2)
    #     p20.move_to(plate[dest].bottom(6))
    #     p20.blow_out()
    #     p20.touch_tip()
    # p300.drop_tip()
    # p20.drop_tip()

# for i, (sample, well) in enumerate(zip(samp_sources, samp_wells)):
#     source = well
#     for x in range(1,12): # need int 1, 2, and 3
#             # find digits in well, G1 and G10 and puts into list
#             findNums = [int(d) for d in well.split()[0] if d.isdigit()]
#             # joins nums from list [1, 0] -> 10 type = string
#             colNum = ''.join(map(str, findNums))
#             # this finds row
#             row = well.split()[0][0]
#             dest = row+str(int(colNum)+x) # row + neighbor well i.e. 1, 2
#             print ("pipette from source:", source)
#             print ("pipetting into dest:", dest)
# mmix_XFR_samp_wells = 417
# for i, well in enumerate(samp_wells):
#     vols = split_asp(mmix_XFR_samp_wells, p300_max_vol) #split 237.60 into 2 asp steps
#     for vol in vols: # loop through each vol
#         # p300.flow_rate.aspirate = 40 #default
#         # p300.flow_rate.dispense = 40 #default
#         # p300.aspirate(vol, MIX_master.bottom(samp_h[i]))
#         # protocol.delay(seconds=2)
#         print ("vol:", vol, "into:", well)
#         # p300.dispense(vol, plate(well))
#         # protocol.delay(seconds=1)
#         # p300.blow_out(plate[well].bottom(10))
#         # p300.touch_tip()
# # p300.drop_tip()
# /def split_asp(tot, max_vol):
#     n = 1
#     if tot/n > max_vol:  # if total greater than max
#         while tot/n > max_vol:  # increment n until some tot/n < max_vol
#             n += 1
#             if tot/n == max_vol:  # if tot evently divided e.g. 1000
#                 subvol = tot/n
#                 return [subvol]*n
#             if tot/(n+1) < max_vol:  # if tot <> evenly divided e.g. 417.3
#                 subvol = tot/(n+1)
#                 return [subvol]*(n+1)  # return # aspiration steps
#     else:  # if total less than max
#         return [tot/n]

# def fifteen_ml_heights(init_vol, steps, vol_dec):
#     vols = []
#     heights = []
#     # these values originate from Excel spreadsheet "Volume.heights.in.15.0mL.conical.tube"
#     p0 = 6.52
#     p1 = 0.013
#     p2 = -2.11E-6
#     p3 = 3.02E-10
#     p4 = -1.95E-14
#     p5 = 4.65E-19
#     if init_vol > 1500:  # where tube begins to cone
#         offset = 5  # ensure tip contacts fluid
#     else:  # if in cone portion
#         offset = 5  # mm Need to add offset to ensure tip reaches below liquid level
#     for i in range(steps):
#         x = init_vol-vol_dec*i
#         vols.append(x)
#         h = p5*x**5+p4*x**4+p3*x**3+p2*x**2+p1*x**1 + p0
#         h = h-offset
#         if h < 8:  # prevent negative heights; go to bottom to avoid air aspirant above certain height
#             h = 1
#             heights.append(h)
#         else:
#             heights.append(round(h, 1))
#     return heights

    
# print(split_asp(3515.21, 200))
# print(fifteen_ml_heights(3696.8, 18, 195.289))