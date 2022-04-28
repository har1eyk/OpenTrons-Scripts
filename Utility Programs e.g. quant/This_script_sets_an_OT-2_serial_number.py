# This script sets an OT-2's serial number.  It's meant to be used after you
# replace or reflash an OT-2's SD card.  This script is based on some of the factory
# provisioning scripts.
#
# Change the following to your OT-2's serial number.
# For example, in the script below: NEW_SERIAL_NUMBER = "<your serial number goes here>"


from opentrons import protocol_api
import os
metadata = {"apiLevel": "2.8"}

def run(ctx: protocol_api.ProtocolContext):

    #Please replace what is between the quotation marks!!

    NEW_SERIAL_NUMBER = "set_your_serial_number_here"


    ctx.comment(f"Setting serial number to {NEW_SERIAL_NUMBER}.")

    if not ctx.is_simulating():
        with open("/var/serial", "w") as serial_number_file:
            serial_number_file.write(NEW_SERIAL_NUMBER + "\n")
        with open("/etc/machine-info", "w") as serial_number_file:
            serial_number_file.write(f"DEPLOYMENT=production\nPRETTY_HOSTNAME={NEW_SERIAL_NUMBER}\n")
        with open("/etc/hostname", "w") as serial_number_file:
            serial_number_file.write(NEW_SERIAL_NUMBER + "\n")
        
        os.sync()
        
        
        ctx.comment("Done.")# This script sets an OT-2's serial number.  It's meant to be used after you
# replace or reflash an OT-2's SD card.  This script is based on some of the factory
# provisioning scripts.
#
# Change the following to your OT-2's serial number.
# For example, in the script below: NEW_SERIAL_NUMBER = "<your serial number goes here>"


from opentrons import protocol_api
import os
metadata = {"apiLevel": "2.8"}

def run(ctx: protocol_api.ProtocolContext):

    #Please replace what is between the quotation marks!!

    NEW_SERIAL_NUMBER = "OT2CEP20201214B12"


    ctx.comment(f"Setting serial number to {NEW_SERIAL_NUMBER}.")

    if not ctx.is_simulating():
        with open("/var/serial", "w") as serial_number_file:
            serial_number_file.write(NEW_SERIAL_NUMBER + "\n")
        with open("/etc/machine-info", "w") as serial_number_file:
            serial_number_file.write(f"DEPLOYMENT=production\nPRETTY_HOSTNAME={NEW_SERIAL_NUMBER}\n")
        with open("/etc/hostname", "w") as serial_number_file:
            serial_number_file.write(NEW_SERIAL_NUMBER + "\n")
        
        os.sync()
        
        
        ctx.comment("Done.")