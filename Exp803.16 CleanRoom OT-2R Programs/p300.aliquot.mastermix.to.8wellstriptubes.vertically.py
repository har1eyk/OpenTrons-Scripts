# imports
from opentrons import protocol_api

# metadata
metadata = {
    'protocolName': 'Dispense mastermix in 8-well strips.',
    'author': 'Ally',
    'description': 'Add mastermix samples to 8-well strip tubes. Tubes are held by temp module.',
    'apiLevel': '2.12'
}

# def which_holder (plate, samp, dest):

##########################
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

def run(protocol: protocol_api.ProtocolContext):

    # LABWARE
    mmx_rack = protocol.load_labware('opentrons_24_tuberack_nest_2ml_snapcap', '2')
    tiprack300 = protocol.load_labware('opentrons_96_filtertiprack_200ul', '8')
    tempdeck = protocol.load_module('tempdeck', '1') # have this so I don't have to move it off
    holder_1 = protocol.load_labware('8wstriptubesonfilterracks_96_aluminumblock_250ul', '3')
    holder_2 = protocol.load_labware('8wstriptubesonfilterracks_96_aluminumblock_250ul', '6')
    # PIPETTES
    p300 = protocol.load_instrument(
        'p300_single_gen2', 'left', tip_racks=[tiprack300]
    )
    
    # REAGENTS   
    # mmx_rack  @ position 2
    mastermix = mmx_rack['A4']

  
    # USER INPUTS
    dispVol = 20 # this is the volume dispensed into each well min = 14.5, max = 20
    mmixVol = 4000 # this is the total volume in 2mL tube.
    # num_of_sample_reps is another way of stating number of strips
    num_of_sample_reps_per_holder = 6 # can't exceed 6
    # holderList = [holder_1, holder_2, holder_3, holder_4]
    holderList = [holder_1, holder_2]
    # holderList = [holder_1]
    
    # lists
    mixes = [mastermix]
    columns = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']
    rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']

    rep_rows=rows[:num_of_sample_reps_per_holder+1]

     #### COMMANDS ######
    # turn on robot rail lights
    protocol.set_rail_lights(True) # turn on lights if not on 
    # Add mastermix, distribute to strip tubes
    for i, mixtube in enumerate(mixes):
        for y in range(0, len(holderList)): 
            p300.pick_up_tip()
            p300.move_to(mixtube.bottom(40))
            p300.aspirate(num_of_sample_reps_per_holder*20*1.10, mixtube.bottom(2)) # 6*20*1.08 = 130
            protocol.delay(seconds=1) #equilibrate
            p300.touch_tip(v_offset=-3)
            holderPos = y
            holder = holderList[holderPos]
            for x in range(num_of_sample_reps_per_holder): # samples in holder
                column = columns[i]
                dest = str(2*x+1) # need +1 offset for col 
                p300.move_to(holder[zip(rep_rows,dest)].bottom(40)) #move across holder in +4cm pos
                p300.dispense(20, holder[zip(rep_rows,dest)].bottom(6), rate=0.75) # more height so tip doesn't touch pellet
                p300.touch_tip()
                p300.move_to(holder[zip(rep_rows,dest)].top()) # centers tip so tip doesn't lift tubes after touch
                p300.move_to(holder[zip(rep_rows,dest)].bottom(40)) #move across holder in +4cm pos
            p300.drop_tip()