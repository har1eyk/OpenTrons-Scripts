# imports
from opentrons import protocol_api

# metadata
metadata = {
    'protocolName': 'Create Vibrio cholerae Probe Matrix for Optimization.',
    'author': 'Harley King <harley.king@luminultra.com>',
    'description': 'Create a probe conc matrix to optimize conc. F and R concentrations must be known first',
    'apiLevel': '2.12'
}
##########################
# functions
# calculates ideal tip height for entering liquid
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
    if init_vol > 1499:
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
    # Calc heights for 2mL Eppendorf tubes
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
        offset = 8 #mm Need to add offset to ensure tip reaches below liquid level
    for i in range(steps):
        x = init_vol-vol_dec*i
        vols.append(x)
        h = p5*x**5+p4*x**4+p3*x**3+p2*x**2+p1*x**1 + p0
        h = h-offset
        if h < 6: # prevent negative heights; go to bottom to avoid air aspirant above certain height
            h = 1        
            heights.append(h)
        else:
            heights.append(round(h, 1))
    return heights

# splits aspiration volume into equal parts 
# returns list with equal volumes
def split_asp(tot, max_vol):
    n =1
    if tot/n > max_vol: # if total greater than max
       while tot/n > max_vol: # increment n until some tot/n < max_vol
            n+=1
            if tot/n == max_vol: # if tot evently divided e.g. 1000
                subvol = tot/n
                return [subvol]*n
            if tot/(n+1) < max_vol: # if tot <> evenly divided e.g. 417.3
                subvol = tot/(n+1)
                return [subvol]*(n+1) # return # aspiration steps
    else: # if total less than max
        return [tot/n]

def run(protocol: protocol_api.ProtocolContext):

    # LABWARE
    fuge_rack = protocol.load_labware('vwr_24_tuberack_1500ul', '1')
    stds_rack = protocol.load_labware('vwr_24_tuberack_1500ul', '2')
    mix_rack = protocol.load_labware('vwr_24_tuberack_1500ul', '3')
    mastermix_rack = protocol.load_labware('eppendorf_24_tuberack_2000ul', '4')
    
    tiprack300 = protocol.load_labware('opentrons_96_filtertiprack_200ul', '8')
    tiprack20 = protocol.load_labware('opentrons_96_filtertiprack_20ul', '9')
    tempdeck = protocol.load_module('tempdeck', '10')
    # plate = tempdeck.load_labware('amplifyt_96_aluminumblock_300ul')
    plate = tempdeck.load_labware('abi_96_wellplate_250ul')
    # PIPETTES
    p300 = protocol.load_instrument(
        'p300_single_gen2', 'left', tip_racks=[tiprack300]
    )
    p20 = protocol.load_instrument(
        'p20_single_gen2', 'right', tip_racks=[tiprack20]
    )
     
    # REAGENTS
    # fuge_rack @ position 1
    water = fuge_rack['B2'] # 1000ul water
    probe_10uM = fuge_rack['C1'] # 300ul
    fwd_10uM = fuge_rack['C2'] # min 300ul
    rev_10uM = fuge_rack['D2'] # min 300ul
    tube_upp = fuge_rack['A4'] # e.g. 0.625uM # empty
    tube_mid = fuge_rack['A5'] # e.g. 1.25uM # empty
    tube_low = fuge_rack['A6'] # e.g. 2.5uM # empty
    probe_mix_1 = fuge_rack['C4'] # e.g. 0.625uM # empty
    probe_mix_2 = fuge_rack['C5'] # e.g. 1.25uM # empty
    probe_mix_3 = fuge_rack['C6'] # e.g. 2.5uM # empty
    probe_mix_4 = fuge_rack['D4'] # e.g. 5.0uM # empty
    probe_mix_5 = fuge_rack['D5'] # e.g. 7.5uM # empty
    probe_mix_6 = fuge_rack['D6'] # e.g. 10uM # empty
    # sds_rack @ position 2
    std_1 = stds_rack['A3'] # 990ul Water
    std_2 = stds_rack['A4'] # 900ul water
    std_3 = stds_rack['A5'] # 900ul water
    std_4 = stds_rack['A6'] # 900ul water
    std_5 = stds_rack['B1'] # 900ul water
    std_6 = stds_rack['B2'] # 900ul water 
    std_7 = stds_rack['B3'] # 900ul water
    # mix_rack @ position 3
    sN_mix = mix_rack['D1'] # empty; receives BPW_mix and water for stds 
    std_1mix = mix_rack['C3'] # empty
    std_2mix = mix_rack['C4'] # empty
    std_3mix = mix_rack['C5'] # empty
    std_4mix = mix_rack['C6'] # empty
    std_5mix = mix_rack['D3'] # empty
    std_6mix = mix_rack['D4'] # empty
    std_7mix = mix_rack['D5'] # empty
    NTC_mix = mix_rack['D6'] # empty, receives sN_mix and water as NTC
    # mastermix_rack @ position 4
    MIX_bw = mastermix_rack['D1'] # see sheet, but gen around 1705 ul; use 2mL tube
   
    
    # user inputs
    p300_max_vol = 200
    orig_F_conc = 10 # What is the starting F primer concentration? (in uM)
    orig_R_conc = 10 # What is the starting R primer concentration? (in uM)
    orig_P_conc = 10 # What is probe starting concentration? (in uM)
    P_conc = 300 # What is the probe concentration for the stds?
    P_50 = 50 # Probe at lowest conc.
    P_100 = 100 # Probe at conc
    P_200 = 200 # Probe at conc
    P_400 = 400 # Probe at conc
    P_600 = 600 # Probe at conc
    P_800 = 800 # Probe at highest conc.
    sample_reps = 24 # How many samples at each F, R conc will be run?
    tot_stds = 21 # How many wells of standards will be run? (in # wells)
    tot_NTCs = 3 # How many wells of NTCs will be run? (in # wells)
    tot_samp = 72 # How many samples with varying conditions will be run? (in # wells)
    rxn_base = 11.26 # Everything in PCR buffer (Mg2+, dNTPs, polymerase, enhancers, stabilizers, sugars, etc.). (in uL)
    rxn_base_plus_water = 14.8 # This value set from other experiments. 
    tot_rxn_vol = 20 # What is total volume of PCR reaction in plate/tube? (in ul)
    F_upp = 400 # F primer at highest concentration. (in nM)
    F_mid = 300 # What is the constant F primer concentration for standards? This should be guess or from literature or empirically determined. (in nM)
    F_low = 200 # F primer at concentration. (in nM)
    R_upp = 400 # R primer at lowest concentration. (in nM)
    R_mid = 300 # What is the constant R primer concentration for standards? This should be guess or from literature or empirically determined. (in nM)
    R_low = 200 # R primer at concentration. (in nM)
    dna_per_rxn = 2 # How much standard, positive control or NTC to add per well. 
    std_NTC_reps = 3 # How many standard and NTC replicates? (int)
    P_reps = 12 # How many wells will use probe primer at particular concentration? (int)
    P_vol_rxn = 1.6 # What vol of probe will be added to reaction? (in ul)
    P_int_vol = 50 # What is the volume of F intermediate primer in new tube? (in ul)
    percent_waste = 0.2 # What percentage waste? (decimal)
    sN_mix_waste_offset = 0.05 # How much percent_waste offset should sN_mix use? This calculated as percent_waste-sN_mix_overage = percent_waste for sN_mix_overage e.g. (20-7=13%) Should not be 0 otherwise offset = percent_waste. (decimal)
    samp_int_mix_waste_offset = 0.05 # How much percent_waste offset should R_mix use? This calculated as percent_waste-R_mix_overage = percent_waste for R_mix_overage e.g. (20-=13%) If 0, then offset = percent_waste. (decimal)
    std_NTC_waste_offset = 0.07 # How much percent_waste offset should std_NTC use? (decimal)
    mix_samp_XFR_well_waste_offset =0.08 #How much should offset be from each sample tube, upper, mid, low to the plate wells? Will receive P, be mixed and then aliquoted to 3 wells.						
    std_tube_from_which_to_add_dna = std_4 # which DNA tube should be used to add DNA from to the mastermix?

    # calcs
    tot_rxns = tot_stds + tot_NTCs + tot_samp  # Calc what is total # rxns. (int)
    tot_stds_NTC =  tot_stds + tot_NTCs # Calc number of standards and nontemplate controls. (int)
    rxn_vol_no_dna =  tot_rxn_vol-dna_per_rxn# Calc what is volume of PCR rxn with no DNA added. (in ul)
    mix_bw_tot = rxn_base_plus_water*tot_rxns*(1+percent_waste)  # Tube with mix containing base and water.
    mix_bw_XFR_mix_sn = rxn_base_plus_water*tot_stds_NTC*(1+percent_waste-sN_mix_waste_offset) # Transfer this amount from MIX_bw to new tube to receive F, R, P for std and NTC prep
    std_vol_F_per_rxn = 0.3 #F_low/1000*tot_rxn_vol/orig_F_conc # Calc adding this much F primer to each std rxn
    std_vol_R_per_rxn = 0.3 #R_low/1000*tot_rxn_vol/orig_R_conc # Calc adding this much R primer to each std rxn
    std_vol_P_per_rxn = 0.3 #P_conc/1000*tot_rxn_vol/orig_P_conc # Calc adding this much Probe to each std rxn
    std_vol_water_per_rxn = 18-(rxn_base_plus_water+std_vol_F_per_rxn+std_vol_R_per_rxn+std_vol_P_per_rxn) # How much water is added to the std_ntc reactions. Should be 18ul to receive 2ul DNA. (in ul)
    std_vol_F_mix = std_vol_F_per_rxn*tot_stds_NTC*(1+percent_waste-sN_mix_waste_offset)  # How much F primer to add to MIX_sn?
    std_vol_R_mix = std_vol_R_per_rxn*tot_stds_NTC*(1+percent_waste-sN_mix_waste_offset) # How much R primer to add to MIX_sn?
    std_vol_P_mix = std_vol_P_per_rxn*tot_stds_NTC*(1+percent_waste-sN_mix_waste_offset) # How much P primer to add to MIX_sn?
    std_vol_water_mix = std_vol_water_per_rxn*tot_stds_NTC*(1+percent_waste-sN_mix_waste_offset) # How much water  to add to MIX_sn?
    mix_sn_tot = mix_bw_XFR_mix_sn+std_vol_F_mix+std_vol_R_mix+std_vol_P_mix+std_vol_water_mix # Mix containing base+water+F,R,P. Needs to be aliquoted to std_int tubes
    mix_sn_XFR_to_std_int = std_NTC_reps*rxn_vol_no_dna*(1+percent_waste-std_NTC_waste_offset)  # transfer this amount to std_int tubes
    std_dna_XFR_to_std_int=6.72	#transfer this amount DNA to std_int_tubes to mix and aliquot to 3 wells
    dna_10x_dna_per_rxn = dna_per_rxn/10 # Dilute DNA vol added by 10x and use std_4 instead of std_5 to save vol for P and F, R at upp
    mix_bw_XFR_samp_int = sample_reps*rxn_base_plus_water*(1+percent_waste-samp_int_mix_waste_offset) # transfer this amount from mix_bw to a new sample intermediate tube for diff values of F, R conc. Need to add 2ul from DNA
    dna_XFR_samp_int = sample_reps*dna_10x_dna_per_rxn*(1+percent_waste-samp_int_mix_waste_offset) # Add this DNA to a tube and mix before aliquoting to samp_int
    F_mid_rxn = F_mid/1000*tot_rxn_vol/orig_F_conc # How much F @ mid conc to add to rxn. 
    F_mid_mix = F_mid_rxn*sample_reps*(1+percent_waste-samp_int_mix_waste_offset) # How much F to add to mix
    R_mid_rxn = R_mid/1000*tot_rxn_vol/orig_R_conc # How much R @ mid conc to add to rxn. 
    R_mid_mix =  R_mid_rxn*sample_reps*(1+percent_waste-samp_int_mix_waste_offset)# How much R to add to mix
    F_low_rxn = F_low/1000*tot_rxn_vol/orig_F_conc # How much F @ low conc to add to rxn. 
    F_low_mix = F_low_rxn*sample_reps*(1+percent_waste-samp_int_mix_waste_offset) # How much F to add to mix
    R_low_rxn = R_low/1000*tot_rxn_vol/orig_R_conc # How much R @ low conc to add to rxn. 
    R_low_mix = R_low_rxn*sample_reps*(1+percent_waste-samp_int_mix_waste_offset) # How much R to add to mix
    F_upp_rxn = F_upp/1000*tot_rxn_vol/orig_F_conc # How much F @ upp conc to add to rxn. 
    F_upp_mix = F_upp_rxn*sample_reps*(1+percent_waste-samp_int_mix_waste_offset) # How much F to add to mix
    R_upp_rxn = R_upp/1000*tot_rxn_vol/orig_R_conc # How much R @ upp conc to add to rxn. 
    R_upp_mix = R_upp_rxn*sample_reps*(1+percent_waste-samp_int_mix_waste_offset) # How much R to add to mix
    water_upp_rxn = tot_rxn_vol-(rxn_base_plus_water+dna_10x_dna_per_rxn+F_upp_rxn+R_upp_rxn+P_vol_rxn)  # How much water to add to upp rxn
    water_upp_mix = water_upp_rxn*sample_reps*(1+percent_waste-samp_int_mix_waste_offset) # How much water to add to upp mix
    water_low_rxn = 20-(dna_10x_dna_per_rxn+F_low_rxn+R_low_rxn+rxn_base_plus_water+P_vol_rxn) # How much water to add to low rxn
    water_low_mix = water_low_rxn*sample_reps*(1+percent_waste-samp_int_mix_waste_offset) # How much water to add to low mix
    water_mid_rxn = 20-(rxn_base_plus_water+P_vol_rxn+dna_10x_dna_per_rxn+F_mid_rxn+R_mid_rxn) # how much water to add to mid rxn
    water_mid_mix = water_mid_rxn*sample_reps*(1+percent_waste-samp_int_mix_waste_offset) # how much water to add to mid mix
    MIX_upp_samp_int = mix_bw_XFR_samp_int+dna_XFR_samp_int+F_upp_mix+R_upp_mix+water_upp_mix # How much in upper intermediate sample tube?
    MIX_mid_samp_int = mix_bw_XFR_samp_int+dna_XFR_samp_int+F_mid_mix+R_mid_mix+water_mid_mix # How much in middle intermediate sample tube?
    MIX_low_samp_int = mix_bw_XFR_samp_int+dna_XFR_samp_int+F_low_mix+R_low_mix+water_low_mix # How much in lower intermediate sample tube?
    mix_samp_XFR_to_well = 82.432 # How much to add to plate wells
    P_50_int_conc = P_50/1000*tot_rxn_vol/P_vol_rxn # What intermediate (int) concentration of  Probe is needed such that by adding 1.6ul I obtain a final concentration of 50, 100, 200…etc in rxn well? (in uM)
    P_100_int_conc = P_100/1000*tot_rxn_vol/P_vol_rxn # What intermediate (int) concentration of  Probe is needed such that by adding 1.6ul I obtain a final concentration of 50, 100, 200…etc in rxn well? (in uM)
    P_200_int_conc = P_200/1000*tot_rxn_vol/P_vol_rxn # What intermediate (int) concentration of  Probe is needed such that by adding 1.6ul I obtain a final concentration of 50, 100, 200…etc in rxn well? (in uM)
    P_400_int_conc = P_400/1000*tot_rxn_vol/P_vol_rxn # What intermediate (int) concentration of  Probe is needed such that by adding 1.6ul I obtain a final concentration of 50, 100, 200…etc in rxn well? (in uM)
    P_600_int_conc = P_600/1000*tot_rxn_vol/P_vol_rxn # What intermediate (int) concentration of  Probe is needed such that by adding 1.6ul I obtain a final concentration of 50, 100, 200…etc in rxn well? (in uM)
    P_800_int_conc = P_800/1000*tot_rxn_vol/P_vol_rxn # What intermediate (int) concentration of  Probe is needed such that by adding 1.6ul I obtain a final concentration of 50, 100, 200…etc in rxn well? (in uM)
    P_50_int_primer = P_50_int_conc*P_int_vol/orig_P_conc # What amount of primer should be added to generate int F primer conc? (in ul)
    P_100_int_primer = P_100_int_conc*P_int_vol/orig_P_conc # What amount of water should be added to generate int F primer conc? (in ul)
    P_200_int_primer = P_200_int_conc*P_int_vol/orig_P_conc # What amount of primer should be added to generate int F primer conc? (in ul)
    P_400_int_primer = P_400_int_conc*P_int_vol/orig_P_conc # What amount of water should be added to generate int F primer conc? (in ul)
    P_600_int_primer = P_600_int_conc*P_int_vol/orig_P_conc # What amount of primer should be added to generate int F primer conc? (in ul)
    P_800_int_primer = P_800_int_conc*P_int_vol/orig_P_conc # What amount of water should be added to generate int F primer conc? (in ul)
    P_50_int_water = P_int_vol-P_50_int_primer # What amount of primer should be added to generate int F primer conc? (in ul)
    P_100_int_water = P_int_vol-P_100_int_primer # What amount of water should be added to generate int F primer conc? (in ul)
    P_200_int_water = P_int_vol-P_200_int_primer # What amount of primer should be added to generate int F primer conc? (in ul)
    P_400_int_water = P_int_vol-P_400_int_primer # What amount of water should be added to generate int F primer conc? (in ul)
    P_600_int_water = P_int_vol-P_600_int_primer # What amount of primer should be added to generate int F primer conc? (in ul)
    P_800_int_water = P_int_vol-P_800_int_primer # What amount of water should be added to generate int F primer conc? (in ul)
    p_int_XFR_to_well =	P_vol_rxn*4*(1+percent_waste-mix_samp_XFR_well_waste_offset) # What amount of probe intermediate to add to bolus in wells?

    #checks
    print ("mix_bw_tot", mix_bw_tot)
    print ("mix_sn_tot", mix_sn_tot)
    print ("mix_bw_XFR_samp_int", mix_bw_XFR_samp_int)
    print ("MIX_upp_samp_int", MIX_upp_samp_int)
    print ("MIX_low_samp_int", MIX_low_samp_int)   
    print ("MIX_low_samp_int", MIX_low_samp_int)
    print ("dna_XFR_samp_int", dna_XFR_samp_int)
    # print ('std_mix_heights', std_mix_heights)
    print ('mix_sn_tot', mix_sn_tot)
    print ('mix_bw_XFR_mix_sn', mix_bw_XFR_mix_sn)
    print ('std_vol_F_mix', std_vol_F_mix)
    print ('std_dna_XFR_to_std_int', std_dna_XFR_to_std_int)
    # lists
    # plate_col = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']
    F_samp_vols = [F_upp_mix, F_mid_mix, F_low_mix]
    R_samp_vols = [R_upp_mix, R_mid_mix, R_low_mix]
    plate_rows = ['A', 'B', 'C', 'D', 'E', 'F']
    # all_fwd = [fwd_1, fwd_2, fwd_3, fwd_4, fwd_5, fwd_6]
    std_tubes = [std_1, std_2, std_3, std_4, std_5, std_6, std_7, water]
    std_mixes = [std_1mix, std_2mix, std_3mix, std_4mix, std_5mix, std_6mix, std_7mix, NTC_mix]
    std_wells = ['G1', 'G4', 'G7', 'G10', 'H1', 'H4', 'H7', 'H10']
    samp_tubes = [tube_upp, tube_mid, tube_low]
    probe_mixes = [probe_mix_1, probe_mix_2, probe_mix_3, probe_mix_4, probe_mix_5, probe_mix_6]
    P_in_mix = [P_50_int_primer, P_100_int_primer, P_200_int_primer, P_400_int_primer, P_600_int_primer, P_800_int_primer]
    W_in_mix = [P_50_int_water, P_100_int_water, P_200_int_water, P_400_int_water, P_600_int_water, P_800_int_water]
    
    # #### COMMANDS ######
    # prepare sN_mix
    # add MIX_bw to sN_mix tube
    p300.pick_up_tip()
    MIX_bw_heights = tip_heightsEpp(mix_bw_tot, len(split_asp(mix_bw_XFR_mix_sn, p300_max_vol)), split_asp(mix_bw_XFR_mix_sn, p300_max_vol)[0])
    p300.mix(3, 200, MIX_bw.bottom(MIX_bw_heights[0]))
    for j in range(len(split_asp(mix_bw_XFR_mix_sn, p300_max_vol))):
        amt = split_asp(mix_bw_XFR_mix_sn, p300_max_vol)[j]
        p300.aspirate(amt, MIX_bw.bottom(MIX_bw_heights[j]), rate=0.8)
        protocol.delay(seconds=2)
        h = tip_heights(amt+amt*j, 1, 0)[0]
        p300.dispense(amt, sN_mix.bottom(h+5), rate=0.8)
        protocol.delay(seconds=2)
        p300.blow_out(sN_mix.bottom(20)) # want to be above liquid level
        p300.touch_tip()
    p300.drop_tip()
    # transfer water to sN__mix
    p300.transfer(
        std_vol_water_mix, # 27.6ul
        water.bottom(20),
        sN_mix.bottom(tip_heights(mix_bw_XFR_mix_sn, 1, 0)[0]),
        blow_out=True,
        blowout_location='destination well')

    p20.transfer(
        std_vol_F_mix, #at 300nM, 8.3ul
        fwd_10uM.bottom(3), 
        sN_mix.bottom(tip_heights(mix_bw_XFR_mix_sn, 1, 0)[0]),
        blow_out=True,
        mix_after=(2, 10),
        blowout_location='destination well')
    # transfer R primer @ std conditions to sN__mix
    p20.transfer( #some resid fluid on outside
        std_vol_R_mix, #at 300nM, 8.3ul
        rev_10uM.bottom(3), 
        sN_mix.bottom(tip_heights(mix_bw_XFR_mix_sn, 1, 0)[0]),
        blow_out=True,
        mix_after=(2, 10), 
        blowout_location='destination well')
        # transfer Probe @ std conditions to sN__mix
    p20.transfer( #some resid fluid on outside
        std_vol_P_mix, #at 300nM, 8.3ul
        probe_10uM.bottom(3), 
        sN_mix.bottom(tip_heights(mix_bw_XFR_mix_sn, 1, 0)[0]),
        blow_out=True,
        mix_after=(2, 20),
        blowout_location='destination well')
    
    # transfer sN_mix to intermediate tubes (std_mixes)
    std_mix_heights = tip_heights(mix_sn_tot, len(std_mixes), mix_sn_XFR_to_std_int)#[13,11,8,6,4,2,0]
    p300.pick_up_tip()
    p300.mix(3, 200, sN_mix.bottom(5)) #4mm from bottom
    p300.mix(3, 200, sN_mix.bottom(8)) #8mm from bottom
    p300.mix(3, 200, sN_mix.bottom(std_mix_heights[0])) #13mm from bottom
    p300.touch_tip()
    # p300.well_bottom_clearance.aspirate = std_mix_heights[0] #mm 
    for tube, h in zip(std_mixes, std_mix_heights):
        # p300.well_bottom_clearance.aspirate = h #mm
        p300.aspirate(mix_sn_XFR_to_std_int, sN_mix.bottom(h)) # 18 * 3 * 1.12-0.05= 54 + 6 =60ul
        protocol.delay(seconds=2) #tip equilibrate
        p300.move_to(sN_mix.bottom(35)) # excess tip fluid condense 
        protocol.delay(seconds=3) #tip droplets slide
        p300.touch_tip()
        p300.dispense(mix_sn_XFR_to_std_int, tube)
        protocol.delay(seconds=1) #tip droplets slide
        p300.move_to(sN_mix.bottom(12)) # excess tip fluid condense 
        protocol.delay(seconds=1) #tip droplets slide
        p300.move_to(sN_mix.bottom(tip_heights(mix_sn_XFR_to_std_int,1,1)[0])) # remove excees by touching tip to fluid level
    p300.drop_tip()
   
    # transfer std DNA into intermediate std_mixes tubes and then to plate
    for std, intTube, well in zip(std_tubes, std_mixes, std_wells):
        p20.pick_up_tip()
        p300.pick_up_tip()
        p20.aspirate(std_dna_XFR_to_std_int, std, rate=0.75) #aspirate from std_1 into std_mix (intermediate tube) e.g. 6.42 ul
        protocol.delay(seconds=2) #equilibrate
        p20.touch_tip()
        p20.dispense(std_dna_XFR_to_std_int, intTube, rate=0.75)
        # p20.move_to(intTube.bottom(3))
        p20.mix(2, 20, intTube.bottom(3)) #ensure vol in tip in intTube and washed
        p20.blow_out()
        p300.move_to(intTube.bottom(40)) #prevent tip from crashing into tube cap
        p300.mix(7, 50, intTube.bottom(1))
        protocol.delay(seconds=2)
        # p300.move_to(intTube.bottom(10)) #prevent air bubbles in mmix during blow out
        p300.blow_out(intTube.bottom(10))
        p20.move_to(intTube.bottom(40))
        for x in range(0,3): # need int 1, 2, and 3
            p20.aspirate(20, intTube, rate=0.75) 
            protocol.delay(seconds=2) #equilibrate
            # find digits in well, G1 and G10 and puts into list
            findNums = [int(i) for i in well.split()[0] if i.isdigit()]
            # joins nums from list [1, 0] -> 10 type = string
            colNum = ''.join(map(str, findNums))
            # this finds row
            row = well.split()[0][0]
            dest = row+str(int(colNum)+x) # row + neighbor well i.e. 1, 2
            p20.dispense(20, plate[dest].bottom(1), rate=0.75)
            p20.move_to(plate[dest].bottom(4))
            p20.blow_out()
            # p20.touch_tip()
        p300.drop_tip()
        p20.drop_tip()

    # create samp_int tube mixes. sample intermediate
    # first add DNA from a std tube e.g. std_4
    p20.transfer(
        dna_XFR_samp_int*3, ## ~3 sets of 24 samples about 5*3 = 15ul
        std_tube_from_which_to_add_dna.bottom(2), 
        MIX_bw.bottom(tip_heights(mix_bw_tot-mix_bw_XFR_mix_sn, 1, 0)[0]),
        mix_after=(2, dna_XFR_samp_int),
        blow_out=True,
        blowout_location='destination well')
    # Three tubes created for upper, mid, lower F,R concentrations
    p300.pick_up_tip()
    h = tip_heightsEpp(mix_bw_tot-mix_bw_XFR_mix_sn, len(split_asp(mix_bw_XFR_samp_int, p300_max_vol)), 408.48)#split_asp(mix_bw_XFR_samp_int, p300_max_vol)[0])
    p300.mix(3, 200, MIX_bw.bottom(4)) # need to thoroughly mix DNA in tube
    p300.mix(3, 200, MIX_bw.bottom(8)) # need to thoroughly mix DNA in tube
    p300.mix(5, 200, MIX_bw.bottom(h[0]-10)) # need to thoroughly mix DNA in tube
    for tube in samp_tubes:
        for j in range(len(split_asp(mix_bw_XFR_samp_int, p300_max_vol))): # split_asp is a function that returns equally divided aspirations
            amt = split_asp(mix_bw_XFR_samp_int, p300_max_vol)[j]
            p300.aspirate(amt, MIX_bw.bottom(2))
            protocol.delay(seconds=2)
            # h = tip_heights(amt+amt*j, 1, 0)[0] # adjust tip height depending on dispenses
            p300.dispense(amt, tube.bottom(3)) # want tip to be just a little above dispense
            p300.blow_out(tube.bottom(15)) # want to be above liquid level
            p300.touch_tip()
    p300.drop_tip()
    # add F, R primers into samp_int tubes first with upper, mid (p300 vols), then with low (p20 vols)
    for i in range(2):
        h = tip_heights(mix_bw_XFR_samp_int,1,0)[0]
        p300.transfer(
            F_samp_vols[i],
            fwd_10uM.bottom(2),
            samp_tubes[i].bottom(h),
            mix_after=(2, 100),
            new_tip='always'
        )
        p300.transfer(
            R_samp_vols[i],
            rev_10uM.bottom(2),
            samp_tubes[i].bottom(h),
            mix_after=(2, R_samp_vols[i]),
            new_tip='always'
        )
    # F primer to low tube
    p20.transfer(
        F_samp_vols[-1],
        fwd_10uM.bottom(2),
        samp_tubes[-1].bottom(tip_heights(mix_bw_XFR_samp_int,1,0)[0]),
        mix_after=(2, F_samp_vols[-1]),
        new_tip='always'
    )
    # R primer to low tube
    p20.transfer(
        R_samp_vols[-1],
        rev_10uM.bottom(2),
        samp_tubes[-1].bottom(tip_heights(mix_bw_XFR_samp_int,1,0)[0]),
        mix_after=(2, R_samp_vols[-1]),
        new_tip='always'
    )
    
    # add water, dispense samp_int tubes containing F,R, water into plate
    # into each 1st well in plate, A1, B1..F1 then tube_mid into A5, B5..F5
    for i, (tube, wvol) in enumerate(zip(samp_tubes, list([water_upp_mix, water_mid_mix, water_low_mix]))):
        p300.pick_up_tip()
        p300.aspirate(wvol, water.bottom(10))
        p300.dispense(wvol, tube.bottom(10))
        p300.mix(2, 200, tube.bottom(4)) 
        p300.mix(3, 200, tube.bottom(7)) 
        p300.mix(3, 200, tube.bottom(10)) 
        for j, row in enumerate(plate_rows):
            h = tip_heights(MIX_upp_samp_int, len(plate_rows), mix_samp_XFR_to_well) #3rd asp is low correct with small tot vol
            print (h)
            dest = row+str(4*i+1)
            p300.aspirate(mix_samp_XFR_to_well, tube.bottom(h[j]))
            protocol.delay(seconds=2) # tip equilibrate
            p300.move_to(tube.bottom(25))
            protocol.delay(seconds=2)
            p300.touch_tip() # bpwd_rxn*row reps (12) * waste = 16.8*12*(1+.12-0.05)=
            p300.dispense(mix_samp_XFR_to_well, plate[dest].bottom(1))
            protocol.delay(seconds=1)
            p300.blow_out(plate[dest].bottom(10))
            p300.touch_tip()
        p300.drop_tip()
    
    # now that PCR reactions are chillin' at 4C, make Probe int tubes
    # Mix 50ul 'probe' dilutions in tube by adding water and "probe" tube as shown in schedule
    # add water
    p300.pick_up_tip()
    for tube, wvol in zip(probe_mixes[0:4], W_in_mix[0:4]):  # first 4 have vol > 20
        p300.transfer(
            wvol,
            water.bottom(15),
            tube.bottom(1), 
            blow_out=False, #this was creating air bubbles
            blowout_location='destination well',
            new_tip='never')
    p300.drop_tip()
    p20.pick_up_tip()
    # for tube, wvol in probe_mixes[4], W_in_mix[4]:  # 5th item has vol < 20ul
    p20.transfer(
        W_in_mix[4],
        water.bottom(15),
        probe_mixes[4].bottom(1), 
        blow_out=False,
        blowout_location='destination well',
        new_tip='never')
    p20.drop_tip()
    # add primer
    p20.pick_up_tip()
    for tube, pvol in zip(probe_mixes[0:3], P_in_mix[0:3]): # first three tubes have vol < 20ul
        p20.transfer(
            pvol,
            probe_10uM.bottom(2),
            tube.bottom(3),
            blow_out=False,
            mix_after=(2, pvol),
            blowout_location='destination well',
            new_tip='never'
        )
    p20.drop_tip()
    # next tubes have vol > 20
    p300.pick_up_tip()
    for tube, pvol in zip(probe_mixes[3:], P_in_mix[3:]): # item 3 till end    
        p300.transfer(
            pvol,
            probe_10uM.bottom(2),
            tube.bottom(2), 
            blow_out=False,
            blowout_location='destination well',
            new_tip='never')
    p300.drop_tip()
   
    # Add probe to wells. mix, aliquot to adjacent wells
    P_mix_h = tip_heights(P_int_vol,1,0)
    for i, (tube, row) in enumerate (zip(probe_mixes, plate_rows)):
        p300.pick_up_tip()
        p20.pick_up_tip()
        p300.flow_rate.aspirate = 60 
        p300.flow_rate.dispense = 60 #don't want air bubbles
        p300.mix(3,30, tube.bottom(P_mix_h[0])) # mix F primer tube, 100ul in tube
        p300.blow_out(tube.bottom(P_mix_h[0]+6))
        p300.touch_tip()
        for j in range(2): # asp and disp into wells
            p20.move_to(tube.bottom(40))
            if j==0: # wells A1 and A5
                dest = row+str(j+1)
                nextWell = row + str(j+5)
                p20.aspirate(p_int_XFR_to_well*2, tube.bottom(2)) # ~7ul aspirate from P int tube to wells
                protocol.delay(seconds=2)
                p20.move_to(tube.bottom(2)) # relieve pressure if tip against tube 
                p20.dispense(p_int_XFR_to_well, plate[dest].bottom(2))
                protocol.delay(seconds=1)
                p20.touch_tip()
                p20.dispense(p_int_XFR_to_well, plate[nextWell].bottom(2))
                protocol.delay(seconds=2)
                p20.blow_out(plate[nextWell].bottom(6))
                p20.touch_tip()
                p20.drop_tip()
                p20.pick_up_tip()
            else: # well A9
                dest = row+str(j+8)
                p20.aspirate(p_int_XFR_to_well, tube.bottom(1)) # ~7ul aspirate from P int tube to wells
                p20.move_to(tube.bottom(2)) # relieve pressure if tip against tube 
                protocol.delay(seconds=2)
                p20.touch_tip()
                p20.dispense(p_int_XFR_to_well, plate[dest])
                protocol.delay(seconds=2)
                p20.blow_out(plate[dest].bottom(6))
                p20.touch_tip()
        for k in range(3): # need int 0, 1, 2. Looping through bolus in row (3)
            swell = row+str(4*k+1) #source well: A1, A5, A9
            p300.move_to(plate[swell].bottom(30))
            p300.mix(3, 70, plate[swell].bottom(3))
            p300.mix(1, 70, plate[swell].bottom(2)) #slow mix to avoid/remove bubbles
            p300.blow_out(plate[swell].bottom(6))
            for m in range(1,4): # want int 1, 2, 3
                dwell = row+str(4*k+1+m) # loop through dispensing wells
                p20.move_to(plate[swell].bottom(40))
                p20.aspirate(20, plate[swell].bottom(1))
                protocol.delay(seconds=1)
                p20.dispense(20, plate[dwell].bottom(2))
                protocol.delay(seconds=1)
                p20.move_to(plate[dwell].bottom(6))
                p20.blow_out()
                p20.touch_tip()
        p20.drop_tip()
        p300.drop_tip()