# imports
from opentrons import protocol_api

# metadata
metadata = {
    'protocolName': 'Create Pos Control Dilution Series for qPCR',
    'author': 'Harley King <harley.king@luminultra.com>',
    'description': 'Create a pos control dilution series on a 96w plate. Created in VS_Code at office. ',
    'apiLevel': '2.9'
}
##########################
def run(protocol: protocol_api.ProtocolContext):

    # LABWARE
    fuge_rack = protocol.load_labware('opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap', '4')
    water_rack = protocol.load_labware('opentrons_10_tuberack_falcon_4x50ml_6x15ml_conical', '5') 
    tiprack300 = protocol.load_labware('opentrons_96_tiprack_300ul', '8')
    tiprack20 = protocol.load_labware('opentrons_96_tiprack_20ul', '9')
    tempdeck = protocol.load_module('tempdeck', '10')
    stds_plate = tempdeck.load_labware('abi_96_wellplate_250ul')

    # PIPETTES
    p300 = protocol.load_instrument(
        'p300_single_gen2', 'left', tip_racks=[tiprack300]
    )
    p20 = protocol.load_instrument(
        'p20_single_gen2', 'right', tip_racks=[tiprack20]
    )
     
    # REAGENTS
    pos_control = fuge_rack['A1'] #30-40ul @1uM
    water = water_rack['A1'] # 15mL concial tube with water, filled between 10 and 13mL mark
    mm_Sybr = fuge_rack['D1'] # 684ul
    mm_Probe = fuge_rack['D2'] # 684ul
    pos_10nM = fuge_rack['B1'] # min 990ul
    
    # lists
    sybr_wells=['A1', 'B1', 'C1', 'D1', 'E1', 'F1', 'G1', 'A4', 'B4', 'C4', 'D4', 'E4']
    probe_wells=['A7', 'B7', 'C7', 'D7', 'E7', 'F7', 'G7', 'A10', 'B10', 'C10', 'D10', 'E10']
    std_water = [180, 180, 180, 180, 180, 180, 180, 180, 180, 180, 180]
    std_wells = ['H1', 'H2', 'H3', 'H4', 'H5', 'H6', 'H7', 'H8', 'H9', 'H10', 'H11', 'H12']
    
    ##### COMMANDS ######
    # Mix, pipette 54ul mm_Sybr, mm_Probe to each well on plate 
    for mmix, dest_wells in zip( # loop through both mmix and wells list
        list([mm_Sybr, mm_Probe]),
        list([sybr_wells, probe_wells])):
        p300.pick_up_tip()
        p300.mix(3, 300, mmix.bottom(10)) #10mm from bottom
        p300.flow_rate.aspirate = 40
        p300.flow_rate.dispense = 40
        for well in dest_wells:
            p300.transfer(
                54,
                mmix,
                stds_plate[well].bottom(0.2),
                touch_tip=True,
                new_tip='never'
            )
        p300.drop_tip()
        p300.flow_rate.aspirate = 92.86 #reset to default
        p300.flow_rate.dispense = 92.86 #reset to default
    
    # Make std dilution series
    # add 180ul to stds wells except H1
    p300.pick_up_tip()
    for i, well in enumerate(std_wells[1:]):
        p300.well_bottom_clearance.aspirate = 50 #mm
        p300.aspirate(std_water[i]+20, water)
        p300.touch_tip()
        p300.dispense(std_water[i], stds_plate[std_wells[i+1]]) #skip H1, offset by 1
        p300.touch_tip()
        p300.blow_out(water.bottom(100))
    p300.well_bottom_clearance.aspirate = 1 #mm, reset to default
    p300.drop_tip()
        
    # Make 10nM pos control
    p20.transfer(
        10,
        pos_control, #1uM
        pos_10nM.bottom(2),
    )
   
    # mix 10nM pos control, add to plate
    p300.pick_up_tip()
    p300.mix(5, 300, pos_10nM.bottom(10))
    # add 200ul to H1
    p300.transfer(
        200,
        pos_10nM,
        stds_plate['H1'],
        new_tip='never'
    )
    p300.drop_tip()

    # make std serial dilutions
    p300.pick_up_tip()
    p20.pick_up_tip()
    for i in range(len(std_wells)-1):
        # p300.mix(2, 180, stds_plate[std_wells[i]])
        # p300.flow_rate.aspirate = 40 #slow draw to avoid air
        # p300.aspirate(20, stds_plate[std_wells[i]])
        p20.well_bottom_clearance.aspirate = 3 #mm default
        p20.well_bottom_clearance.dispense = 3 #mm default
        p20.aspirate(20, stds_plate[std_wells[i]])
        p20.touch_tip()
        # p300.flow_rate.aspirate = 92.86 #default
        p20.dispense(20, stds_plate[std_wells[i+1]])
        p20.mix(2, 20, stds_plate[std_wells[i+1]]) #remove residual inside tip
        p20.move_to(stds_plate[std_wells[i+1]].bottom(6)) #come up for blowout
        p20.blow_out()
        protocol.delay(seconds=2) #wait for bubbles to subside
        p300.well_bottom_clearance.dispense = 3 #mm for mixing
        p300.well_bottom_clearance.aspirate = 3 #mm for mixing
        p300.mix(2, 180, stds_plate[std_wells[i+1]])
        p300.move_to(stds_plate[std_wells[i+1]].bottom(6)) #come up for blowout
        p300.blow_out() #expel air gap from mixing
        protocol.delay(seconds=2) #wait for bubbles to subside
    p300.well_bottom_clearance.dispense = 1 #mm default
    p20.well_bottom_clearance.dispense = 1 #mm default
    p300.well_bottom_clearance.aspirate = 1 #mm default
    p20.well_bottom_clearance.aspirate = 1 #mm default
    p300.drop_tip()
    p20.drop_tip()

    # add 6ul stds to SYBR, PROBE mmxs and dispense into neighboring wells
    for mmix in list([sybr_wells, probe_wells]): #loop through mmixes
        for i in range(len(std_wells)): #loop 12x
            p20.pick_up_tip()
            p20.aspirate(6, stds_plate[std_wells[i]]) #aspirate 6 ul from std
            p20.dispense(6, stds_plate[mmix[i]]) #dispense into 54ul in sybr_wells[i] on plate
            p20.well_bottom_clearance.dispense = 20 # bring up for more forceful mix
            p20.mix(3, 20)
            p20.well_bottom_clearance.dispense = 2 # move close to avoid air gap
            for x in range(1,3): # need int 1 and 2
                p20.aspirate(20, stds_plate[mmix[i]]) # asp from 54ul, dispense to neighbor well
                # find digits in well, A1 vs A10 and puts into list
                findNums = [int(i) for i in mmix[i].split()[0] if i.isdigit()]
                # joins nums from list [1, 0] -> 10 type = string
                colNum = ''.join(map(str, findNums))
                # this finds row
                row = mmix[i].split()[0][0]
                dest = row+str(int(colNum)+x) # row + neighbor well
                p20.dispense(20, stds_plate[dest])
                p20.touch_tip()
            p20.drop_tip()