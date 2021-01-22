# imports
from opentrons import protocol_api

# metadata
metadata = {
    'protocolName': 'Create Primer Conc Matrix for Optimization',
    'author': 'Harley King <harley.king@luminultra.com>',
    'description': 'Create a fwd, rev primer conc matrix to optimize conc.',
    'apiLevel': '2.8'
}
##########################
def run(protocol: protocol_api.ProtocolContext):

    # LABWARE
    fuge_rack = protocol.load_labware('opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap', '6')
    tiprack300 = protocol.load_labware('opentrons_96_tiprack_300ul', '8')
    tiprack20 = protocol.load_labware('opentrons_96_tiprack_20ul', '7')
    tempdeck = protocol.load_module('tempdeck', '3')
    sample_plate = tempdeck.load_labware('biorad_96_wellplate_200ul_pcr')

    # PIPETTES
    p300 = protocol.load_instrument(
        'p300_single_gen2', 'left', tip_racks=[tiprack300]
    )
    p20 = protocol.load_instrument(
        'p20_single_gen2', 'right', tip_racks=[tiprack20]
    )
     
    # REAGENTS
    pos_control = fuge_rack['A1']
    # liquid_trash = fuge_rack['B1']
    water = fuge_rack['C1']
    mmix = fuge_rack['D1']
    
    fwd_10uM = fuge_rack['B2']
    rev_10uM = fuge_rack['D2']
    mmix_NTC = fuge_rack['C2']

    fwd_1 = fuge_rack['A4'] # e.g. 0.625uM
    fwd_2 = fuge_rack['A5'] # e.g. 1.25uM
    fwd_3 = fuge_rack['A6'] # e.g. 2.5uM
    fwd_4 = fuge_rack['B4'] # e.g. 5.0uM
    fwd_5 = fuge_rack['B5'] # e.g. 7.5uM
    fwd_6 = fuge_rack['B6'] # e.g. 10uM

    mmx_rev_1 = fuge_rack['C4'] # e.g. 0.625uM
    mmx_rev_2 = fuge_rack['C5'] # e.g. 1.25uM
    mmx_rev_3 = fuge_rack['C6'] # e.g. 2.5uM
    mmx_rev_4 = fuge_rack['D4'] # e.g. 5.0uM
    mmx_rev_5 = fuge_rack['D5'] # e.g. 7.5uM
    mmx_rev_6 = fuge_rack['D6'] # e.g. 10uM

    ###### COMMANDS ######
    # split mmix into 2 tubes: NFC and pos control
    p300.transfer(
        200.5,
        mmix.bottom(3),
        mmix_NTC.bottom(3),
        mix_before=(3, 300),
        blow_out=True,
        blowout_location='destination well')
    # to Mmix_NTC tube, add 59.5ul water, mix, aliquot to row H, all wells
    p300.transfer(
        59.5,
        water.bottom(3),
        mmix_NTC.bottom(3),
        mix_after=(3, 225),
        blow_out=True,
        blowout_location='destination well')
    p20.transfer(
        20,
        mmix_NTC.bottom(1), #does this get all mmix?
        sample_plate.rows_by_name()['H'])
    
    # to Mmix, add 20ul pos control, mix. Aliquot 203.5ul to 6 'mmix_N2_Rev tubes'
    p20.transfer(
        20,
        pos_control.bottom(1), #does this hit bottom?
        mmix.bottom(3),
        blow_out=True,
        blowout_location='destination well')
    
    all_mmx_rev = [mmx_rev_1, mmx_rev_2, mmx_rev_3, mmx_rev_4, mmx_rev_5, mmx_rev_6]
    p300.pick_up_tip() #need to mix mmix with pos control befor dist
    p300.mix(3, 300, mmix)
    p300.drop_tip()
    p300.transfer(
        203.5,
        mmix.bottom(1),#hit bottom?
        all_mmx_rev, #'list' object has no attribute 'bottom'
        disposal_volume=0, #remove 10% default 
        blow_out=True,
        blowout_location='destination well')
    
    # From 'N2_Rev_10uM' tube, add in schedule to all 6 'mmix_N2_Rev tubes'
    mmx_rev_vol = [1.3, 2.6, 5.2, 10.4, 15.6, 20.8]
    p20.transfer(
        mmx_rev_vol, #hit bottom? last amt 20.8 fully transfer?
        rev_10uM.bottom(3),
        all_mmx_rev,
        blow_out=True,
        new_tip='always'
    )
    
    # from WATER tube, add amounts in schedule to all 6 'mmix_N2_Rev' tubes, mix
    water_mmix_N2_rev_vol = [34.4, 33.1, 30.5, 25.3, 20.1, 14.9]
    p20.transfer(
        water_mmix_N2_rev_vol,
        water.bottom(3),
        all_mmx_rev,
        new_tip='always',
        blow_out=True,
        blowout_location='destination well') 
    for tube in range(len(all_mmx_rev)): #mix mmix_N2
        p300.pick_up_tip()
        p300.mix(3, 200, all_mmx_rev[tube])
        p300.drop_tip()

    # From each 'mmix_N2_rev' tube, add to each well in row as shown in figure.
    plate_rows = ['A', 'B', 'C', 'D', 'E', 'F']
    for tube in range(len(all_mmx_rev)):
        p300.pick_up_tip()
        p300.distribute(
            20,
            all_mmx_rev[tube], #does this get all mmix?
            sample_plate.rows_by_name()[plate_rows[tube]],
            new_tip='never',
            disposal_volume=10)
        p300.drop_tip()

    # Mix 100ul 'N2_Fwd' dilutions in tube by adding water and "N2_Fwd 10uM" tube as shown in schedule
    all_fwd = [fwd_1, fwd_2, fwd_3, fwd_4, fwd_5, fwd_6]
    water_fwd_vol = [93.75, 87.5, 75, 50, 25, 0]
    p300.transfer(
        water_fwd_vol,
        water.bottom(3),
        all_fwd,
        new_tip='once')

    N2_fwd_vol = [6.25, 12.5, 25, 50, 75, 100] #from N2_fwd tube @ 10uM
    for first_two in range(len(N2_fwd_vol[0:2])):
        p20.transfer(
            N2_fwd_vol[first_two],
            fwd_10uM,
            all_fwd[first_two].bottom(3),
            blow_out=True,
            new_tip='always', 
            blowout_location='destination well')
    
    for last_four in range(len(N2_fwd_vol[2:6])):
        offset = 2
        p300.transfer(
            N2_fwd_vol[last_four+offset],
            fwd_10uM,
            all_fwd[last_four+offset].bottom(3),
            blow_out=True,
            new_tip='always',
            blowout_location='destination well')
        
    for tube in range(len(N2_fwd_vol)): #mix N2_fwd
        p300.pick_up_tip()
        p300.mix(2, 90, all_fwd[tube])
        p300.drop_tip()
    
    # Pipette 1.6ul 'N2_Fwd' to 12wells starting with lowest conc first, left to right, top to bottom.
    N2_fwd_pos = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']
   
    for tube in range(len(all_fwd)): #loop through all N2_fwd tubes
        stepper = tube+tube #tube 1 to A1,A2; tube 2 to A3,A4 etc. with same tip
        for col in range(len(N2_fwd_pos[stepper:stepper+2:2])): #slices two items but only loops once
            p20.pick_up_tip()
            p20.aspirate(20, all_fwd[tube].bottom(1))
            for row in range(len(plate_rows)):
                fw = plate_rows[row]+N2_fwd_pos[stepper+col] # A1 firstwell
                sw = plate_rows[row]+N2_fwd_pos[stepper+col+1] # A2 secondwell
                p20.dispense(1.6, sample_plate[fw])
                p20.dispense(1.6, sample_plate[sw])
            p20.drop_tip()