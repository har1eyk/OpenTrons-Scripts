# imports
from opentrons import protocol_api

# metadata
metadata = {
    'protocolName': 'Add 20ul DNA from 15mL Tube to Lyophilized Rxns in 8-well Strips in Holders.',
    'author': 'Harley King <harley.king@luminultra.com>',
    'description': 'DNA at a single concentration from a 15mL tube is added to 8-well strip tubes on holders.',
    'apiLevel': '2.12'
}

# def which_holder (plate, samp, dest):

##########################
# calculate water level heights in 15mL tube
def fifteen_ml_heights(init_vol, steps, vol_dec):
    vols = []
    heights = []
    # these values originate from Excel spreadsheet "Volume.heights.in.15.0mL.conical.tube"
    p0 = 6.52
    p1 = 0.013
    p2 = -2.11E-6
    p3 = 3.02E-10
    p4 = -1.95E-14
    p5 = 4.65E-19
    if init_vol > 1500:  # where tube begins to cone
        offset = 5  # ensure tip contacts fluid
    else:  # if in cone portion
        offset = 5  # mm Need to add offset to ensure tip reaches below liquid level
    for i in range(steps):
        x = init_vol-vol_dec*i
        vols.append(x)
        h = p5*x**5+p4*x**4+p3*x**3+p2*x**2+p1*x**1 + p0
        h = h-offset
        if h < 8:  # prevent negative heights; go to bottom to avoid air aspirant above certain height
            h = 1
            heights.append(h)
        else:
            heights.append(round(h, 1))
    return heights

def run(protocol: protocol_api.ProtocolContext):

    # LABWARE
    # stds_rack = protocol.load_labware('vwr_24_tuberack_1500ul', '2')
    dna_rack = protocol.load_labware('opentrons_10_tuberack_nest_4x50ml_6x15ml_conical', '2') # keep this out of way of styrofoam container
    tiprack300 = protocol.load_labware('opentrons_96_filtertiprack_200ul', '8')
    # tempdeck = protocol.load_module('tempdeck', '10')
    # plate = tempdeck.load_labware('opentrons_96_aluminumblock_generic_pcr_strip_200ul')
    holder_1 = protocol.load_labware('8wstriptubesonfilterracks_96_aluminumblock_250ul', '3')
    holder_2 = protocol.load_labware('8wstriptubesonfilterracks_96_aluminumblock_250ul', '6')
    # holder_3 = protocol.load_labware('8wstriptubesonfilterracks_96_aluminumblock_250ul', '1')
    # holder_4 = protocol.load_labware('8wstriptubesonfilterracks_96_aluminumblock_250ul', '4')
    # holder_3 = protocol.load_labware('8wstriptubesonfilterracks_96_aluminumblock_250ul', '7')
    # PIPETTES
    p300 = protocol.load_instrument(
        'p300_single_gen2', 'right', tip_racks=[tiprack300]
    )
    
    # REAGENTS   
    # sds_rack  @ position 2
    dna_mix = dna_rack['A1'] # empty
    
    
    # user inputs
    # num_of_sample_reps is another way of stating number of strips
    num_of_sample_reps_per_holder = 6 # can't exceed 6
    # holderList = [holder_1, holder_2, holder_3, holder_4]
    holderList = [holder_1, holder_2]
    # holderList = [holder_1]
    
    # lists
    SAMP_wells = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
    
    # #### COMMANDS ######    
    # Add sample DNA, mix, distribute to strip tubes
    dnaH = fifteen_ml_heights(3000, len(holderList)*8, (num_of_sample_reps_per_holder+1)*20*1.10) # 6*2*8*20 = 1920, 
    print (dnaH)
    print (len(holderList)*8, (num_of_sample_reps_per_holder+1)*20*1.10)
    height_counter = 0
    for i in range(8): # repeat for each row
        for y in range(0, len(holderList)): #usually length 1 or 2
            dna_mix_h = dnaH[height_counter]
            p300.pick_up_tip()
            # p300.move_to(dna_mix.bottom(dna_mix_h))
            p300.mix(2, 200, dna_mix.bottom(dna_mix_h)) # pre-wet tip for better accuracy
            p300.aspirate((num_of_sample_reps_per_holder+1)*20*1.10, dna_mix.bottom(dna_mix_h)) # 6*20*1.08 = 130, burn 1st dispense
            height_counter+=1
            p300.move_to(dna_mix.bottom(dna_mix_h+10))
            p300.dispense(20, dna_mix.bottom(dna_mix_h)) # dispense 20ul into tube to increase accuracy. 
            protocol.delay(seconds=1) #equilibrate
            p300.move_to(dna_mix.bottom(dna_mix_h)) # remove droplets
            holderPos = y
            holder = holderList[holderPos]
            for x in range(num_of_sample_reps_per_holder): # samples in holder
                row = SAMP_wells[i]
                dest = row+str(2*x+1) # need +1 offset for col 
                p300.move_to(holder[dest].bottom(40)) #move across holder in +4cm pos
                p300.dispense(20, holder[dest].bottom(6), rate=0.75) # more height so tip doesn't touch pellet
                p300.touch_tip(speed=50)
                p300.move_to(holder[dest].top()) # centers tip so tip doesn't lift tubes after touch
                p300.move_to(holder[dest].bottom(40)) #move across holder in +4cm pos
            print ("Height counter:", height_counter)
            p300.drop_tip()