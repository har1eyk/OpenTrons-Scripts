# imports
from opentrons import protocol_api

# metadata
metadata = {
    'protocolName': 'Create Pos Control Dilution Series for qPCR',
    'author': 'Harley King <harley.king@luminultra.com>',
    'description': 'Create a pos control dilution series on a 96w plate.',
    'apiLevel': '2.9'
}
##########################
def run(protocol: protocol_api.ProtocolContext):

    # LABWARE
    fuge_rack = protocol.load_labware('opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap', '4')
    tiprack300 = protocol.load_labware('opentrons_96_tiprack_300ul', '8')
    tiprack20 = protocol.load_labware('opentrons_96_tiprack_20ul', '9')
    tempdeck = protocol.load_module('tempdeck', '10')
    sample_plate = tempdeck.load_labware('abi_96_wellplate_250ul')

    # PIPETTES
    p300 = protocol.load_instrument(
        'p300_single_gen2', 'left', tip_racks=[tiprack300]
    )
    p20 = protocol.load_instrument(
        'p20_single_gen2', 'right', tip_racks=[tiprack20]
    )
     
    # REAGENTS
    pos_control = fuge_rack['A1'] #30-40ul
    liquid_trash = fuge_rack['B1']
    water = fuge_rack['C1'] #1500ul
    Sybr_10uM = fuge_rack['D1'] #1540ul
    
    Probe_10uM = fuge_rack['B2'] # min 300ul
    # rev_10uM = fuge_rack['D2'] # min 100ul
    # mmix_NTC = fuge_rack['C2'] # empty

    # fwd_1 = fuge_rack['A4'] # e.g. 0.625uM # empty
    # fwd_2 = fuge_rack['A5'] # e.g. 1.25uM # empty
    # fwd_3 = fuge_rack['A6'] # e.g. 2.5uM # empty
    # fwd_4 = fuge_rack['B4'] # e.g. 5.0uM # empty
    # fwd_5 = fuge_rack['B5'] # e.g. 7.5uM # empty
    # fwd_6 = fuge_rack['B6'] # e.g. 10uM # empty

    # mmx_rev_1 = fuge_rack['C4'] # e.g. 0.625uM # empty
    # mmx_rev_2 = fuge_rack['C5'] # e.g. 1.25uM # empty
    # mmx_rev_3 = fuge_rack['C6'] # e.g. 2.5uM # empty
    # mmx_rev_4 = fuge_rack['D4'] # e.g. 5.0uM # empty
    # mmx_rev_5 = fuge_rack['D5'] # e.g. 7.5uM # empty
    # mmx_rev_6 = fuge_rack['D6'] # e.g. 10uM # empty
    # lists
    plate_col = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']
    all_mmx_rev = [mmx_rev_1, mmx_rev_2, mmx_rev_3, mmx_rev_4, mmx_rev_5, mmx_rev_6]
    plate_rows = ['B', 'C', 'D', 'E', 'F', 'G', 'H']
    # all_fwd = [fwd_1, fwd_2, fwd_3, fwd_4, fwd_5, fwd_6]

    ##### COMMANDS ######
    # transfer sybr to plate, 3x per well
    p300.transfer(
        54,
        mmix.bottom(3),
        mmix_NTC.bottom(3),
        mix_before=(3, 300),
        blow_out=True,
        blowout_location='destination well')
    
    # to mmix_NTC tube, add 16 ul N2_fwd and N2_rev primers
    p20.transfer(
        16,
        fwd_10uM.bottom(1),
        mmix_NTC.bottom(3),
        blow_out=True,
        blowout_location='destination well')
    
    p20.transfer(
        16,
        rev_10uM.bottom(1),
        mmix_NTC.bottom(3),
        blow_out=True,
        blowout_location='destination well')

    # to Mmix_NTC tube, add 59.5ul water, mix, aliquot to row H, all wells
    p300.pick_up_tip()
    p300.aspirate(27.4, water.bottom(5)) #1500ul
    p300.dispense(27.4, mmix_NTC)
    p300.mix(3, 225)
    
    p300.aspirate(250, mmix_NTC.bottom(0.5)) #12*10+20=240+10=250
    for well in plate_col:
        well_pos = 'H'+well
        p300.flow_rate.dispense = 50 #92.86 default
        p300.dispense(20, sample_plate[well_pos])
        p300.touch_tip()
    p300.flow_rate.dispense = 92.86 #92.86 default, return to normal
    p300.drop_tip()

    # to Mmix, add 20ul pos control, mix. Aliquot 203.5ul to 6 'mmix_N2_Rev tubes'
    p20.transfer(
        20,
        pos_control.bottom(0.5), #does this hit bottom?
        mmix.bottom(3),
        blow_out=True,
        blowout_location='destination well')
    
    dist_from_bot = [20, 15, 10, 8, 4, 0.2]
    p300.pick_up_tip() #need to mix mmix with pos control befor dist
    p300.mix(3, 300, mmix.bottom(20)) #1361.7ul
    for i in range(len(all_mmx_rev)):
        p300.flow_rate.aspirate = 50
        p300.aspirate(203.5, mmix.bottom(dist_from_bot[i]))
        p300.well_bottom_clearance.dispense = 10
        p300.dispense(203.5, all_mmx_rev[i])
        p300.blow_out()
    p300.drop_tip()
    
    # From 'N2_Rev_10uM' tube, add in schedule to all 6 'mmix_N2_Rev tubes'
    mmx_rev_vol = [1.3, 2.6, 5.2, 10.4, 15.6, 20.8]
    p20.transfer(
        mmx_rev_vol, #hit bottom? last amt 20.8 fully transfer?
        rev_10uM.bottom(1),
        all_mmx_rev,
        blow_out=True, #!blowout distance needs to be closer to bottom of well
        new_tip='always',
        blowout_location='destination well' #!need a blowout location here
    )
    
    # from WATER tube, add amounts in schedule to all 6 'mmix_N2_Rev' tubes
    water_mmix_N2_rev_vol = [34.4, 33.1, 30.5, 25.3, 20.1, 14.9]
    p20.transfer(
        water_mmix_N2_rev_vol,
        water.bottom(3),
        all_mmx_rev,
        new_tip='always',
        blow_out=True,
        blowout_location='destination well') 

    # mix mmix_N2_rev tubes and add to each well in row as shown in figure.
    for i in range(len(all_mmx_rev)): #mix mmix_N2 #!combine mixing and dispensing step below
        p300.pick_up_tip()
        p300.flow_rate.aspirate = 92.86 #reset to default
        p300.flow_rate.dispense = 92.86 #reset to default
        p300.mix(3, 200, all_mmx_rev[i].bottom(2)) #in well: 
        p300.flow_rate.aspirate = 40
        p300.flow_rate.dispense = 40
        p300.aspirate(232, all_mmx_rev[i].bottom(0.4)) # 23.4*20=220.8+9.2= 232ul
        protocol.delay(seconds=2) #wait for equilibration
        p300.dispense(2, liquid_trash) #remove case of air in tip
        p300.touch_tip() #prime tip
        for col in plate_col:  # distribute to every well in row
            well_pos = plate_rows[i]+col
            p300.dispense(18.4, sample_plate[well_pos].bottom(0.5))
            p300.touch_tip()
        p300.drop_tip()
    p300.flow_rate.aspirate = 92.86 #default
    p300.flow_rate.dispense = 92.86

    # Mix 100ul 'N2_Fwd' dilutions in tube by adding water and "N2_Fwd 10uM" tube as shown in schedule
    water_fwd_vol = [93.75, 87.5, 75, 50, 25, 0]
    p300.transfer(
        water_fwd_vol,
        water.bottom(3),
        all_fwd,
        touch_tip=True,
        new_tip='once')

    N2_fwd_vol = [6.25, 12.5, 25, 50, 75, 100] #from N2_fwd tube @ 10uM
    for first_two in range(len(N2_fwd_vol[0:2])):
        p20.transfer(
            N2_fwd_vol[first_two],
            fwd_10uM,
            all_fwd[first_two].bottom(3),
            new_tip='always', 
            blowout_location='destination well')
    
    for last_four in range(len(N2_fwd_vol[2:6])):
        offset = 2
        p300.transfer(
            N2_fwd_vol[last_four+offset],
            fwd_10uM,
            all_fwd[last_four+offset].bottom(1),
            new_tip='always',
            blowout_location='destination well') #! last well, misses aspiration, about 20ul remaining, about 50ul short. More in source tube.
    # mix N2_fwd    
    for tube in range(len(N2_fwd_vol)):
        p300.pick_up_tip()
        p300.mix(2, 78, all_fwd[tube])
        p300.drop_tip()
    
    # Pipette 1.6ul 'N2_Fwd' to 12wells starting with lowest conc first, left to right, top to bottom.
    for tube in range(len(all_fwd)): #loop through all N2_fwd tubes
        stepper = tube+tube #tube 1 to A1,A2; tube 2 to A3,A4 etc. with same tip
        for col in range(len(plate_col[stepper:stepper+2:2])): #slices two items but only loops once
            p20.pick_up_tip()
            p20.aspirate(20, all_fwd[tube].bottom(1))
            for row in range(len(plate_rows)):
                fw = plate_rows[row]+plate_col[stepper+col] # A1 firstwell
                sw = plate_rows[row]+plate_col[stepper+col+1] # A2 secondwell
                p20.dispense(1.6, sample_plate[fw])
                p20.touch_tip()
                p20.dispense(1.6, sample_plate[sw])
                p20.touch_tip()
            p20.drop_tip()