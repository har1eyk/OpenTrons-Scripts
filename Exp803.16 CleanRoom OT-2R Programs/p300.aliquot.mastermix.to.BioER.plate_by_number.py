# imports
from opentrons import protocol_api

# metadata
metadata = {
    'protocolName': 'Transfer Mix from 2mL Eppendorf tube to 96w BioER Plate. Set well number, e.g. N= 32',
    'author': 'Harley King <harley.king@luminultra.com>',
    'description': 'Aliquots user-specified volume mastermix into 96w BioER plate.',
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
    
    tempDeckMmix = protocol.load_module('temperature module gen2', '4') # mmix is stored on this alum block
    mixBlock = tempDeckMmix.load_labware('opentrons_24_aluminumblock_nest_2ml_snapcap', '2')
    
    tempdeck = protocol.load_module('temperature module gen2', '1')
    plate = tempdeck.load_labware('bioer_96_aluminumblock_200ul')
    
    # PIPETTES
    p300 = protocol.load_instrument(
        'p300_single_gen2', 'left', tip_racks=[tiprack300]
    )
     
    # REAGENTS 
    # mastermix rack
    mmix = mixBlock['A1'] # in a 2mL epp tube on tempdeck

    # USER INPUTS
    dispVol = 20 # this is the volume dispensed into each well min = 14.5, max = 20
    mmixVol = 2000 # this is the total volume in 2mL tube. Probably listed on recipe sheet. For 14.5ul in 96w plate = 14.5*96 = *1.15= 1600.8ul; For 20ul in 96w plate = 20*96 = *1.15= 2208ul
    rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
    dispNumberWells = 96 # number of wells to dispense into
    dispNumberColumns =dispNumberWells//8 # number of columns to dispense into
    
    #### COMMANDS ######
    # turn on robot rail lights
    protocol.set_rail_lights(True) # turn on lights if not on

    p300.pick_up_tip()
    mmixH = tip_heightsEpp(mmixVol, dispNumberColumns, dispVol*8) # each column gets dispensed 8x. each row goes to mix 3 times * 8 rows = 24 times
    # prewetting step for tip
    print (mmixH)
    p300.mix(2, 200, mmix.bottom(mmixH[0])) # a pre-moistened tip is more accurate. 
    i = 0 # height counter
    for col in range(dispNumberColumns):# loops through sliced or all columns on plate
        # aspirate and prepare tip and remove residual droplets
        p300.aspirate(200, mmix.bottom(mmixH[i]), rate=0.65) # could aspirate dispVol*10
        protocol.delay(seconds=2) #equilibrate
        p300.dispense(dispVol, mmix.bottom(mmixH[i]), rate=0.8) # dispense dispVol back into tube to improve volume accuracy in subsequent dispenses
        protocol.delay(seconds=1) #equilibrate
        # p300.touch_tip(mmix, v_offset=-3, speed=60)
        p300.touch_tip(mmix, v_offset=-5, speed=20)
        # dispense in column-wise manner
        for dispNo in range(8): # how many dispenses? (200-dispVol (15.8)= 184.2/15.8 = 11 )
            dest = plate[rows[dispNo]+str(col+1)] # destination well
            p300.move_to(dest.bottom(40)) # move to destination and pause for a few seconds to remove lateral motion
            # protocol.delay(seconds=1)
            p300.dispense(dispVol, dest.bottom(2), rate = 0.75) # want height to above parafilm, but not too high
            # protocol.delay(seconds=1)
            p300.move_to(dest.bottom(10)) # residual fluid coalesces
            protocol.delay(seconds=1)
            p300.move_to(dest.bottom(3)) # remove excess fluid from tip
        p300.move_to(mmix.bottom(mmixH[i]+10)) # drop waste mix back into tube
        p300.blow_out(mmix.bottom(mmixH[i]+4))
        p300.move_to(mmix.bottom(mmixH[i])) # touch tip to fluid to remove residual mmix on tubes
        i+=1 # increment height counter
    p300.drop_tip()

 