# imports
from opentrons import protocol_api
from opentrons.commands.commands import blow_out
import tkinter as tk
from tkinter import simpledialog

# metadata
metadata = {
    'protocolName': 'Prep BioER Deepwell Plate with E32 Extraction Reagents.',
    'author': 'Harley King <harley.king@luminultra.com>',
    'description': 'Making a BioER plate with beads, lysis buffer, wash1-3 and NFW.',
    'apiLevel': '2.11'
}


def tip_heights(init_vol, steps, vol_dec):
    vols = []
    heights = []
    # these values originate from Excel spreadsheet "Exp803..."
    p0 = 0.029502064
    p1 = 0.084625954
    p2 = -0.000174864
    p3 = 2.18373E-07
    p4 = -1.30599E-10
    p5 = 2.97839E-14
    if init_vol > 1499:
        offset = 14  # model out of range; see sheet
    else:
        offset = 7  # mm Need to add offset to ensure tip reaches below liquid level
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

def fifty_ml_heights(init_vol, steps, vol_dec):
    vols = []
    heights = []
    # these values originate from Excel spreadsheet "Exp803..."
    b = 7.5
    m = 0.002
    if init_vol > 51000:
        offset = 14  # model out of range; see sheet
    else:
        offset = 7  # mm Need to add offset to ensure tip reaches below liquid level
    for i in range(steps):
        x = init_vol-vol_dec*i
        vols.append(x)
        h = m*x*+b
        h = h-offset
        if h < 17.5:  # If less than 5mL remain in 50mL tube, go to bottom for asp
            h = 2
            heights.append(h)
        else:
            heights.append(round(h, 1))
    return heights

##########################


def run(protocol: protocol_api.ProtocolContext):

    # LABWARE
    mag_rack = protocol.load_labware(
        'opentrons_24_tuberack_eppendorf_2ml_safelock_snapcap', '11')
    tiprack300 = protocol.load_labware('opentrons_96_filtertiprack_200ul', '8')
    tempdeck = protocol.load_module('tempdeck', '10')
    deep_plate1 = protocol.load_labware('bioer_96_wellplate_2200ul', '1')
    deep_plate2 = protocol.load_labware('bioer_96_wellplate_2200ul', '4')
    reagent_rack = protocol.load_labware(
        'opentrons_6_tuberack_nest_50ml_conical', '2')

    # PIPETTES
    p300 = protocol.load_instrument(
        'p300_single_gen2', 'left', tip_racks=[tiprack300]
    )
    # REAGENTS
    # the magnetic beads are undiluted in 2mL Epp snap-cap tube
    # 50mL | 40 *16 = 640*1.2 = 768 | undiluted beads
    mag_beads = mag_rack['B3']
    # These are on 6-well, 50mL rack
    lysis_buffer = reagent_rack['A1']  # 50mL 400 * 16 =6400*1.2 = 7680
    # 50mL | 100*16 = 1600*1.2 = 1920 + dilution for beads = 360*16 =5760*1.2=6912 = 8832
    nfw = reagent_rack['A3']
    wash_sol_one = reagent_rack['B1']  # 50mL | 1000 *16 = 16000*1.2 = 19200
    wash_sol_two = reagent_rack['B2']  # 50mL | 1000 *16 = 16000*1.2 = 19200
    # 50mL | 1000 *16 = 16000*1.2 = 19200
    wash_sol_three_etoh = reagent_rack['B3']

    # CALCS
    lysis_buffer_per_well = 400
    mag_beads_per_well = 40
    water_for_mag_bead_dil_per_well = 360
    wash_one_sol_per_well = 1000
    wash_two_sol_per_well = 1000
    wash_three_etoh_per_well = 1000
    elution_buffer_per_well = 100
    # COLUMNS
    mag_bead_columns = ['6', '12']
    lysis_buffer_columns = ['1', '7']
    elution_columns = ['5', '11']
    wash_one_sol_columns = ['2', '8']
    wash_two_sol_columns = ['3', '9']
    wash_three_etoh_columns = ['4', '10']

    # LISTS
    tot_sample_plates = [deep_plate1]
    rows_on_plate = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']

    ##### USER PROMPTS #####
    # # ROOT = tk.Tk()
    # # ROOT.withdraw()
    # # # the input dialog
    # # beadVolInput = simpledialog.askstring(
    # #     title="ConfirmBeads", prompt="For 1 plate (8 wells) there should be 8*40*1.1 = 352ul undiluted beads. How many microliters are in the 1.5mL tube?:")
    # # check it out
    # # print("Hello", USER_INP)

    # ##### COMMANDS ######



    fifty_h=fifty_ml_heights(32.4, 100, 200)
    p300.pick_up_tip()
    p300.aspirate(200, reagent_rack['A1'].bottom(fifty_h))
    p300.dispense(200, 'trash')
    # # magnetic beads transfer
    # # the beads should not be diluted!
    # p300.pick_up_tip()
    # # print ("Bead Input Volume:", beadVolInput)
    # mag_h = tip_heights(352, 8, 40)  # 16*40 *1.1 = 704ul
    # print (mag_h)
    
    # counter = 0
    # print (counter)

    # for plate in tot_sample_plates:
    #     p300.mix(2, 200, mag_beads.bottom(4))
    #     p300.mix(2, 200, mag_beads.bottom(8))
    #     p300.mix(4, 200, mag_beads.bottom(12))
    #     for col in mag_bead_columns:
    #         for row in rows_on_plate:
    #             p300.mix(1, 200, mag_beads.bottom(2))
    #             p300.mix(1, 200, mag_beads.bottom(4))
    #             dest = row+str(col)
    #             p300.aspirate(mag_beads_per_well, mag_beads.bottom(
    #                 mag_h[counter]), rate=0.5)
    #             p300.touch_tip(v_offset=-4) # remove bead droplets on tip outside
    #             p300.dispense(mag_beads_per_well, plate[dest].bottom(2))
    #             p300.blow_out(plate[dest].bottom(10))
    #             p300.touch_tip()
    #             counter += 1
    #             print (counter)
    # p300.drop_tip()
    # # dilute the mag beads 1:10 with water
    # p300.pick_up_tip()
    # for plate in tot_sample_plates:
    #     for col in mag_bead_columns:
    #         for row in rows_on_plate:
    #             dest = row+str(col)
    #             p300.aspirate(water_for_mag_bead_dil_per_well/2, nfw)
    #             p300.dispense(water_for_mag_bead_dil_per_well /
    #                           2, plate[dest].bottom(25))
    #             p300.aspirate(water_for_mag_bead_dil_per_well/2, nfw)
    #             p300.dispense(water_for_mag_bead_dil_per_well /
    #                           2, plate[dest].bottom(25))
    #             p300.blow_out(plate[dest].bottom(25))
    #             p300.touch_tip()
    # p300.drop_tip()

    # # lysis buffer
    # p300.pick_up_tip()
    # for plate in tot_sample_plates:
    #     for col in lysis_buffer_columns:
    #         for row in rows_on_plate:
    #             dest = row+str(col)
    #             p300.aspirate(lysis_buffer_per_well/2, lysis_buffer, rate=0.75)
    #             p300.dispense(lysis_buffer_per_well/2, plate[dest].bottom(10))
    #             p300.blow_out(plate[dest].bottom(20))
    #             p300.aspirate(lysis_buffer_per_well/2, lysis_buffer, rate=0.75)
    #             p300.dispense(lysis_buffer_per_well/2, plate[dest].bottom(15))
    #             p300.blow_out(plate[dest].bottom(20))
    #             p300.touch_tip()
    # p300.drop_tip()

    # # wash buffer 1
    # p300.pick_up_tip()
    # for plate in tot_sample_plates:
    #     for col in wash_one_sol_columns:
    #         for row in rows_on_plate:
    #             dest = row+str(col)
    #             for i in range(5):
    #                 p300.aspirate(wash_one_sol_per_well/5, wash_sol_one)
    #                 p300.dispense(wash_one_sol_per_well/5,
    #                               plate[dest].bottom(25))
    #                 p300.blow_out(plate[dest].bottom(25))
    #                 p300.touch_tip()
    # p300.drop_tip()

    # # wash buffer 2
    # p300.pick_up_tip()
    # for plate in tot_sample_plates:
    #     for col in wash_two_sol_columns:
    #         for row in rows_on_plate:
    #             dest = row+str(col)
    #             for i in range(5):
    #                 p300.aspirate(wash_two_sol_per_well/5, wash_sol_two)
    #                 p300.dispense(wash_two_sol_per_well/5,
    #                               plate[dest].bottom(25))
    #                 p300.blow_out(plate[dest].bottom(25))
    #                 p300.touch_tip()
    # p300.drop_tip()

    # # wash buffer 3
    # p300.pick_up_tip()
    # for plate in tot_sample_plates:
    #     for col in wash_three_etoh_columns:
    #         for row in rows_on_plate:
    #             dest = row+str(col)
    #             for i in range(5):
    #                 p300.aspirate(wash_three_etoh_per_well /
    #                               5, wash_sol_three_etoh)
    #                 p300.dispense(wash_three_etoh_per_well /
    #                               5, plate[dest].bottom(25))
    #                 p300.blow_out(plate[dest].bottom(25))
    #                 p300.touch_tip()
    # p300.drop_tip()

    # # elution buffer (NFW)
    # # pipette this solution last to avoid evaporative losses
    # p300.pick_up_tip()
    # for plate in tot_sample_plates:
    #     for col in elution_columns:
    #         for row in rows_on_plate:
    #             dest = row+str(col)
    #             p300.aspirate(elution_buffer_per_well, nfw)
    #             p300.dispense(elution_buffer_per_well, plate[dest].bottom(20))
    #             p300.touch_tip()
    # p300.drop_tip()
