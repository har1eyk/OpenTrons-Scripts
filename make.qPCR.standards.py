# imports
from opentrons import protocol_api

# metadata
metadata = {
    'protocolName': 'Create Pos Control Dilution Series for qPCR',
    'author': 'Harley King <harley.king@luminultra.com>',
    'description': 'Create a 12-tube pos control dilution series on a 24-well rack.',
    'apiLevel': '2.9'
}
##########################
def run(protocol: protocol_api.ProtocolContext):

    # LABWARE
    fuge_rack = protocol.load_labware('opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap', '4')
    water_rack = protocol.load_labware('opentrons_10_tuberack_falcon_4x50ml_6x15ml_conical', '5') 
    # tiprack300 = protocol.load_labware('opentrons_96_tiprack_300ul', '8')
    tiprack300 = protocol.load_labware('opentrons_96_filtertiprack_200ul', '8')
    # tiprack20 = protocol.load_labware('opentrons_96_tiprack_20ul', '9')
    tiprack20 = protocol.load_labware('opentrons_96_filtertiprack_20ul', '9')
    tempdeck = protocol.load_module('tempdeck', '10')
    stds_plate = tempdeck.load_labware('abi_96_wellplate_250ul')
    
    std_1 = fuge_rack['A3'] # e.g. 10nM pos control DNA, 990ul Water
    std_2 = fuge_rack['A4'] # 900ul water
    std_3 = fuge_rack['A5'] # 900ul water
    std_4 = fuge_rack['A6'] # 900ul water
    std_5 = fuge_rack['B3'] # 900ul water
    std_6 = fuge_rack['B4'] # 900ul water 
    std_7 = fuge_rack['B5'] # 900ul water
    std_8 = fuge_rack['B6'] # 900ul water
    std_9 = fuge_rack['C3'] # 900ul water
    std_10 = fuge_rack['C4'] # 900ul water
    std_11 = fuge_rack['C5'] # 900ul water
    std_12 = fuge_rack['C6'] # 900ul water

    # PIPETTES
    p300 = protocol.load_instrument(
        'p300_single_gen2', 'left', tip_racks=[tiprack300]
    )
    p20 = protocol.load_instrument(
        'p20_single_gen2', 'right', tip_racks=[tiprack20]
    )
     
    # REAGENTS
    # water = water_rack['A1'] # 15mL concial tube with water, filled between 10 and 13mL mark
    water = fuge_rack['B1']
    pos_control = fuge_rack['A1'] #30-40ul @1uM
    mm_Sybr = fuge_rack['D1'] # 684ul
    mm_Probe = fuge_rack['D2'] # 684ul
    
    # LISTS
    sybr_wells=['A1', 'B1', 'C1', 'D1', 'E1', 'F1', 'G1', 'A4', 'B4', 'C4', 'D4', 'E4', 'F4']
    probe_wells=['A7', 'B7', 'C7', 'D7', 'E7', 'F7', 'G7', 'A10', 'B10', 'C10', 'D10', 'E10', 'F10']
    std_wells = [std_1, std_2, std_3, std_4, std_5, std_6, std_7, std_8, std_9, std_10, std_11, std_12]
    tip_heights = [] #in future, put tip heights here.
    
    # ##### COMMANDS ######
    # ## Mix, pipette 54ul mm_Sybr, mm_Probe to each well on plate 
    # for mmix, dest_wells in zip( # loop through both mmix and wells list
    #     list([mm_Sybr, mm_Probe]),
    #     list([sybr_wells, probe_wells])):
    #     p300.pick_up_tip()
    #     p300.mix(3, 200, mmix.bottom(10)) #10mm from bottom
    #     p300.flow_rate.aspirate = 30
    #     p300.flow_rate.dispense = 40
    #     for well in dest_wells:
    #         p300.well_bottom_clearance.aspirate = 0.6 #mm
    #         p300.aspirate(56, mmix)
    #         protocol.delay(seconds=3) #tip equilibrate
    #         p300.move_to(mmix.bottom(35)) # excess tip fluid condense 
    #         protocol.delay(seconds=1) #tip equilibrate
    #         p300.touch_tip()
    #         protocol.delay(seconds=1) #tip residue form outside droplet
    #         p300.move_to(mmix.bottom(38)) # move to center, don't catch front lip of tube
    #         protocol.delay(seconds=3) #tip residue form outside droplet
    #         p300.touch_tip()
    #         p300.dispense(56, stds_plate[well])
    #         p300.touch_tip()
    #     p300.drop_tip()
    #     p300.flow_rate.aspirate = 92.86 #reset to default
    #     p300.flow_rate.dispense = 92.86 #reset to default
    #     p300.well_bottom_clearance.aspirate = 10 #mm default
    
    # ## Make std dilution series      
    # # Make 10nM pos control
    # p20.transfer(
    #     10,
    #     pos_control, #1uM
    #     std_1.bottom(20),
    #     mix_after=(2, 20), # remove residual fluid from tip
    #     blow_out=True,
    #     touch_tip=True,
    #     blowout_location='destination well'
    # )
   
    # serial dilutions in microfuge tubes, 10% diliutions
    p300.pick_up_tip()
    for i in range(len(std_wells)-2): #don't want water tube to be included
        p300.well_bottom_clearance.aspirate = 15 #mm come up for mixing 
        p300.well_bottom_clearance.dispense = 15 #mm 
        if i==0 or i==10: # first or last tube
            p300.mix(3, 200, std_wells[i]) # need to add mixes to first and last tubes
        p300.mix(4, 200, std_wells[i])
        # p300.well_bottom_clearance.aspirate = 10 #mm 
        p300.flow_rate.aspirate = 40 #slow aspirate; no air
        p300.aspirate(100, std_wells[i])
        p300.touch_tip()
        p300.flow_rate.dispense = 40 #slow dispense
        p300.dispense(100, std_wells[i+1])
        p300.flow_rate.aspirate = 92.86 #default
        p300.flow_rate.dispense = 92.86 #default
        p300.mix(2, 200, std_wells[i+1]) #remove residual inside tip
        p300.move_to(std_wells[i+1].bottom(15)) #come up for blowout
        p300.blow_out()
        protocol.delay(seconds=2) #wait for bubbles to subside
    p300.well_bottom_clearance.dispense = 1 #mm default
    p300.well_bottom_clearance.aspirate = 1 #mm default
    p300.flow_rate.aspirate = 92.86 #default
    p300.flow_rate.dispense = 92.86 #default
    p300.drop_tip()

    # add 6ul stds to SYBR, PROBE mmxs into plate wells and dispense into neighboring wells
    p20.flow_rate.aspirate = 7.56 #default
    p20.flow_rate.dispense = 7.56 #default
    for mmix in list([sybr_wells, probe_wells]): #loop through mmixes
        for i in range(len(std_wells)): #loop 12x
            p20.pick_up_tip()
            p300.pick_up_tip()
            # move 6ul from std tube to well
            p20.well_bottom_clearance.aspirate = 15 
            p20.aspirate(6, std_wells[i])
            p20.touch_tip() #aspirate 6 ul from std
            p20.well_bottom_clearance.dispense = 2 #
            p20.dispense(6, stds_plate[mmix[i]]) #dispense into 54ul in sybr_wells[i] on plate
            p20.mix(2, 20) # remove inside soln
            p20.move_to(stds_plate[mmix[i]].bottom(5)) #above mmix solution
            p20.blow_out()
            p20.touch_tip()
            # p300 necessary for mixing
            p300.move_to(stds_plate[mmix[i]].bottom(1)) #above mmix solution
            p300.mix(4, 50, stds_plate[mmix[i]].bottom(2)) # can't be mixed homogenously with p20 #ivetried
            p300.move_to(stds_plate[mmix[i]].bottom(5)) #above mmix solution
            protocol.delay(seconds=2) #outside fluid coalesce 
            p300.blow_out()
            p300.touch_tip()
            p20.well_bottom_clearance.aspirate = 2 # bring up for more forceful mix
            p20.well_bottom_clearance.dispense = 2 # move close to avoid air gap
            for x in range(1,3): # need int 1 and 2
                p20.aspirate(20, stds_plate[mmix[i]]) # asp from 54ul, dispense to neighbor well
                protocol.delay(seconds=2) #equilibrate
                # find digits in well, A1 and A10 and puts into list
                findNums = [int(i) for i in mmix[i].split()[0] if i.isdigit()]
                # joins nums from list [1, 0] -> 10 type = string
                colNum = ''.join(map(str, findNums))
                # this finds row
                row = mmix[i].split()[0][0]
                dest = row+str(int(colNum)+x) # row + neighbor well i.e. 1, 2
                p20.dispense(20, stds_plate[dest])
                p20.touch_tip()
            p300.drop_tip()
            p20.drop_tip()