# imports
from opentrons import protocol_api

# metadata
metadata = {
    'protocolName': 'Create Primer Conc Matrix for Optimization in 50ul Volume',
    'author': 'Harley King <harley.king@luminultra.com>',
    'description': 'Create a fwd, rev primer conc matrix to optimize conc. in 50ul vs 25ul.',
    'apiLevel': '2.11'
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

# splits aspiration volume into equal parts 
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
    # sds_rack
    pos_control = stds_rack['A1'] #900ul, 1uM ssDNA
    sN_mix = stds_rack['D1'] # empty; receives BPW_mix and water for stds 
    std_1 = stds_rack['A3'] # 990ul Water
    std_2 = stds_rack['A4'] # 900ul water
    std_3 = stds_rack['A5'] # 900ul water
    std_4 = stds_rack['A6'] # 900ul water
    std_5 = stds_rack['B3'] # 900ul water
    std_6 = stds_rack['B4'] # 900ul water 
    std_7 = stds_rack['B5'] # 900ul water
    std_1mix = stds_rack['C3'] # empty
    std_2mix = stds_rack['C4'] # empty
    std_3mix = stds_rack['C5'] # empty
    std_4mix = stds_rack['C6'] # empty
    std_5mix = stds_rack['D3'] # empty
    std_6mix = stds_rack['D4'] # empty
    std_7mix = stds_rack['D5'] # empty
    NTC_mix = stds_rack['D6'] # empty, receives sN_mix and water as NTC
    
    #fuge_rack
    bpwd_mix = fuge_rack['A1'] #empty
    liquid_trash = fuge_rack['B1']
    water = fuge_rack['B2'] # 1000ul water want to separate this from pos stds
    BPW_mix = fuge_rack['D1'] # see sheet, but gen around 1705 ul; use 2mL tube
    fwd_10uM = fuge_rack['C2'] # min 300ul
    rev_10uM = fuge_rack['D2'] # min 300ul
    fwd_1 = fuge_rack['A4'] # e.g. 0.625uM # empty
    fwd_2 = fuge_rack['A5'] # e.g. 1.25uM # empty
    fwd_3 = fuge_rack['A6'] # e.g. 2.5uM # empty
    fwd_4 = fuge_rack['B4'] # e.g. 5.0uM # empty
    fwd_5 = fuge_rack['B5'] # e.g. 7.5uM # empty
    fwd_6 = fuge_rack['B6'] # e.g. 10uM # empty
    R_mix_1 = fuge_rack['C4'] # e.g. 0.625uM # empty
    R_mix_2 = fuge_rack['C5'] # e.g. 1.25uM # empty
    R_mix_3 = fuge_rack['C6'] # e.g. 2.5uM # empty
    R_mix_4 = fuge_rack['D4'] # e.g. 5.0uM # empty
    R_mix_5 = fuge_rack['D5'] # e.g. 7.5uM # empty
    R_mix_6 = fuge_rack['D6'] # e.g. 10uM # empty
    
    # lists
    plate_col = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']
    all_R_mix = [R_mix_1, R_mix_2, R_mix_3, R_mix_4, R_mix_5, R_mix_6]
    plate_rows = ['A', 'B', 'C', 'D', 'E', 'F']
    all_fwd = [fwd_1, fwd_2, fwd_3, fwd_4, fwd_5, fwd_6]
    std_tubes = [std_1, std_2, std_3, std_4, std_5, std_6, std_7, water]
    std_mixes = [std_1mix, std_2mix, std_3mix, std_4mix, std_5mix, std_6mix, std_7mix, NTC_mix]
    std_wells = ['G1', 'G4', 'G7', 'G10', 'H1', 'H4', 'H7', 'H10']
   
    # user inputs
    orig_F_conc = 10 # What is the starting F primer concentration? (in uM)
    orig_R_conc = 10 # What is the starting R primer concentration? (in uM)
    orig_P_conc = 10 # What is probe starting concentration? (in uM)
    std_F_conc = 300 # What is the constant F primer concentration for standards? This should be guess or from literature. (in nM)
    std_R_cond = 300 # What is the constant R primer concentration for standards? This should be guess or from literature. (in nM)
    P_conc = 300 # What is the probe concentration? This should be constant throughout experiment.
    tot_stds = 21 # How many wells of standards will be run? (in # wells)
    tot_NTCs = 3 # How many wells of NTCs will be run? (in # wells)
    tot_samp = 72 # How many samples with varying conditions will be run? (in # wells)
    rxn_base = 11.2 # Everything in PCR buffer (Mg2+, dNTPs, polymerase, enhancers, stabilizers, sugars, etc.). (in uL)
    tot_rxn_vol = 20 # What is total volume of PCR reaction in plate/tube? (in ul)
    # F_concs = [50, 100, 200, 400, 600, 800] # What are the F primer concentrations? (a list in nM)
    # R_concs = [50, 100, 200, 400, 600, 800] # What are the R primer concentrations? (a list in nM)
    F_50 = 50 # F primer at lowest concentration. (in nM)
    F_100 = 100 # F primer at concentration. (in nM)
    F_200 = 200 # F primer at concentration. (in nM)
    F_400 = 400 # F primer at concentration. (in nM)
    F_600 = 600 # F primer at concentration. (in nM)
    F_800 = 800 # F primer at highest concentration. (in nM)
    R_50 = 50 # R primer at lowest concentration. (in nM)
    R_100 = 100 # R primer at concentration. (in nM)
    R_200 = 200 # R primer at concentration. (in nM)
    R_400 = 400 # R primer at concentration. (in nM)
    R_600 = 600 # R primer at concentration. (in nM)
    R_800 = 800 # R primer at highest concentration. (in nM)
    dna_per_rxn = 2 # How much standard, positive control or NTC to add per well. 
    std_NTC_reps = 3 # How many standard and NTC replicates? (int)
    R_reps = 12 # How many wells will use R primer at particular concentration? (int)
    # F_reps = 12 # How many wells will use F primer at particular concentration? (int)
    F_int_vol = 100 # What is the volume of F intermediate primer in new tube? (in ul)
    percent_waste =  0.20 # What percentage waste? (decimal)
    sN_mix_waste_offset = 0.025  # How much percent_waste offset should sN_mix use? This calculated as percent_waste-sN_mix_overage = percent_waste for sN_mix_overage e.g. (20-7=13%) Should not be 0 otherwise offset = percent_waste. (decimal)
    R_mix_waste_offset = 0.11  # How much percent_waste offset should R_mix use? This calculated as percent_waste-R_mix_overage = percent_waste for R_mix_overage e.g. (20-=13%) If 0, then offset = percent_waste. (decimal)
    std_NTC_waste_offset = 0.028 # How much percent_waste offset should std_NTC use? (decimal)
    bpw_waste_offset = 0.032 # How much percent_waste offset should bpw_waste use? (decimal)
    p300_max_vol = 200


    # calcs
    tot_rxns = tot_stds+tot_NTCs+tot_samp # Calc what is total # rxns. (int)
    tot_sds_NTC = tot_stds+tot_NTCs # Calc number of standards and nontemplate controls. (int)
    rxn_vol_no_dna = tot_rxn_vol-dna_per_rxn # Calc what is volume of PCR rxn with no DNA added. (in ul)
    P_per_rxn = P_conc/1000*tot_rxn_vol/orig_P_conc # Calc this constant probe is needed per pcr reaction. (in ul)
    max_vol_F_per_rxn = F_800/1000*tot_rxn_vol/orig_F_conc # Calc greatest vol added from starting F primer conc to rxn to satisfy max test F conc? (in ul)
    max_vol_R_per_rxn = R_800/1000*tot_rxn_vol/orig_R_conc # Calc greatest vol added from starting R primer conc to rxn to satisfy max test R conc? (in ul)
    water_per_rxn =  rxn_vol_no_dna-rxn_base-P_per_rxn-max_vol_F_per_rxn-max_vol_R_per_rxn # Calc this is water added per rxn such that greatest F, R primer conc can be accommodated in total rxn vol. (in ul)
    std_vol_F_per_rxn =  std_F_conc/1000*tot_rxn_vol/orig_F_conc# Calc adding this much F primer to each std rxn
    std_vol_R_per_rxn =  std_R_cond/1000*tot_rxn_vol/orig_R_conc# Calc adding this much F primer to each std rxn
    BPW_rxn =  rxn_base+P_per_rxn+water_per_rxn# Mix base + probe + water (no DNA, F, R primer). (in ul)
    std_woff_per_sN_rxn =  max_vol_F_per_rxn-std_vol_F_per_rxn+max_vol_R_per_rxn-std_vol_R_per_rxn# Calc how much water to add to offset diff in max vol F,R primer per reaction. (Max-Std)*2 (in ul)
    BPW_sN_rxn =  BPW_rxn+std_vol_F_per_rxn+std_vol_R_per_rxn+std_woff_per_sN_rxn# Mix base + probe + water+F,R primer at std conc+water_offset(no DNA). (in ul)
    BWP_mix_xfer_sN_mix = tot_sds_NTC*(1+percent_waste-sN_mix_waste_offset)*BPW_rxn # Calc how much tot_BPW_mix to move to make new tube for stds and NTC. (in ul)
    std_woff_add_to_sN_mix = std_woff_per_sN_rxn*tot_sds_NTC*(1+percent_waste-sN_mix_waste_offset) # Calc how much water to add to sdd_NTC mmix with waste
    F_add_to_sN_mix = tot_sds_NTC*(1+percent_waste-sN_mix_waste_offset)*std_vol_F_per_rxn # Calc how much F primer to add to std_NTC mmix with waste
    R_add_to_sN_mix =  tot_sds_NTC*(1+percent_waste-sN_mix_waste_offset)*std_vol_R_per_rxn# Calc how much R primer to add to std_NTC mmix with waste
    sN_mix_xfer_to_stds_mix = BPW_sN_rxn*std_NTC_reps*(1+percent_waste-std_NTC_waste_offset)  # Calc how much sn_mix to aliquot to tube in preparation for std DNA mixing. (in ul)
    std_DNA_xfer_to_stds_mix =  dna_per_rxn*std_NTC_reps*(1+percent_waste-std_NTC_waste_offset)# Calc how much DNA from each standard adding to stds_mix with waste. (in ul)
    bpw_mix_xfer_bpwd_mix =  tot_samp*BPW_rxn*(1+percent_waste-bpw_waste_offset)# Calc how much bpw_mix needed in new tube for # total samples
    std_DNA_xfer_to_bpwd_mix = dna_per_rxn*tot_samp*(1+percent_waste-bpw_waste_offset) # Calc how much DNA to add to bpw_mix for template in PCR rxns.
    dna_per_rxn_10x = 0.2 # dna_per_rxn_10x =  # 10x concentrated DNA to add to reactions to avoid using too much std sample
    water_per_rxn_bpwd_mix = 2-dna_per_rxn_10x# water_per_rxn_bpwd_mix =  # Water to add to bpwd mix to offset 2ul to 0.2ul DNA addition.
    dna_XFR_bpwd_mix = tot_samp*dna_per_rxn_10x*(1+percent_waste-bpw_waste_offset) # dna_XFR_bpwd_mix =  # The amount of DNA to transfer from a std tube to the bpwd_mix
    water_XFR_bpwd_mix = tot_samp*water_per_rxn_bpwd_mix*(1+percent_waste-bpw_waste_offset) # water_XFR_bpwd_mix =  # The amount of water to transfer to the bpwd_mix to offset lower DNA vol addition
    bpwd_rxn = BPW_rxn+dna_per_rxn  # Calc vol of bpw reaction + DNA vol
    bpwd_mix_xfer_R_mix = bpwd_rxn*R_reps*(1+percent_waste-R_mix_waste_offset) # Calc how muc bpwd_mix to transfer to each tube for specific R conc. Less than 12% to avoid missing vol.
    R_50_rxn = R_50/1000*tot_rxn_vol/orig_R_conc # Calc how much R primer at lowest concentration to add per reaction? (e.g. 50nM) (in ul)
    R_50_mix =  R_50_rxn*R_reps*(1+percent_waste-R_mix_waste_offset)# Calc how much R primer to add to R_50 mix. (in ul)
    R_50_woff_rxn = max_vol_R_per_rxn-R_50_rxn# Calc how much water offset to add to each rxn. (in ul)
    R_50_woff_mix = R_50_woff_rxn*R_reps*(1+percent_waste-R_mix_waste_offset) # Calc how much water offset to add to R_50 mix. (in ul)
    R_100_rxn = R_100/1000*tot_rxn_vol/orig_R_conc # Calc how much R primer at concentration to add. (in ul)
    R_100_mix =  R_100_rxn*R_reps*(1+percent_waste-R_mix_waste_offset)# Calc how much R primer to add to add. (in ul)
    R_100_woff_rxn = max_vol_R_per_rxn-R_100_rxn # Calc how much water offset to add to each rxn. (in ul)
    R_100_woff_mix =  R_100_woff_rxn*R_reps*(1+percent_waste-R_mix_waste_offset)# Calc how much water offset to add to mix. (in ul)
    R_200_rxn = R_200/1000*tot_rxn_vol/orig_R_conc  # Calc how much R primer at concentration to add. (in ul)
    R_200_mix = R_200_rxn*R_reps*(1+percent_waste-R_mix_waste_offset) # Calc how much R primer to add to add. (in ul)
    R_200_woff_rxn = max_vol_R_per_rxn-R_200_rxn # Calc how much water offset to add to each rxn. (in ul)
    R_200_woff_mix =  R_200_woff_rxn*R_reps*(1+percent_waste-R_mix_waste_offset)# Calc how much water offset to add to mix. (in ul)
    R_400_rxn = R_400/1000*tot_rxn_vol/orig_R_conc # Calc how much R primer at concentration to add. (in ul)
    R_400_mix = R_400_rxn*R_reps*(1+percent_waste-R_mix_waste_offset) # Calc how much R primer to add to add. (in ul)
    R_400_woff_rxn = max_vol_R_per_rxn-R_400_rxn # Calc how much water offset to add to each rxn. (in ul)
    R_400_woff_mix = R_400_woff_rxn*R_reps*(1+percent_waste-R_mix_waste_offset) # Calc how much water offset to add to mix. (in ul)
    R_600_rxn =  R_600/1000*tot_rxn_vol/orig_R_conc  # Calc how much R primer at concentration to add. (in ul)
    R_600_mix = R_600_rxn*R_reps*(1+percent_waste-R_mix_waste_offset) # Calc how much R primer to add to add. (in ul)
    R_600_woff_rxn = max_vol_R_per_rxn-R_600_rxn # Calc how much water offset to add to each rxn. (in ul)
    R_600_woff_mix =  R_600_woff_rxn*R_reps*(1+percent_waste-R_mix_waste_offset) # Calc how much water offset to add to mix. (in ul)
    R_800_rxn = R_800/1000*tot_rxn_vol/orig_R_conc  # Calc how much R primer at concentration to add. (in ul)
    R_800_mix = R_800_rxn*R_reps*(1+percent_waste-R_mix_waste_offset) # Calc how much R primer to add to add. (in ul)
    R_800_woff_rxn = max_vol_R_per_rxn-R_800_rxn # Calc how much water offset to add to each rxn. (in ul)
    R_800_woff_mix = R_800_woff_rxn*R_reps*(1+percent_waste-R_mix_waste_offset) # Calc how much water offset to add to mix. (in ul)
    F_50_int_conc = F_50/1000*tot_rxn_vol/max_vol_F_per_rxn # What intermediate (int) concentration of F primer is needed such that by adding 1.6ul I obtain a final F primer concentration of 50, 100, 200…etc in rxn well? (in uM)
    F_100_int_conc = F_100/1000*tot_rxn_vol/max_vol_F_per_rxn # What intermediate (int) concentration of F primer is needed such that by adding 1.6ul I obtain a final F primer concentration of 50, 100, 200…etc in rxn well? (in uM)
    F_200_int_conc =  F_200/1000*tot_rxn_vol/max_vol_F_per_rxn# What intermediate (int) concentration of F primer is needed such that by adding 1.6ul I obtain a final F primer concentration of 50, 100, 200…etc in rxn well? (in uM)
    F_400_int_conc =  F_400/1000*tot_rxn_vol/max_vol_F_per_rxn# What intermediate (int) concentration of F primer is needed such that by adding 1.6ul I obtain a final F primer concentration of 50, 100, 200…etc in rxn well? (in uM)
    F_600_int_conc =  F_600/1000*tot_rxn_vol/max_vol_F_per_rxn# What intermediate (int) concentration of F primer is needed such that by adding 1.6ul I obtain a final F primer concentration of 50, 100, 200…etc in rxn well? (in uM)
    F_800_int_conc =  F_800/1000*tot_rxn_vol/max_vol_F_per_rxn# What intermediate (int) concentration of F primer is needed such that by adding 1.6ul I obtain a final F primer concentration of 50, 100, 200…etc in rxn well? (in uM)
    F_50_int_primer = F_50_int_conc*F_int_vol/orig_F_conc # What amount of primer should be added to generate int F primer conc? (in ul)
    F_50_int_water =  F_int_vol-F_50_int_primer# What amount of water should be added to generate int F primer conc? (in ul)
    F_100_int_primer = F_100_int_conc*F_int_vol/orig_F_conc # What amount of primer should be added to generate int F primer conc? (in ul)
    F_100_int_water = F_int_vol-F_100_int_primer # What amount of water should be added to generate int F primer conc? (in ul)
    F_200_int_primer = F_200_int_conc*F_int_vol/orig_F_conc # What amount of primer should be added to generate int F primer conc? (in ul)
    F_200_int_water = F_int_vol-F_200_int_primer # What amount of water should be added to generate int F primer conc? (in ul)
    F_400_int_primer = F_400_int_conc*F_int_vol/orig_F_conc # What amount of primer should be added to generate int F primer conc? (in ul)
    F_400_int_water = F_int_vol-F_400_int_primer # What amount of water should be added to generate int F primer conc? (in ul)
    F_600_int_primer = F_600_int_conc*F_int_vol/orig_F_conc # What amount of primer should be added to generate int F primer conc? (in ul)
    F_600_int_water = F_int_vol-F_600_int_primer # What amount of water should be added to generate int F primer conc? (in ul)
    F_800_int_primer =  F_800_int_conc*F_int_vol/orig_F_conc # What amount of primer should be added to generate int F primer conc? (in ul)
    F_800_int_water = F_int_vol-F_800_int_primer # What amount of water should be added to generate int F primer conc? (in ul)
    R_mix_rxn = bpwd_rxn+R_50_rxn+R_50_woff_rxn # What is the rxn vol that should be aliquoted to plate wells after R primer addition? (in ul e.g.18.4)

    # more lists
    R_mix_primer=[R_50_mix, R_100_mix, R_200_mix, R_400_mix, R_600_mix, R_800_mix]
    R_mix_water=[R_50_woff_mix, R_100_woff_mix, R_200_woff_mix, R_400_woff_mix, R_600_woff_mix, R_800_woff_mix]
    F_mix_primer=[F_50_int_primer, F_100_int_primer, F_200_int_primer, F_400_int_primer, F_600_int_primer, F_800_int_primer]
    F_mix_water=[F_50_int_water, F_100_int_water, F_200_int_water, F_400_int_water, F_600_int_water, F_800_int_water]

    # Mixes
    BPW_mix_tot = BPW_rxn*(1+percent_waste)*tot_rxns  # Mix = base + probe + water (no DNA, F, R primer)*96*waste. (in ul)
    sN_mix_tot = BWP_mix_xfer_sN_mix+std_woff_add_to_sN_mix+F_add_to_sN_mix+R_add_to_sN_mix # Mix = base + probe + water + F,R primers at std conc + water offset (no DNA) * number stds_NTC * waste
    bpwd_mix_tot = bpw_mix_xfer_bpwd_mix+std_DNA_xfer_to_bpwd_mix # Mix = base + probe + DNA (no F, R primer) 
    R_50_mix = bpwd_mix_xfer_R_mix+R_50_mix+R_50_woff_mix # Mix = base + probe + DNA+ R primer (No F primer)
    R_100_mix = bpwd_mix_xfer_R_mix+R_100_mix+R_100_woff_mix # Mix = base + probe + DNA+ R primer (No F primer)
    R_200_mix = bpwd_mix_xfer_R_mix+R_200_mix+R_200_woff_mix # Mix = base + probe + DNA+ R primer (No F primer)
    R_400_mix = bpwd_mix_xfer_R_mix+R_400_mix+R_400_woff_mix # Mix = base + probe + DNA+ R primer (No F primer)
    R_600_mix = bpwd_mix_xfer_R_mix+R_600_mix+R_600_woff_mix # Mix = base + probe + DNA+ R primer (No F primer)
    R_800_mix = bpwd_mix_xfer_R_mix+R_800_mix+R_800_woff_mix # Mix = base + probe + DNA+ R primer (No F primer)
    
    print ("BWP_mix_xfer_sN_mix", BWP_mix_xfer_sN_mix)
    print ("bpw_mix_xfer_bpwd_mix", bpw_mix_xfer_bpwd_mix)
   
   
    # ##### COMMANDS ######
    # prepare sN_mix
    # add BPW_mix to sN_mix tube
    p300.pick_up_tip()
    bpw_heights = tip_heights(BPW_mix_tot, len(split_asp(BWP_mix_xfer_sN_mix, p300_max_vol)), split_asp(BWP_mix_xfer_sN_mix, p300_max_vol)[0])
    p300.mix(3, 200, BPW_mix.bottom(bpw_heights[0]))
    # p300.flow_rate.aspirate = 40 #default
    # p300.flow_rate.dispense = 40 #default
    for j in range(len(split_asp(BWP_mix_xfer_sN_mix, p300_max_vol))):
        amt = split_asp(BWP_mix_xfer_sN_mix, p300_max_vol)[j]
        p300.aspirate(amt, BPW_mix.bottom(bpw_heights[j]), rate=0.4)
        protocol.delay(seconds=1) #equilibrate
        h = tip_heights(amt+amt*j, 1, 0)[0]
        p300.dispense(amt, sN_mix.bottom(h+5), rate=0.5)
        p300.blow_out(sN_mix.bottom(h+10)) # want to be above liquid level
        p300.touch_tip()
    p300.drop_tip()
    # transfer water to sN__mix
    p300.transfer(
        std_woff_add_to_sN_mix, # ~55ul
        water.bottom(5),
        sN_mix.bottom(15), #don't want tip going too far to avoid mmix buildup
        touch_tip=True,
        blowout_location='destination well')
    # transfer F primer @ std conditions to sN__mix
    p20.transfer(
        F_add_to_sN_mix,
        fwd_10uM.bottom(3),
        sN_mix.bottom(15),
        blow_out=True,
        mix_after=(2, 20),
        blowout_location='destination well')
    # transfer R primer @ std conditions to sN__mix
    p20.transfer( #some resid fluid on outside
        R_add_to_sN_mix,
        rev_10uM.bottom(3),
        sN_mix.bottom(15),
        blow_out=True,
        mix_after=(2, 20),
        blowout_location='destination well')
    
    # # transfer sN_mix to intermediate tubes (std_mixes)
    # std_mix_heights = tip_heights(sN_mix_tot, len(std_mixes), sN_mix_xfer_to_stds_mix)#[13,11,8,6,4,2,0]
    # p300.pick_up_tip()
    # # need to mix F, R and water
    # p300.mix(2, 200, sN_mix.bottom(4)) #4mm from bottom; this algo better for mixing
    # p300.mix(2, 200, sN_mix.bottom(8)) #8mm from bottom
    # p300.mix(5, 200, sN_mix.bottom(std_mix_heights[0])) #10mm from bottom
    # p300.well_bottom_clearance.aspirate = std_mix_heights[0] #mm 
    # for tube, h in zip(std_mixes, std_mix_heights):
    #     # p300.well_bottom_clearance.aspirate = h #mm
    #     p300.aspirate(sN_mix_xfer_to_stds_mix, sN_mix.bottom(h), rate=0.4) # 18 * 3 * 1.12-0.05= 54 + 6 =60ul
    #     protocol.delay(seconds=2) #tip equilibrate
    #     p300.move_to(sN_mix.bottom(35)) # excess tip fluid condense 
    #     protocol.delay(seconds=3) #tip droplets slide
    #     p300.touch_tip()
    #     p300.dispense(sN_mix_xfer_to_stds_mix, tube, rate=0.5)
    # p300.drop_tip()
    # # p300.flow_rate.aspirate = 92.86 #reset to default
    # # p300.flow_rate.dispense = 92.86 #reset to default
    # # p300.well_bottom_clearance.aspirate = 1 #mm default
   
    # # transfer std DNA into intermediate std_mixes tubes and then to plate
    # for std, intTube, well in zip(std_tubes, std_mixes, std_wells):
    #     p20.pick_up_tip()
    #     p300.pick_up_tip()
    #     # p20.flow_rate.aspirate = 4
    #     # p20.flow_rate.dispense = 4
    #     p20.aspirate(std_DNA_xfer_to_stds_mix, std.bottom(3), rate=0.4) #aspirate from std_1 into std_mix (intermediate tube) e.g. 6.42 ul
    #     protocol.delay(seconds=3) #equilibrate
    #     p20.touch_tip()
    #     p20.dispense(std_DNA_xfer_to_stds_mix, intTube.bottom(2), rate=0.5)
    #     # p20.move_to(intTube.bottom(3))
    #     # p20.flow_rate.aspirate = 7.56
    #     # p20.flow_rate.dispense = 7.56
    #     p20.mix(2, 20, intTube.bottom(5)) #ensure vol in tip in intTube and washed
    #     p20.blow_out()
    #     p300.move_to(intTube.bottom(40)) #prevent tip from crashing into tube cap
    #     p300.mix(7, 50, intTube.bottom(1))
    #     protocol.delay(seconds=2)
    #     # p300.move_to(intTube.bottom(10)) #prevent air bubbles in mmix during blow out
    #     p300.blow_out(intTube.bottom(10))
    #     p20.move_to(intTube.bottom(40))
    #     for x in range(0,3): # need int 1, 2, and 3
    #         p20.aspirate(20, intTube.bottom(1), rate=0.5) 
    #         protocol.delay(seconds=2) #equilibrate
    #         # find digits in well, G1 and G10 and puts into list
    #         findNums = [int(i) for i in well.split()[0] if i.isdigit()]
    #         # joins nums from list [1, 0] -> 10 type = string
    #         colNum = ''.join(map(str, findNums))
    #         # this finds row
    #         row = well.split()[0][0]
    #         dest = row+str(int(colNum)+x) # row + neighbor well i.e. 1, 2
    #         p20.dispense(20, plate[dest].bottom(2), rate=0.85)
    #         p20.move_to(plate[dest].bottom(5))
    #         p20.blow_out()
    #         # p20.touch_tip()
    #     p300.drop_tip()
    #     p20.drop_tip()

    # create bpwd_mix 
    # First, add bpw_mix to a new tube
    p300.pick_up_tip()
    # tip_heights is a function using total_vol, # steps, and aliquot (vol decrement) amt as parameters.
    bpwd_xfer_h = tip_heights(BPW_mix_tot-BWP_mix_xfer_sN_mix, len(split_asp(bpw_mix_xfer_bpwd_mix, p300_max_vol)), split_asp(bpw_mix_xfer_bpwd_mix, p300_max_vol)[0])
    p300.mix(3, 200, BPW_mix.bottom(bpwd_xfer_h[0]))
    for j in range(len(split_asp(bpw_mix_xfer_bpwd_mix, p300_max_vol))): # split_asp is a function that returns equally divided aspirations
        amt = split_asp(bpw_mix_xfer_bpwd_mix, p300_max_vol)[j]
        p300.aspirate(amt, BPW_mix.bottom(bpwd_xfer_h[j]), rate=0.8)
        protocol.delay(seconds=2)
        h = tip_heights(amt+amt*j, 1, 0)[0] # adjust tip height depending on dispenses
        p300.dispense(amt, bpwd_mix.bottom(h+5)) # want tip to be just a little above dispense
        p300.blow_out(bpwd_mix.bottom(h+8)) # want to be above liquid level
        p300.touch_tip()
    p300.drop_tip()
    # Second, add std_5 DNA or other std. 0.2ul added instead of 2ul to avoid using large volumes of std
    p20.transfer(
        dna_XFR_bpwd_mix, #16.8ul
        std_6.bottom(3),
        bpwd_mix.bottom(24),
        mix_after=(2, dna_XFR_bpwd_mix),
        blow_out=True,
        blowout_location='destination well')
    # Third, add water to offset the reduction in DNA vol, from 2ul to 0.2 = 1.8ul*72*(1+waste-offset)
    p300.transfer(
        water_XFR_bpwd_mix, # ~151.4ul
        water.bottom(20), # vol = 900 - std_DNA_xfer_to_stds_mix (~7ul) = 893ul. 
        bpwd_mix.bottom(24))
    # Last, transfer bpwd_mix to intermediate R tubes (R_mix_1)
    bpwd_heights = tip_heights(bpwd_mix_tot, len(all_R_mix), bpwd_mix_xfer_R_mix)
    bpwd_heights = tip_heights(BPW_mix_tot-sN_mix_tot, len(all_R_mix), bpwd_mix_xfer_R_mix)    #[25.9, 22.9, 19.5, 15.9, 12.3, 0.5]
    p300.pick_up_tip()
    p300.mix(2, 200, bpwd_mix.bottom(4)) #second to last height; for mixing at bottom
    p300.mix(2, 200, bpwd_mix.bottom(8)) #mid tip height
    p300.mix(5, 200, bpwd_mix.bottom(bpwd_heights[0])) #first tip height; need thorough mix
    p300.blow_out(bpwd_mix.bottom(bpwd_heights[0]+2)) # bring tip up from solution
    # p300.flow_rate.aspirate = 30
    # p300.flow_rate.dispense = 40
    for Rtube, h in zip(all_R_mix, bpwd_heights):
        for r in range(2):
            p300.aspirate(bpwd_mix_xfer_R_mix/2, bpwd_mix.bottom(h), rate=0.8) # bpwd_rxn*row reps (12) * waste = 16.8*12*(1+.12-0.05)=
            protocol.delay(seconds=2) #tip equilibrate
            p300.dispense(bpwd_mix_xfer_R_mix/2, Rtube.bottom(4+4*r)) # good pos for dispense
            p300.blow_out(Rtube.bottom(10+6*r)) # good pos for blow out
    p300.drop_tip()
    
    # add R_primer, water to all_R_mix tubes
    # add primer 
    p20.transfer(
        R_mix_primer, # list, can't do .bottom()
        rev_10uM,
        all_R_mix, # list
        new_tip='always',
        touch_tip=True,
    )
    # add water
    p20.transfer(
        R_mix_water, # list
        water.bottom(15),
        all_R_mix, # list
        new_tip='always',
    )
    
    # mix and aliquot tubes in all_R_mix and aliquot to plate row
    for tube, row in zip(all_R_mix, plate_rows):
        p300.flow_rate.aspirate = 92.86 #reset to default
        p300.flow_rate.dispense = 92.86 #reset to default
        p300.pick_up_tip()
        # p300.move_to(tube.bottom(6))
        p300.mix(6, 200, tube.bottom(3)) # about 230ul in tube
        # p300.blow_out(tube.bottom(6))
        # p300.flow_rate.aspirate = 30 
        # p300.flow_rate.dispense = 40 
        for i in range(0,2): # split 1..12 dispensing in half
            p300.aspirate(R_mix_rxn*2*3, tube.bottom(1), rate=0.4) # 18.4 *2 wells * 3 times on row
            protocol.delay(seconds=3)
            for j in range(1+6*i,6+6*i,2): #1,3,5->7,9,11; distribute to every other col
                dest = row+str(j)
                p300.dispense(R_mix_rxn*2, plate[dest], rate=0.5) # bolus for two wells
                if j==5 or j==11:
                    # p300.move_to(plate[dest].bottom(7)) #confirm both these work. prefer blow_out()
                    p300.blow_out(plate[dest].bottom(10))
                p300.touch_tip()
        p300.drop_tip()

    # now that PCR reactions are chillin' at 4C, make F_primer int tubes
    # Mix 100ul 'Fwd' dilutions in tube by adding water and "fwd 10uM" tube as shown in schedule
    # p20.well_bottom_clearance.aspirate=2
    # p20.well_bottom_clearance.dispense=8
    p300.transfer(
        F_mix_water, 
        water.bottom(12),
        all_fwd,
        touch_tip=True,
        new_tip='once')

    # first two with vol < 20ul
    for first_two in range(len(F_mix_primer[0:2])): 
        p20.transfer(
            F_mix_primer[first_two],
            fwd_10uM.bottom(2),
            all_fwd[first_two],
            new_tip='once')
    # last four with vol>20
    for last_four in range(len(F_mix_primer[2:6])):
        offset = 2
        p300.transfer(
            F_mix_primer[last_four+offset],
            fwd_10uM.bottom(2),
            all_fwd[last_four+offset],
            new_tip='once') #! last well, misses aspiration, about 20ul remaining, about 50ul short. More in source tube.
    # p20.well_bottom_clearance.aspirate=1
    # p20.well_bottom_clearance.dispense=1

    # Add F_primer to wells. mix, aliquot to adjacent wells
    F_tube_heights = tip_heights(100,1,0)
    for i, tube in enumerate (all_fwd):
        p300.pick_up_tip()
        p20.pick_up_tip()
        # p300.flow_rate.aspirate = 92.86 #reset to default
        # p300.flow_rate.dispense = 92.86 #reset to default
        p300.mix(4,78, tube.bottom(F_tube_heights[0])) # mix F primer tube, 100ul in tube
        p300.blow_out(tube.bottom(10))
        p300.touch_tip()
        # p20.flow_rate.aspirate=4
        # p20.flow_rate.dispense=4
        p20.move_to(tube.bottom(40))
        p20.aspirate(20, tube.bottom(1), rate=0.4) # aspirate from F primer tube to wells
        p20.move_to(tube.bottom(2)) # relieve pressure if tip against tube 
        protocol.delay(seconds=1)
        p20.touch_tip()
        # need 3.2ul in A1, B1, C1, D1..F1
        for x in range(0, len(plate_rows)):  # distribute to every other col
            well_pos = plate_rows[x]+plate_col[2*i] # var i can be used to loop through rows since each mmix is on its own row
            p20.dispense(3.2, plate[well_pos], rate=0.5)
            # protocol.delay(seconds=1)
            p20.touch_tip()
            # p20.move_to(robot.deck(['12'])) # move to trash for blow out
        p20.blow_out(liquid_trash.bottom(10))
        p20.touch_tip() #has 20-3.2*6ul remaining; need to go in trash
        for y in range(0, len(plate_rows)):  # distribute to every other col
            well_pos = plate_rows[y]+plate_col[2*i] # var i can be used to loop through rows since each mmix is on its own row
            well_dest = plate_rows[y]+plate_col[2*i+1]
            p300.move_to(plate[well_pos].bottom(40)) # prevent running tip into plate
            # p300.move_to(plate[well_pos].bottom(3))
            # p300.flow_rate.aspirate = 92.86
            # p300.flow_rate.dispense = 92.86
            p300.mix(5,20, plate[well_pos].bottom(3), rate=0.7) 
            # p300.flow_rate.aspirate = 30
            # p300.flow_rate.dispense = 30
            p300.aspirate(30, plate[well_pos].bottom(3), rate=0.4)
            protocol.delay(seconds=1)
            p300.dispense(30, plate[well_pos].bottom(1), rate=0.4) #deposit slowly at bottom so no bubbles
            protocol.delay(seconds=1)
            p300.move_to(plate[well_pos].bottom(10))
            protocol.delay(seconds=2)
            # p300.flow_rate.aspirate = 92.86 # default
            # p300.flow_rate.aspirate = 92.86 # default
            p300.blow_out(plate[well_pos].bottom(15))
            p20.move_to(plate[well_pos].bottom(40)) # prevent plate collision
            p20.aspirate(20, plate[well_pos].bottom(1))
            protocol.delay(seconds=2)
            p20.dispense(20, plate[well_dest])
            p20.move_to(plate[well_dest].bottom(5))
            p20.blow_out()
            p20.touch_tip()
        p300.drop_tip()
        p20.drop_tip()

  