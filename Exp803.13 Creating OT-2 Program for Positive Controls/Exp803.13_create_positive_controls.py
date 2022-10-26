# imports
from opentrons import protocol_api

# metadata
metadata = {
    'protocolName': 'Dispense Positive Controls',
    'author': 'Harley King <harley.king@luminultra.com>',
    'description': 'Create a 15, 50mL positive control mix and distribute to 9 racks x 24 tubes.',
    'apiLevel': '2.12'
}
##########################
# functions
# Calc heights for 50mL conical tubes
def fifty_ml_heights(init_vol, steps, vol_dec):
    vols = []
    heights = []
    # these values originate from Excel spreadsheet "Exp803..."
    b = 0
    m = 0.0024
    if init_vol > 51000:
        offset = 14  # model out of range; see sheet
    else:
        offset = 15  # mm Need to add offset to ensure tip reaches below liquid level
    for i in range(steps):
        x = init_vol-vol_dec*i
        vols.append(x)
        h = m*x+b
        h = h-offset
        if h < 17.5:  # If less than 5mL remain in 50mL tube, go to bottom for asp
            h = 2
            heights.append(h)
        else:
            heights.append(round(h, 1))
    return heights

   # calculates ideal tip height for entering liquid in 15mL tube
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
    rack_1 = protocol.load_labware('opentrons_24_tuberack_nest_1.5ml_screwcap', '10')
    rack_2 = protocol.load_labware('opentrons_24_tuberack_nest_1.5ml_screwcap', '11')
    rack_3 = protocol.load_labware('opentrons_24_tuberack_nest_1.5ml_screwcap', '3')
    rack_4 = protocol.load_labware('opentrons_24_tuberack_nest_1.5ml_screwcap', '4')
    rack_5 = protocol.load_labware('opentrons_24_tuberack_nest_1.5ml_screwcap', '5')
    rack_6 = protocol.load_labware('opentrons_24_tuberack_nest_1.5ml_screwcap', '6')
    rack_7 = protocol.load_labware('opentrons_24_tuberack_nest_1.5ml_screwcap', '7')
    rack_8 = protocol.load_labware('opentrons_24_tuberack_nest_1.5ml_screwcap', '8')
    rack_9 = protocol.load_labware('opentrons_24_tuberack_nest_1.5ml_screwcap', '9')
    pos_control_rack = protocol.load_labware('opentrons_10_tuberack_nest_4x50ml_6x15ml_conical', '1',)
    tiprack300 = protocol.load_labware('opentrons_96_filtertiprack_200ul', '2')

    # PIPETTES
    p300 = protocol.load_instrument(
        'p300_single_gen2', 'left', tip_racks=[tiprack300]
    )
     
    # REAGENTS
    # pos_control = pos_control_rack['A1'] #15mL tube
    pos_control = pos_control_rack['B4'] #50mL tube

    # user inputs
    pos_control_vol = 20 #ul
    pos_control_begin_vol = 4000 # what is the beginning vol of the pos control?
    num_of_rounds = 1 # how many times should a full deck be processed? 9*24 = 216 tubes/round?
    # all_racks = [rack_1, rack_2, rack_3, rack_4]
    all_racks = [rack_1, rack_2, rack_3, rack_4, rack_5, rack_6, rack_7]
    # all_racks = [rack_1, rack_2]
    rack_rows = ['A', 'B', 'C', 'D']
    rack_cols = ['1', '2', '3', '4', '5', '6']

    # ##### COMMANDS ######
    # distribute positive controls to tubes on racks
    h=0
    # height = fifty_ml_heights(pos_control_begin_vol, 3*len(all_racks)*num_of_rounds, 160) #3 aspirants per rack; 9 racks; # rounds
    height = fifteen_ml_heights(pos_control_begin_vol, 3*len(all_racks)*num_of_rounds, 160) #3 aspirants per rack; 9 racks; # rounds
    print (height)
    for r in range(1, num_of_rounds+1):
        p300.pick_up_tip()
        for rack in all_racks:
        #p300 pipette will unorthodoxly move top to bottom instead of l to r
        #more efficient for pipetting, refill every 8 vs 12
            for i in range(0,6): # columns
                if i == 0 or i==2 or i==4: # refill every 8
                    print ("height is: ", h)
                    p300.aspirate(pos_control_vol*8, pos_control.bottom(height[h]))
                    p300.move_to(pos_control.bottom(height[h]+20))
                    protocol.delay(seconds=2)
                    p300.move_to(pos_control.bottom(height[h])) # touch tip in solution
                    h+=1
                for j in range(0,4): # rows
                    dest = rack[rack_rows[j] + rack_cols[i]]
                    p300.dispense(pos_control_vol, dest.bottom(2))  # dispense to each well
        p300.drop_tip()
        if r == num_of_rounds:
            protocol.pause(msg='Round {0} is complete. That was the last round!'.format(r))
            # print ("Round {0} is complete. That was the last round!".format(r))
        else:
            protocol.pause(msg='Round {0} is complete. Clear and resume to begin round {1}.'.format(r, r+1))
            # print ("Round {0} is complete. Clear and resume to begin round {1}!".format(r, r+1))


