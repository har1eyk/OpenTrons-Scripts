from operator import countOf
from opentrons import protocol_api
from opentrons.commands.commands import dispense, drop_tip

# metadata
metadata = {
    'protocolName': 'Standard Curve Validation v1.2.1',
    'author': 'Tim Carter',
    'description': 'Creates 3 rep 5 point standard curves in increments of 16 25Oct22',
    'apiLevel': '2.11'
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
    for i in range(int(steps)):
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


def run(protocol: protocol_api.ProtocolContext):

    # LABWARE
    pos_rack = protocol.load_labware('vwr_24_tuberack_1500ul', '1')
    fuge_rack = protocol.load_labware('vwr_24_tuberack_1500ul', '2')
    water_rack = protocol.load_labware('opentrons_10_tuberack_nest_4x50ml_6x15ml_conical', '3')
    holder_1 = protocol.load_labware('8wstriptubesonfilterracks_96_aluminumblock_250ul', '7')
    holder_2 = protocol.load_labware('8wstriptubesonfilterracks_96_aluminumblock_250ul', '4')
    tiprack300 = protocol.load_labware('opentrons_96_filtertiprack_200ul', '8')
 

    # PIPETTES
    p300 = protocol.load_instrument(
        'p300_single_gen2', 'left', tip_racks=[tiprack300]
    )
    # p20 = protocol.load_instrument(
    #     'p20_single_gen2', 'right', tip_racks=[tiprack20]
    # )
    
    # in multiples of 16, not above 96
    reaction_number = 32
    

    # REAGENTS 
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

    pos_control = pos_rack['A1'] # 100-1000ul pos control @1uM
    # waste = pos_rack['D6']
    
    water = water_rack['A1'] # 15mL water in 15mL conical
   

    # LISTS
    std_wells = [std_1, std_2, std_3, std_4, std_5, std_6, std_7, std_8, std_9, std_10, std_11, std_12, std_13, std_14, std_15]
    std_conc = [std_6, std_7, std_8, std_9, std_10]
    cols = [1, 3, 5, 7, 9, 11]
    rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
    
    ###Tube Output###
    # example std_conc list [std_6, std_7, std_8, std_9, std_10]	
	# ________________________
    # |    std_9	std_9    |   
    # |    std_8	std_8    |   
    # |    std_7	std_7    |   
    # |    std_6	std_6    |   
    # |    std_9	std_10   |   
    # |    std_8	std_10   |   
    # |    std_7	std_10   |     
    # |    std_6	water    |
    # |______________________|
    
    #this will replicate each column individually when the number of reactions is increased

    ### COMMANDS ######
    # Make std dilution series      
    # Make 10nM pos control, std_1
    p300.pick_up_tip()
    waterH = fifteen_ml_heights(15000, 76 + (reaction_number/16), 180) # 180*5=900, 15*5 = 75 total steps + water for neg
    dispenseH = tip_heights(900, 5, 180)
    for i, stdTube in enumerate(std_wells):
        for h in range(1,6): #1 to 5
            p300.aspirate(180, water.bottom(waterH[5*i+h]))
            p300.dispense(180, stdTube.bottom(dispenseH[-h])) # want to reverse heights
    p300.drop_tip()

    # Make std dilution series      
    # Make 10nM pos control, std_1
    p300.transfer(
        100,
        pos_control.bottom(2), #1uM
        std_1.bottom(20),
        mix_after=(3, 200), # remove residual fluid from tip
        touch_tip=True
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


    std_conc.reverse() #reverses the list order so the lowest concetrations are used first

    if reaction_number <= 48:
        rxn_num = reaction_number
        rxn_coeff = int(rxn_num/8)
        vol = (rxn_coeff * 20) + ((rxn_coeff * 20)/5) 
        # add water to bottom right
        p300.pick_up_tip()
        for row in rows[7:]:
            p300.aspirate(int(vol/2), water.bottom(waterH[5*i+h]))
            p300.touch_tip()
            for col in cols[int(rxn_coeff/2):int(rxn_coeff)]:
                p300.move_to(holder_1[row + str(col)].bottom(40))
                p300.dispense(20, holder_1[row + str(col)].bottom(6), rate=0.75)
                p300.touch_tip()
                p300.move_to(holder_1[row + str(col)].top())
            # p300.dispense(int((rxn_coeff * 20)/10) , std_conc[count].bottom(5))
            # p300.blow_out(waste.bottom(5))
        p300.drop_tip()

        # add last(first becuse list is reversed)dilution
        count = 0
        p300.pick_up_tip()
        for row in rows[4:7]:
            p300.aspirate(int(vol/2), std_conc[count])
            p300.touch_tip()
            for col in cols[int(rxn_coeff/2):int(rxn_coeff)]:
                p300.move_to(holder_1[row + str(col)].bottom(40))
                p300.dispense(20, holder_1[row + str(col)].bottom(6), rate=0.75)
                p300.touch_tip()
                p300.move_to(holder_1[row + str(col)].top())
            # p300.dispense(int((rxn_coeff * 20)/10) , std_conc[count].bottom(5))
            # p300.blow_out(waste.bottom(3))
            p300.touch_tip()
        p300.drop_tip()

        # add dil to top half of rows
        count = 1 # keep track of standard 
        for row in rows[:4]:
            p300.pick_up_tip()
            p300.aspirate(vol, std_conc[count])
            p300.touch_tip()
            for col in cols[:rxn_coeff]:
                p300.move_to(holder_1[row + str(col)].bottom(40))
                p300.dispense(20, holder_1[row + str(col)].bottom(6), rate=0.75)
                p300.touch_tip()
                p300.move_to(holder_1[row + str(col)].top())
            # p300.dispense(20, waste.bottom(5))
            #p300.blow_out(waste.bottom(5))
            p300.drop_tip()
            count += 1 

        # add dil to bottom half of rows
        count = 1
        for row in rows[4:]:
            p300.pick_up_tip()
            p300.aspirate(int(vol/2), std_conc[count])
            p300.touch_tip()
            for col in cols[:int(rxn_coeff/2)]:
                p300.move_to(holder_1[row + str(col)].bottom(40))
                p300.dispense(20, holder_1[row + str(col)].bottom(6), rate=0.75)
                p300.touch_tip()
                p300.move_to(holder_1[row + str(col)].top())
            # p300.dispense(20, waste.bottom(5))
            #p300.blow_out(waste.bottom(5))
            p300.drop_tip()
            count += 1 
    # if reaction number is more than 48, fill 1st holder then mmove on to holder 2
    else:
        rxn_num = 48
        rxn_coeff = int(rxn_num/8)
        vol = (rxn_coeff * 20) + ((rxn_coeff * 20)/5) 
        # add water to bottom right
        p300.pick_up_tip()
        for row in rows[7:]:
            p300.aspirate(int(vol/2), water.bottom(waterH[5*i+h]))
            p300.touch_tip()
            for col in cols[int(rxn_coeff/2):int(rxn_coeff)]:
                p300.move_to(holder_1[row + str(col)].bottom(40))
                p300.dispense(20, holder_1[row + str(col)].bottom(6), rate=0.75)
                p300.touch_tip()
                p300.move_to(holder_1[row + str(col)].top())
            # p300.dispense(int((rxn_coeff * 20)/10) , std_conc[count].bottom(5))
            # p300.blow_out(waste.bottom(5))
        p300.drop_tip()

        # add last(first becuse list is reversed)dilution
        count = 0
        p300.pick_up_tip()
        for row in rows[4:7]:
            p300.aspirate(int(vol/2), std_conc[count])
            p300.touch_tip()
            for col in cols[int(rxn_coeff/2):int(rxn_coeff)]:
                p300.move_to(holder_1[row + str(col)].bottom(40))
                p300.dispense(20, holder_1[row + str(col)].bottom(6), rate=0.75)
                p300.touch_tip()
                p300.move_to(holder_1[row + str(col)].top())
            # p300.dispense(int((rxn_coeff * 20)/10) , std_conc[count].bottom(5))
            # p300.blow_out(waste.bottom(5))
            p300.touch_tip()
        p300.drop_tip()

        # add dil to top half of rows
        count = 1 # keep track of standard 
        for row in rows[:4]:
            p300.pick_up_tip()
            p300.aspirate(vol, std_conc[count])
            p300.touch_tip()
            for col in cols[:rxn_coeff]:
                p300.move_to(holder_1[row + str(col)].bottom(40))
                p300.dispense(20, holder_1[row + str(col)].bottom(6), rate=0.75)
                p300.touch_tip()
                p300.move_to(holder_1[row + str(col)].top())
            # p300.dispense(20, waste.bottom(5))
            #p300.blow_out(waste.bottom(5))
            p300.drop_tip()
            count += 1 

        # add dil to bottom half of rows
        count = 1
        for row in rows[4:]:
            p300.pick_up_tip()
            p300.aspirate(int(vol/2), std_conc[count])
            p300.touch_tip()
            for col in cols[:int(rxn_coeff/2)]:
                p300.move_to(holder_1[row + str(col)].bottom(40))
                p300.dispense(20, holder_1[row + str(col)].bottom(6), rate=0.75)
                p300.touch_tip()
                p300.move_to(holder_1[row + str(col)].top())
            # p300.dispense(20, waste.bottom(5))
            #p300.blow_out(waste.bottom(5))
            p300.drop_tip()
            count += 1 
        
        # repeat for holder 2 
        rxn_num = reaction_number - 48
        rxn_coeff = int(rxn_num/8)
        vol = (rxn_coeff * 20) + ((rxn_coeff * 20)/5) 
        # add water to bottom right
        p300.pick_up_tip()
        for row in rows[7:]:
            p300.aspirate(int(vol/2), water.bottom(waterH[5*i+h]))
            p300.touch_tip()
            for col in cols[int(rxn_coeff/2):int(rxn_coeff)]:
                p300.move_to(holder_2[row + str(col)].bottom(40))
                p300.dispense(20, holder_2[row + str(col)].bottom(6), rate=0.75)
                p300.touch_tip()
                p300.move_to(holder_2[row + str(col)].top())
            # p300.dispense(int((rxn_coeff * 20)/10) , std_conc[count].bottom(5))
            # p300.blow_out(waste.bottom(5))
        p300.drop_tip()

        # add last(first becuse list is reversed)dilution
        count = 0
        p300.pick_up_tip()
        for row in rows[4:7]:
            p300.aspirate(int(vol/2), std_conc[count])
            p300.touch_tip()
            for col in cols[int(rxn_coeff/2):int(rxn_coeff)]:
                p300.move_to(holder_2[row + str(col)].bottom(40))
                p300.dispense(20, holder_2[row + str(col)].bottom(6), rate=0.75)
                p300.touch_tip()
                p300.move_to(holder_2[row + str(col)].top())
            # p300.dispense(int((rxn_coeff * 20)/10) , std_conc[count].bottom(5))
            # p300.blow_out(waste.bottom(5))
            p300.touch_tip()
        p300.drop_tip()

        # add dil to top half of rows
        count = 1 # keep track of standard 
        for row in rows[:4]:
            p300.pick_up_tip()
            p300.aspirate(vol, std_conc[count])
            p300.touch_tip()
            for col in cols[:rxn_coeff]:
                p300.move_to(holder_2[row + str(col)].bottom(40))
                p300.dispense(20, holder_2[row + str(col)].bottom(6), rate=0.75)
                p300.touch_tip()
                p300.move_to(holder_2[row + str(col)].top())
            # p300.dispense(20, waste.bottom(5))
            #p300.blow_out(waste.bottom(5))
            p300.drop_tip()
            count += 1 

        # add dil to bottom half of rows
        count = 1
        for row in rows[4:]:
            p300.pick_up_tip()
            p300.aspirate(int(vol/2), std_conc[count])
            p300.touch_tip()
            for col in cols[:int(rxn_coeff/2)]:
                p300.move_to(holder_2[row + str(col)].bottom(40))
                p300.dispense(20, holder_2[row + str(col)].bottom(6), rate=0.75)
                p300.touch_tip()
                p300.move_to(holder_2[row + str(col)].top())
            # p300.dispense(20, waste.bottom(5))
            #p300.blow_out(waste.bottom(5))
            p300.drop_tip()
            count += 1 
    
    
  