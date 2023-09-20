# imports
from opentrons import protocol_api

# metadata
metadata = {
    'protocolName': 'Use 2 Mixes and Deepwell Plate to Add to Qiagen Plate (24w, 26k).',
    'author': 'Harley King <harley.king@luminultra.com>',
    'description': '66 ul master mix dispensed into 24tubes. 22ul of DNA added to wells, mixed and added to Qiagen plate.',
    'apiLevel': '2.12'
}
##########################
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

def run(protocol: protocol_api.ProtocolContext):

    # LABWARE
    # mix_one_tubes = protocol.load_labware('vwr_24_tuberack_1500ul', '1')
    # mix_two_tubes = protocol.load_labware('vwr_24_tuberack_1500ul', '4')
    deepwell = protocol.load_labware('bioer_96_wellplate_2200ul', '11')
    mastermixes = protocol.load_labware('opentrons_24_tuberack_eppendorf_2ml_safelock_snapcap', '7')
    tiprack300 = protocol.load_labware('opentrons_96_filtertiprack_200ul', '8')
    # tiprack20 = protocol.load_labware('opentrons_96_filtertiprack_200ul', '9')
    nano_one_plate = protocol.load_labware('qiagen_24_wellplate_60ul', '1')
    nano_one_dup_plate = protocol.load_labware('qiagen_24_wellplate_60ul', '2')
    nano_two_plate = protocol.load_labware('qiagen_24_wellplate_60ul', '4')
    nano_two_dup_plate = protocol.load_labware('qiagen_24_wellplate_60ul', '5')
    # tiprack20 = protocol.load_labware('opentrons_96_filtertiprack_20ul', '9')
    tempdeck = protocol.load_module('tempdeck', '10') # have this so I don't have to move it off
    mixplate = tempdeck.load_labware('bioer_96_aluminumblock_200ul')
    
    # PIPETTES
    p300 = protocol.load_instrument(
        'p300_single_gen2', 'left', tip_racks=[tiprack300]
    )
    # p20 = protocol.load_instrument(
    #     'p20_single_gen2', 'right', tip_racks=[tiprack20]
    # )
     
    # REAGENTS 
    mix_one = mastermixes['A1'] # 1696.7ul in 2mL Epp tube
    mix_two = mastermixes['A2']

    # LISTS
    mixes_list = [mix_one, mix_two]
    # 24 samples from the plate from A1 to H3, can specific specific wells and pos controls
    deepwell_wells = [
        'A1', 'B1', 'C1', 'D1', 'E1', 'F1', 'G1', 'H1',
        'A2', 'B2', 'C2', 'D2', 'E2', 'F2', 'G2', 'H2',
        'A3', 'B3', 'C3', 'D3', 'F9', 'G9', 'H11', 'H12'
        ]
    
    # #### COMMANDS ######
    # Experiment overview
    #1-1 66ul mmix added to wells A1 to H3. 
    #1-2 22ul DNA added to wells A1 to H3 from deepwell plate.
    #1-3 Samples mixed and added to nano plates

    # 1-1 66ul mmix added to wells A1 to H3.
    
    for tubeNumber, mmix in enumerate(mixes_list):
        mmix_heights = tip_heightsEpp(1696.7, 24, 66)
        p300.pick_up_tip()
        p300.mix(2, 100, mmix.bottom(mmix_heights[5])) #wet tip for more accurate dispenses. 
        # I want to add 66ul to wells A1-H3 in mixplate
        hcounter = 0
        if tubeNumber == 0:
            col_begin = 1
            col_end = 4
        else:
            col_begin = 4
            col_end = 7
        for row in 'ABCDEFGH': 
            for col in range(col_begin, col_end):
                well = row+str(col)
                p300.aspirate(66, mmix.bottom(mmix_heights[hcounter]))
                p300.dispense(66, mixplate[well])
                p300.blow_out(mixplate[well].top(-4))
                hcounter += 1
        p300.drop_tip()



