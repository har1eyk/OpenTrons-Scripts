# imports
from opentrons import protocol_api

# metadata
metadata = {
    'protocolName': 'Dispense mastermix in 8-well strips using strip-cap tubes number.',
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
    tiprack300 = protocol.load_labware('opentrons_96_filtertiprack_200ul', '8')

    tempDeckMmix = protocol.load_module('temperature module gen2', '1') 
    mixBlock = tempDeckMmix.load_labware('opentrons_24_aluminumblock_nest_2ml_snapcap')
    
    tempdeck = protocol.load_module('temperature module gen2', '1') 
    stripTubes = tempdeck.load_labware('opentrons_96_aluminumblock_generic_pcr_strip_200ul')

    # PIPETTES
    p300 = protocol.load_instrument(
        'p300_single_gen2', 'left', tip_racks=[tiprack300]
    )
    
    # REAGENTS   
    # mmx_rack  @ position 2
    mmix = mixBlock['A4']

  
    # USER INPUTS
    dispVol = 20 # this is the volume dispensed into each well min = 14.5, max = 20
    mmixVol = 1000 # this is the total volume in 2mL tube.
    # num_of_sample_reps is another way of stating number of strips
    dispNumberStripCaps = 4 # can't exceed 6
    
    # lists
    rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
    
    #### COMMANDS ######
    # turn on robot rail lights
    protocol.set_rail_lights(True) # turn on lights if not on

    p300.pick_up_tip()
    mmixH = tip_heightsEpp(mmixVol, dispNumberStripCaps, dispVol*8) # each column gets dispensed 8x. each row goes to mix 3 times * 8 rows = 24 times
    # prewetting step for tip
    print (mmixH)
    p300.mix(2, 200, mmix.bottom(mmixH[0])) # a pre-moistened tip is more accurate. 
    i = 0 # height counter
    for col in range(dispNumberStripCaps):# loops through sliced or all columns on plate
        p300.aspirate(200, mmix.bottom(mmixH[i])) # could aspirate dispVol*10
        p300.move_to(mmix.bottom(mmixH[i]+20))
        protocol.delay(seconds=3)
        p300.dispense(dispVol, mmix.bottom(mmixH[i]+20)) # dispense dispVol back into tube to improve volume accuracy in subsequent dispenses
        protocol.delay(seconds=3) # tip for drops to coalesce
        p300.move_to(mmix.bottom(mmixH[i])) # touch tip to remove droplets
        p300.touch_tip(mmix, v_offset=-5, speed=20)
        for dispNo in range(8): # how many dispenses? (200-dispVol (15.8)= 184.2/15.8 = 11 )
            dest = stripTubes[rows[dispNo]+str(col+1)] # destination well
            p300.move_to(dest.bottom(40)) # move to destination and pause for a few seconds to remove lateral motion
            # protocol.delay(seconds=1)
            p300.dispense(dispVol, dest.bottom(2), rate = 0.75) # want height to above parafilm, but not too high
            # protocol.delay(seconds=1)
            p300.move_to(dest.bottom(5)) # residual fluid coalesces
            protocol.delay(seconds=1)
            p300.move_to(dest.bottom(3)) # remove excess fluid from tip
            p300.move_to(dest.bottom(40)) # move to destination and pause for a few seconds to remove lateral motion
        p300.move_to(mmix.bottom(mmixH[i]+10)) # drop waste mix back into tube
        p300.dispense((200-9*dispVol), mmix.bottom(mmixH[i]+10))
        p300.blow_out(mmix.bottom(mmixH[i]+4))
        p300.move_to(mmix.bottom(mmixH[i])) # touch tip to fluid to remove residual mmix on tubes
        i+=1 # increment height counter
    p300.drop_tip()

 