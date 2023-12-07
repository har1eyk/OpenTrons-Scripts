# imports
from opentrons import protocol_api

# metadata
metadata = {
    'protocolName': 'Uses a 1 Mix and 2 Tube Racks to Add to 1 Qiagen 24w, 26k NanoPlate.',
    'author': 'Harley King <harley.king@luminultra.com>',
    'description': '66 ul master mix dispensed into 24wells. 22ul of DNA added to wells, mixed and added to 1 Qiagen Nanoplate.',
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
    tempdeck = protocol.load_module('tempdeck', '10') 
    mixplate = tempdeck.load_labware('bioer_96_aluminumblock_200ul')

    # samplePlate = protocol.load_labware('bioermounted20ulfiltertipbox_96_wellplate_200ul', '4')
    sampleRackOne = protocol.load_labware('vwr_24_tuberack_1500ul', '4')
    sampleRackTwo = protocol.load_labware('vwr_24_tuberack_1500ul', '2')
    mastermixes = protocol.load_labware('opentrons_24_tuberack_eppendorf_2ml_safelock_snapcap', '11')
    tiprack300 = protocol.load_labware('opentrons_96_filtertiprack_200ul', '8')

    single_nanoplate = protocol.load_labware('qiagen_24_wellplate_60ul', '3')
    
    # PIPETTES
    p300 = protocol.load_instrument(
        'p300_single_gen2', 'left', tip_racks=[tiprack300]
    )
   
     
    # REAGENTS 
    mmix = mastermixes['A1'] # 1742.4ul in 2mL Epp tube
    # mix_two = mastermixes['A2']

    # LISTS
        
    # Define the wells for each rack
    sampleRackOne_wells = [
        'A1', 'B1', 'C1', 'D1', 'A2', 'B2', 'C2', 'D2'
        
    ]
    sampleRackTwo_wells = [
        'A1', 'B1', 'C1', 'D1'  # 1/100 Salmon, NTC, POS, NTC
    ]
    # Ensure the total number of samples does not exceed 24
    total_samples = len(sampleRackOne_wells) + len(sampleRackTwo_wells)
    assert total_samples <= 12, "Total number of samples exceeds 24"

    # Define well pairs for each sample
    # This should be adjusted based on specific well-pair requirements
    sample_to_well_pairs = [
        ('A1', 'A2'), ('B1', 'B2'), ('C1', 'C2'), ('D1', 'D2'), 
        ('E1', 'E2'), ('F1', 'F2'), ('G1', 'G2'), ('H1', 'H2'),
        ('A3', 'E3'), ('B3', 'F3'), ('C3', 'G3'), ('D3', 'H3')
    ]
        # Ensure that the number of well pairs matches the number of samples
    assert len(sample_to_well_pairs) == total_samples, "Number of well pairs does not match total samples"

    mastermix_wells = ['A1', 'B1', 'C1', 'D1', 'E1', 'F1', 'G1', 'H1', 'A2', 'B2', 'C2', 'D2']
    
    # #### COMMANDS ######
    # Experiment overview
    # 1-1 66ul mmix added to wells A1 to D2
    # 1-2 22ul DNA added to wells A1 to D2 from rack, samples mixed and added to nano plate

    # 1-1 66ul mmix added to wells A1 to D2.    
    # mmix_heights = tip_heightsEpp(1850.11, 8, 200)
    mmix_heights = tip_heightsEpp(858.00, 12, 70) #12*70 = 840
    p300.pick_up_tip()
    p300.mix(2, 200, mmix.bottom(mmix_heights[0]), rate=0.7) #wet tip for more accurate dispenses. 
    protocol.delay(seconds=2) #equilibrate
    # I want to add 66ul to wells A1-H3 in mixplate
    hcounter = 0
    for well in mastermix_wells:
        p300.aspirate(70, mmix.bottom(mmix_heights[hcounter]), rate=0.7)
        protocol.delay(seconds=2) #equilibrate
        p300.touch_tip(mmix, v_offset=-4)
        p300.dispense(66, mixplate[well].bottom(4), rate=0.7)
        protocol.delay(seconds=2) #equilibrate
        p300.touch_tip(mixplate[well], v_offset=-2)
        p300.dispense(4, mmix.bottom(mmix_heights[hcounter]))
        hcounter += 1
    p300.drop_tip()

    # 1-2 22ul DNA added to wells A1 to D2 from RACK, samples miXed and added to nanoplate
    # Process samples from both racks
    pos = 0
    for well in mastermix_wells:
        if len(sampleRackOne_wells) > 0:
            rack_well = sampleRackOne_wells.pop(0)  # Get the next well from rack one
            sample_rack = sampleRackOne
        elif len(sampleRackTwo_wells) > 0:
            rack_well = sampleRackTwo_wells.pop(0)  # Get the next well from rack two
            sample_rack = sampleRackTwo
        else:
            break  # No more samples
        # add template to mastermix in BioER plate
        p300.pick_up_tip()
        p300.aspirate(22, sample_rack[rack_well].bottom(2))
        p300.dispense(22, mixplate[well].bottom(2), rate=0.65)
        p300.mix(2, 22, mixplate[well].bottom(1), rate=0.5)
        p300.blow_out(mixplate[well].bottom(5))
        p300.move_to(mixplate[well].bottom(3)) #removes residual fluid from tip
        p300.drop_tip()
        # mixes mastermix + template and adds 40ul to nanoplate wells
        p300.pick_up_tip() # get a new tip remove variability from leftover template on previous tip
        p300.mix(2, 80, mixplate[well].bottom(1), rate=0.65)
        p300.aspirate(84, mixplate[well].bottom(1), rate=0.5)
        protocol.delay(seconds=2)
        nanoplate_well_1, nanoplate_well_2 = sample_to_well_pairs[pos]
        # Dispense into the two wells of the same nanoplate
        p300.dispense(40, single_nanoplate[nanoplate_well_1].bottom(2))
        p300.touch_tip(single_nanoplate[nanoplate_well_1], v_offset=-2, speed=40) # slow it down; don't want tip to flip-tick material into adj wells                    
        p300.dispense(40, single_nanoplate[nanoplate_well_2].bottom(2))
        p300.touch_tip(single_nanoplate[nanoplate_well_2], v_offset=-2, speed=40) # slow it down; don't want tip to flip-tick material into adj wells                    
        p300.drop_tip()
        pos +=1
        

