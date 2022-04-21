# imports
from opentrons import protocol_api

# metadata
metadata = {
    'protocolName': 'Transfer 20ul Sample from 96w Plate to 96 Lyophilized Tubes',
    'author': 'Harley King <harley.king@luminultra.com>',
    'description': 'Add DNA samples from 96w Plate to lyophilized 8-well strip tubes. Tubes are held by 200 filter tip racks.',
    'apiLevel': '2.11'
}

# def which_holder (plate, samp, dest):

##########################

def run(protocol: protocol_api.ProtocolContext):

    # LABWARE
    tiprack300 = protocol.load_labware('opentrons_96_filtertiprack_200ul', '8')
    tiprack20 = protocol.load_labware('opentrons_96_filtertiprack_20ul', '9')
    tempdeck = protocol.load_module('tempdeck', '4') #keep this on so I don't have to move it off and on
    holder_1 = protocol.load_labware('8wstriptubesonfilterracks_96_aluminumblock_250ul', '3')
    holder_2 = protocol.load_labware('8wstriptubesonfilterracks_96_aluminumblock_250ul', '6')
    sample_plate = protocol.load_labware('bioer_96_wellplate_2200ul', '2')
    # PIPETTES
    p300 = protocol.load_instrument(
        'p300_single_gen2', 'left', tip_racks=[tiprack300]
    )
    p20 = protocol.load_instrument(
        'p20_single_gen2', 'right', tip_racks=[tiprack20]
    )
  
    # user inputs
    holderList = [holder_1, holder_2]
    rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
    
    # #### COMMANDS ######    
    # Transfer 20ul from 96w plate to 96 lyophilized tubes
    for row in rows:
        p20.pick_up_tip()
        for i in range(12):
            j = 0 if i < 6 else 1 # need to move to next holder when columns >6
            source = sample_plate[row+str(i+1)]
            dest = holderList[j][row + str(2*i+1)]
            p20.aspirate(20, source.bottom(1), rate=0.75)
            p20.move_to(source.bottom(40)) #move p20 pipette +4cm so no crash into lyo tubes
            p20.move_to(dest.bottom(40)) #move p20 pipette +4cm so no crash into lyo tubes
            p20.dispense(20, dest.bottom(6))
            p20.blow_out()
            p20.touch_tip()
            p20.move_to(dest.top()) # centers tip so tip doesn't lift tubes after touch
            p20.move_to(dest.bottom(40))
        p20.drop_tip()