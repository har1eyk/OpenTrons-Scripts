from opentrons import protocol_api
from opentrons.commands.commands import dispense, drop_tip

# metadata
metadata = {
    'protocolName': 'Create Pos Control Dilution Series for qPCR and mixes Ht total prokayrote',
    'author': 'Harley King / Tim Carter',
    'description': 'Create a 15-tube pos control dilution series on a 24-well rack, thenm',
    'apiLevel': '2.11'
}
##########################


def run(protocol: protocol_api.ProtocolContext):

    # LABWARE
    fuge_rack = protocol.load_labware('vwr_24_tuberack_1500ul', '1')
    std_rack = protocol.load_labware('vwr_24_tuberack_1500ul', '2')
    tiprack300 = protocol.load_labware('opentrons_96_filtertiprack_200ul', '8')
    tiprack20 = protocol.load_labware('opentrons_96_filtertiprack_20ul', '9')
    tempdeck = protocol.load_module('tempdeck', '10') # have this so I don't have to move it off
    holder_1 = protocol.load_labware('8wstriptubesonfilterracks_96_aluminumblock_250ul', '3')
    holder_2 = protocol.load_labware('8wstriptubesonfilterracks_96_aluminumblock_250ul', '6')
    stds_plate = tempdeck.load_labware('abi_96_wellplate_250ul')
    

    # PIPETTES
    p300 = protocol.load_instrument(
        'p300_single_gen2', 'left', tip_racks=[tiprack300]
    )
    p20 = protocol.load_instrument(
        'p20_single_gen2', 'right', tip_racks=[tiprack20]
    )
     
    # REAGENTS 
    std_1 = std_rack['A1'] # 900ul Water
    std_2 = std_rack['A2'] # 900ul water
    std_3 = std_rack['A3'] # 900ul water
    std_4 = std_rack['A4'] # 900ul water
    std_5 = std_rack['A5'] # 900ul water
    std_6 = std_rack['A6'] # 900ul water 
    std_7 = std_rack['B1'] # 900ul water
    std_8 = std_rack['B2'] # 900ul water
    std_9 = std_rack['B3'] # 900ul water
    std_10 = std_rack['B4'] # 900ul water
    std_11 = std_rack['B5'] # 900ul water
    std_12 = std_rack['B6'] # 900ul water
    std_13 = std_rack['C1'] # 900ul water
    std_14 = std_rack['C2'] # 900ul water
    std_15 = std_rack['C3'] # 900ul water

    pos_control = fuge_rack['A1'] # 100-1000ul pos control @1uM
    mmp_tube = fuge_rack['A2'] #500 uL of master mixs and 400uL of primers
    waste = fuge_rack['D6'] # waste
    water = fuge_rack['A3'] # 100 uL water

    # LISTS
    std_wells = [std_1, std_2, std_3, std_4, std_5, std_6, std_7, std_8, std_9, std_10, std_11, std_12, std_13, std_14, std_15]
    std_conc = [std_4, std_5, std_6, std_7, std_8,]
    cols = [1, 3, 5, 7, 9, 11]
    rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
    
    
    
    ### COMMANDS ######
    #Make std dilution series      
    #Make 10nM pos control, std_1
    p300.transfer(
        100,
        pos_control.bottom(2), #1uM
        std_1.bottom(20),
        mix_after=(3, 200), # remove residual fluid from tip
        touch_tip=False
    )
   
    # serial dilutions in microfuge tubes, 10% diliutions
    for i in range(len(std_wells)-1): 
        h_mix = 20
        p300.pick_up_tip()
        p300.mix(2, 200, std_wells[i].bottom(8)) # mix low
        p300.mix(2, 200, std_wells[i].bottom(14)) # mix mid
        p300.mix(5, 200, std_wells[i].bottom(h_mix)) #mix hi
        p300.aspirate(100, std_wells[i].bottom(h_mix), rate=0.4)
        p300.touch_tip()
        p300.dispense(100, std_wells[i+1].bottom(14)) # better mixing with mid dispense
        p300.blow_out(std_wells[i+1].bottom(h_mix))# blow out just below the surface
        p300.drop_tip()
        if i==len(std_wells)-2: # last tube
            p300.pick_up_tip()
            p300.mix(2, 200, std_wells[i+1].bottom(8)) # mix low
            p300.mix(2, 200, std_wells[i+1].bottom(14)) # mix mid
            p300.mix(5, 200, std_wells[i+1].bottom(h_mix)) #mix hi
            p300.blow_out(std_wells[i+1].bottom(h_mix))# blow out just below the surface
    p300.drop_tip()


    #add master mix and primers to PRC tubes
    for col in cols[0:2]:
        p20.pick_up_tip()
        for row in rows:
            p20.aspirate(18, mmp_tube)
            p20.touch_tip(v_offset=-5)
            p20.dispense(18, holder_1[row + str(col)])
        p20.drop_tip()

    #add first 4 standards to upper half of tubes
    count = 0 # keep track of standard
    for row in rows:
        p20.pick_up_tip()
        p20.aspirate(6, std_conc[count]) #take from standand 
        p20.touch_tip()
        for col in cols[0:2]:
            p20.dispense(2, holder_1[row + str(col)]) # dispense in PCR tubes  
            p20.touch_tip()
        p20.dispense(2, waste)
        p20.blow_out(waste)
        p20.drop_tip()
        count = count + 1
        if count == 4:
            break

    # #add first 4 standards to lower half of tubes
    count = 0 #reset count
    for row in rows[4: ]:
        p20.pick_up_tip()
        p20.aspirate(4, std_conc[count])
        p20.touch_tip()
        for col in cols[0:1]:
            p20.dispense(2, holder_1[row + str(col)])
            p20.touch_tip()
        p20.dispense(2, waste)
        p20.blow_out(waste)
        p20.drop_tip()
        count = count + 1     
        if count == 4:
            break       
    
    #add final standard 
    for row in rows[4:7]:
        p20.pick_up_tip()
        p20.aspirate(8, std_conc[count])
        p20.touch_tip()
        for col in cols[1:2]:
            p20.dispense(2, holder_1[row + str(col)])
            p20.touch_tip()
        p20.dispense(2, waste)
        p20.blow_out(waste)
        p20.drop_tip()
        
    # add water to last 3 wells
    for row in rows[7:8]:
        p20.pick_up_tip()
        p20.aspirate(4, water)
        p20.touch_tip()
        for col in cols[1:2]:
            p20.dispense(2, holder_1[row + str(col)])
            p20.touch_tip()
        p20.dispense(2, waste)
        p20.blow_out(waste)
        p20.drop_tip()
       


