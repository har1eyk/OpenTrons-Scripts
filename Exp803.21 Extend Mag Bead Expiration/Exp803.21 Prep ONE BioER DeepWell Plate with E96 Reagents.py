# imports
from opentrons import protocol_api
from opentrons.commands.commands import blow_out
import tkinter as tk
from tkinter import simpledialog

# metadata
metadata = {
    'protocolName': 'Prep BioER Deepwell Plate with LysisBuffer, LS1A and IsoPropanol.',
    'author': 'Harley King <harley.king@luminultra.com>',
    'description': 'Making a BioER plate with LB/BB, LS1a and isopropanol.',
    'apiLevel': '2.13'
}

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
    # mag_rack = protocol.load_labware(
    #     'opentrons_24_tuberack_eppendorf_2ml_safelock_snapcap', '11')
    tiprack300 = protocol.load_labware('opentrons_96_filtertiprack_200ul', '8')
    # tempdeck = protocol.load_module('tempdeck', '10')
    deep_plate1 = protocol.load_labware('bioer_96_wellplate_2200ul', '1')
    # deep_plate2 = protocol.load_labware('bioer_96_wellplate_2200ul', '4')
    reagent_rack = protocol.load_labware(
        'opentrons_6_tuberack_nest_50ml_conical', '2')

    # PIPETTES
    p300 = protocol.load_instrument(
        'p300_single_gen2', 'left', tip_racks=[tiprack300]
    )
    # REAGENTS
    alcohol = reagent_rack['A1'] 
    lysis_buffer = reagent_rack['A2']  
    water = reagent_rack['A3']

    # CALCS
    alcohol_per_well = 400
    lysis_buffer_per_well = 400
    water_per_well = 300

    alcohol_volume = 42000
    lysis_buffer_volume = 42000
    water_volume = 42000

    # LISTS
    tot_sample_plates = [deep_plate1]
    rows_on_plate = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']

    # ##### COMMANDS ######
    p300.pick_up_tip()
    alcoholHList=fifty_ml_heights(alcohol_volume, 97, 400) # this returns a list of heights
    # print ("the height list is ", alcoholHList)
    # dispense 200ul into every well of deepwell plate
    for plate in tot_sample_plates:
        for row in range(8):
            for col in range(1, 13):
                dest = plate[rows_on_plate[row] + str(col)]
                vol = alcohol_per_well/2
                for r in range(2):
                    h=alcoholHList[col+12*row]
                    p300.aspirate(vol, alcohol.bottom(h))
                    p300.dispense(vol, dest.bottom(2))
                    p300.blow_out()
    p300.drop_tip()

    p300.pick_up_tip()
    lysisHList=fifty_ml_heights(lysis_buffer_volume, 97, 400) # this returns a list of heights
    # dispense 200ul into every well of deepwell plate
    for plate in tot_sample_plates:
        for row in range(8):
            for col in range(1, 13):
                dest = plate[rows_on_plate[row] + str(col)]
                vol = lysis_buffer_per_well/2
                for r in range(2):
                    h=lysisHList[col+12*row]
                    p300.aspirate(vol, lysis_buffer.bottom(h))
                    p300.dispense(vol, dest.bottom(2))
                    p300.blow_out()
    p300.drop_tip()

    p300.pick_up_tip()
    waterHList=fifty_ml_heights(water_volume, 97, 400) # this returns a list of heights
    # dispense 200ul into every well of deepwell plate
    for plate in tot_sample_plates:
        for row in range(8):
            for col in range(1, 13):
                dest = plate[rows_on_plate[row] + str(col)]
                vol = water_per_well/2
                for r in range(2):
                    h=waterHList[col+12*row]
                    p300.aspirate(vol, water.bottom(h))
                    p300.dispense(vol, dest.bottom(2))
                    p300.blow_out()
    p300.drop_tip()

 
