# from pylabrobot import liquid_handling
# from pylabrobot.liquid_handling.backends import opentrons_backend
# from pylabrobot.liquid_handling.resources.opentrons import OTDeck
import ot_api

# ot = opentrons_backend(host="169.254.66.13", port=31950)
ot_api.set_host("169.254.66.13") # find in OT app
ot_api.set_port(31950)     # default, so not really necessary

print ("Hello World")
# Creating a run
run_id = ot_api.runs.create()
ot_api.set_run(run_id) # set run globally, alternative to `run_id` parameter for functions

# # Add pipettes that are detected in hardware to the software
left_pipette, right_pipette = ot_api.lh.add_mounted_pipettes()
left_pipette_id = left_pipette["pipetteId"]
print (left_pipette_id)

# # Defining labware
labware_loc = (r'C:\Users\HarleyKing\AppData\Roaming\Opentrons\labware\bioer_96_wellplate_2200ul.json')
# labware_loc = (r'bioer_96_wellplate_2200ul.json')
labware_def = ot_api.labware.define(labware_loc) # json from opentrons-shared-data

# labware_def = ot_api.labware.define('bioer_96_wellplate_2200ul.json') # json from opentrons-shared-data

# # Adding labware
# labware_id = ot_api.labware.add(labware_def, slot=1)

# # Picking up a tip
# ot_api.lh.pick_up_tip(labware_id=labware_id, well_name="A1", pipette_id=left_pipette_id)

# # Aspirating
# ot_api.lh.aspirate(labware_id=labware_id, well_name="A1", pipette_id=left_pipette_id,
#                    flow_rate=10, volume=10)

# # Dispensing
# ot_api.lh.dispense(labware_id=labware_id, well_name="A1", pipette_id=left_pipette_id,
#                    flow_rate=10, volume=10)

# # Tip drop
# ot_api.lh.drop_tip(labware_id=labware_id, well_name="A1", pipette_id=left_pipette_id)
