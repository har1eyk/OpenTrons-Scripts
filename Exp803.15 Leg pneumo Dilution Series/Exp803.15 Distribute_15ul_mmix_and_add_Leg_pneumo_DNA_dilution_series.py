# imports
from re import I
from opentrons import protocol_api

# metadata
metadata = {
    'protocolName': 'Distribute 15ul Leg pneumo qPCR mmix and Add Dilution Series.',
    'author': 'Harley King <harley.king@luminultra.com>',
    'description': 'Aliquoting 15ul Leg pneumo qPCR mmix to chilled PCR plate and adding 5ul sample Leg pneumo pos control DNA.',
    'apiLevel': '2.12'
}

##########################
def tip_heightsEpp(init_vol, steps, vol_dec):
    vols = []
    heights = []
    # these values originate from Excel spreadsheet "Exp803..."
    p0=-0.272820744
    p1=0.019767959
    p2=2.00442E-06
    p3=-8.99691E-09
    p4=6.72776E-12
    p5=-1.55428E-15
    if init_vol > 2000:
        offset = 12 # model out of range; see sheet
    else:
        offset = 11 #mm Need to add offset to ensure tip reaches below liquid level
    for i in range(steps):
        x = init_vol-vol_dec*i
        vols.append(x)
        h = p5*x**5+p4*x**4+p3*x**3+p2*x**2+p1*x**1 + p0
        h = h-offset
        if h < 7: # prevent negative heights; go to bottom to avoid air aspirant above certain height
            h = 1        
            heights.append(h)
        else:
            heights.append(round(h, 1))
    return heights

def tip_heights(init_vol, steps, vol_dec):
    vols = []
    heights = []
    # these values originate from Excel spreadsheet "Exp803..."
    p0=0.029502064
    p1=0.084625954
    p2=-0.000174864
    p3=2.18373E-07
    p4=-1.30599E-10
    p5=2.97839E-14
    if init_vol > 1500:
        offset = 14 # model out of range; see sheet
    else:
        offset = 7 #mm Need to add offset to ensure tip reaches below liquid level
    for i in range(steps):
        x = init_vol-vol_dec*i
        vols.append(x)
        h = p5*x**5+p4*x**4+p3*x**3+p2*x**2+p1*x**1 + p0
        h = h-offset
        if h < 8: # prevent negative heights; go to bottom to avoid air aspirant above certain height
            h = 1        
            heights.append(h)
        else:
            heights.append(round(h, 1))
    return heights

def run(protocol: protocol_api.ProtocolContext):

    # LABWARE
    tiprack20 = protocol.load_labware('opentrons_96_filtertiprack_20ul', '9')
    
    tempdeck = protocol.load_module('tempdeck', '1')
    pcr_plate = tempdeck.load_labware('abi_96_wellplate_250ul')

    mix_rack =  protocol.load_labware('opentrons_24_tuberack_eppendorf_2ml_safelock_snapcap', '4')
    stds_rack = protocol.load_labware('vwr_24_tuberack_1500ul', '2')

    # PIPETTES
    p20 = protocol.load_instrument(
        'p20_single_gen2', 'right', tip_racks=[tiprack20]
    )
    
    # REAGENTS   
    # stds_rack
    a_std_1 = stds_rack['A1']  # 980ul Water + 20ul 
    a_std_2 = stds_rack['A2']  # from previous program, 750ul
    a_std_3 = stds_rack['A3']  # from previous program, 750ul
    a_std_4 = stds_rack['A4']  # from previous program, 750ul
    a_std_5 = stds_rack['A5']  # from previous program, 750ul
    a_std_6 = stds_rack['A6']  # from previous program, 750ul
    a_std_7 = stds_rack['B1']  # from previous program, 750ul
    a_std_8 = stds_rack['B2']  # from previous program, 750ul
    a_std_9 = stds_rack['B3']  # from previous program, 750ul
    a_std_10 =stds_rack['B4']  # from previous program, 750ul
    a_std_11 =stds_rack['B5']  # from previous program, 750ul
    a_std_12 =stds_rack['B6']  # from previous program, 750ul
    a_std_13 =stds_rack['C1']  # from previous program, 750ul
    a_std_14 =stds_rack['C2']  # from previous program, 750ul
    a_std_15 =stds_rack['C3']  # from previous program, 750ul
    
    # mix_rack
    LU_Mix = mix_rack['D1'] # LU MasterMix; must be in the same tubes as the a_stds, "2mL Epp snap cap" 15*96*1.1ul = 1710ul
    neg = mix_rack['A1'] # Negative Control NFW 1000ul in 2mL Epp snap cap

    # LISTS
    rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
    stds = [a_std_1, a_std_2, a_std_3, a_std_4, a_std_5, a_std_6,
            a_std_7, a_std_8, a_std_9, a_std_10, a_std_11, a_std_12, a_std_13, a_std_14, a_std_15, neg]
    std_locations = ['A1', 'B1', 'C1', 'D1', 'E1', 'F1', 'G1', 'H1','A7', 'B7', 'C7', 'D7', 'E7', 'F7', 'H7', 'G7']
    # #### COMMANDS ######    
    # aspirate mmix to all wells in 96w plate; 15*96 = 1440ul*1.10=1584ul
    h_list = tip_heightsEpp(1710, 96, 15)
    well_num = 1
    p20.pick_up_tip()
    p20.mix(3, 20, LU_Mix.bottom(h_list[well_num-1]))
    for row in rows: #8 rows
        for col in range(1,13): #12 cols
            dest = row+str(col)
            p20.aspirate(15, LU_Mix.bottom(h_list[well_num-1]), rate=0.75)
            protocol.delay(seconds=1) #head vol for more accurate pipetting
            p20.move_to(LU_Mix.bottom(38))
            protocol.delay(seconds=2) #equilibrate
            p20.touch_tip(v_offset=-3, speed=30)
            p20.dispense(15, pcr_plate[dest].bottom(1))
            p20.blow_out(pcr_plate[dest].bottom(8))
            protocol.delay(seconds=1) #equilibrate
            p20.move_to(pcr_plate[dest].bottom(3)) # touch to remove fluid from tip
            well_num += 1
    p20.drop_tip()

    # add 5ul of Leg pneumo dilution series to each well in 96w plate 
    j = 0   
    tubeHeight = tip_heights(750, 2, 15)
    negTubeHeight = tip_heightsEpp(1000, 2, 15)
    
    for i, (std, row) in enumerate(zip(stds, 2*rows)):
        j = 6 if i > 7 else 0 # need a way to go from A1-->A7
        height = tubeHeight if i < 14 else negTubeHeight  # need to accomodate diff tubes and volume levels
        for k in range(2): # 3 sets of 2
            p20.pick_up_tip()
            p20.mix(3, 20, std.bottom(height[k])) # more accurate dispense with pre-moisten
            p20.aspirate(20, std.bottom(height[k]))
            p20.touch_tip(v_offset=-3, speed=30)
            print ('height', height)
            protocol.delay(seconds=1) # equilibrate
            dest1 = row+str(3*k+1+j)
            dest2 = row+str(3*k+2+j)
            dest3 = row+str(3*k+3+j)
            p20.dispense(5, pcr_plate[dest1].bottom(1), rate=0.75)
            p20.dispense(5, pcr_plate[dest2].bottom(1), rate=0.75)
            p20.dispense(5, pcr_plate[dest3].bottom(1), rate=0.75)
            p20.drop_tip()

# j     i    k    dest1    dest2    dest3
# 0     0    0     A1       A2       A3
# 0     0    1     A4       A5       A6
# 0     1    0     B1       B2       B3
# 0     1    1     B4       B5       B6
# 0     2    0     C1       C2       C3
# 0     2    1     C4       C5       C6
# 0     3    0     D1       D2       D3
# 0     3    1     D4       D5       D6
# 0     4    0     E1       E2       E3
# 0     4    1     E4       E5       E6
# 0     5    0     F1       F2       F3
# 0     5    1     F4       F5       F6
# 0     6    0     G1       G2       G3
# 0     6    1     G4       G5       G6
# 0     7    0     H1       H2       H3
# 0     7    1     H4       H5       H6



    
