# imports
from opentrons import protocol_api

# metadata
metadata = {
    'protocolName': 'Transfer Dilution Series from Rack into 96w BioER Plate. Set well number, e.g. N= 32',
    'author': 'Harley King <harley.king@luminultra.com>',
    'description': 'Aliquots dilution series into 96w BioER plate with lyophilized mastermix.',
    'apiLevel': '2.12'
}
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
# Calc heights for 50mL conical tubes
def fifty_ml_heights(init_vol, steps, vol_dec):
    vols = []
    heights = []
    # these values originate from Excel spreadsheet "Exp803..."
    b = 0
    m = 0.0024
    if init_vol > 51000:
        offset = 12  # model out of range; see sheet
    else:
        offset = 5  # mm Need to add offset to ensure tip reaches below liquid level
    for i in range(steps):
        x = init_vol-vol_dec*i
        vols.append(x)
        h = m*x+b
        h = h-offset
        if h < 12:  # If less than 5mL remain in 50mL tube, go to bottom for asp
            h = 3
            heights.append(h)
        else:
            heights.append(round(h, 1))
    return heights
def closest_value(input_list: list, value: float):
    return min(input_list, key=lambda x: abs(x-value))
def run(protocol: protocol_api.ProtocolContext):

    # LABWARE
    tiprack300 = protocol.load_labware('opentrons_96_filtertiprack_200ul', '8')
        
    tempdeck = protocol.load_module('temperature module gen2', '4')
    plate = tempdeck.load_labware('bioer_96_aluminumblock_200ul')

    fuge_rack = protocol.load_labware('vwr_24_tuberack_1500ul', '2')    
    # PIPETTES
    p300 = protocol.load_instrument(
        'p300_single_gen2', 'left', tip_racks=[tiprack300]
    )
     
    # REAGENTS 
    std_1 = fuge_rack['A1'] # no water
    std_2 = fuge_rack['A2'] # no water
    std_3 = fuge_rack['A3'] # no water
    std_4 = fuge_rack['A4'] # no water
    std_5 = fuge_rack['A5'] # no water
    std_6 = fuge_rack['A6'] #  no water
    std_7 = fuge_rack['B1'] # no water
    std_8 = fuge_rack['B2'] # no water
    std_9 = fuge_rack['B3'] # no water
    std_10 = fuge_rack['B4'] # no water
    std_11 = fuge_rack['B5'] # no water
    std_12 = fuge_rack['B6'] # no water
    std_13 = fuge_rack['C1'] # no water
    std_14 = fuge_rack['C2'] # no water
    std_15 = fuge_rack['C3'] # no water

    # USER INPUTS
    dispVol = 20 # this is the volume dispensed into each well min = 14.5, max = 20
    rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
    dispNumberWells = 32 # number of wells to dispense into
    dispNumberColumns =dispNumberWells//8 # number of columns to dispense into
    stds = [std_4, std_5, std_6, std_7, std_8, std_9, std_10, std_11]
    
    #### COMMANDS ######
    # turn on robot rail lights
    protocol.set_rail_lights(True) # turn on lights if not on

    # tip should move in left to right, top to bottom order
    for i in range(8): # 8 rows
        p300.pick_up_tip() # new tip for each row
        p300.mix(2, 200, stds[i].bottom(10)) # mix 2x
        p300.aspirate(dispVol*(dispNumberColumns+2), stds[i].bottom(2)) # aspirate disp Vol * (number of columns+2) Want to dispense 1x back into source tube for more accurate dispenses
        for j in range(dispNumberColumns): # dispense into each column
            p300.dispense(dispVol, plate[rows[i]+str(j+1)].bottom(2), rate=0.75) # dispense dispVol into each well
            p300.touch_tip(plate[rows[i]+str(j+1)], v_offset=-1, speed=20) # touch tip
        p300.drop_tip()  
    protocol.comment('Finished!') # end of protocol
   

 