# imports
from opentrons import labware, instruments

# metadata
metadata = {
    'protocolName': 'Setting up PCR Reaction for BSCI:414 students',
    'author': 'Harley King <harley@umd.edu>',
    'description': 'Students specify a sets of primers for a list of six, OpenTrons does the pipetting.',
}
##########################

# Labware
fuge_rack = labware.load('opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap', '1')
pcr_plate = labware.load('biorad_96_wellplate_200ul_pcr', '2')
# tips
tiprack_300 = labware.load('opentrons_96_tiprack_300ul', '4')
tiprack_10 = labware.load('opentrons_96_tiprack_10ul', '5') #has slot adapter
##########################

# initialize single channel, 1st gen pipetters 
p300 = instruments.P300_Single(
    mount='right',
    tip_racks=[tiprack_300])

p10 = instruments.P10_Single(
    mount='left',
    tip_racks=[tiprack_10])
###########################

# Setup Overview
# 1) Pipette PCR MMix from fuge_rack A1 to PCR plate
# 2) Distribute primers into wells 
##########################

F_primer = [
'F20_Bam-sfGFP',
'F20_Bam-sfGFP',
'F20_Bam-sfGFP',
'F20_Bam-sfGFP',
'F20_Bam-sfGFP',
'F20_Bam-sfGFP',
'F20_Bam-sfGFP',
'F20_Bam-sfGFP',
'F20_Bam-sfGFP',
'F20_Bam-sfGFP',
'F20_Bam-sfGFP',
'F20_Bam-sfGFP',
'F20_Bam-sfGFP',
'F20_Bam-sfGFP',
'F20_Bam-sfGFP',
'F20_Bam-sfGFP',
'F20_Bam-sfGFP',
'F20_Bam-sfGFP',
'F20_Bam-sfGFP',
'F20_Bam-sfGFP',
'F20_Bam-sfGFP',
'F20_Bam-sfGFP',
'F20_Bam-sfGFP',
'F20_MA_sfGFP1',
'F20_MA_sfGFP1',
'F20_MA_sfGFP1',
'F20_MA_sfGFP1',
'F20_MA_sfGFP1',
'F20_MA_sfGFP1',
'F20_MA_sfGFP1',
'F20_MA_sfGFP1',
'F20_MA_sfGFP1',
'F20_MA_sfGFP1',
'F20_MA_sfGFP1',
'F20_sfGFP.seq',
'F20_sfGFP.seq',
'F20_sfGFP.seq',
'F20_sfGFP.seq',
'F20_sfGFP.seq',
'F20_sfGFP.seq',
'F20_sfGFP.seq',
'F20_sfGFP.seq',
'F20_sfGFP.seq',
'F20_Bam-sfGFP',
'F20_sfGFP.seq'
]


R_primer = [
'F20_HA_sfGFP2',
'F20_HA_sfGFP2',
'F20_M13AR',
'F20_M13AR',
'F20_TEV-sfGFP_ns',
'F20_M13AR',
'F20_TEV-sfGFP_ns',
'F20_M13AR',
'F20_M13AR',
'F20_TEV-sfGFP_ns',
'F20_TEV-sfGFP_ns',
'F20_TEV-sfGFP_ns',
'F20_TEV-sfGFP_ns',
'F20_TEV-sfGFP_ns',
'F20_TEV-sfGFP_ns',
'F20_TEV-sfGFP_ns',
'F20_HA_sfGFP2',
'F20_M13AR',
'F20_HA_sfGFP2',
'F20_M13AR',
'F20_M13AR',
'F20_M13AR',
'F20_TEV-sfGFP_ns',
'F20_M13AR',
'F20_HA_sfGFP2',
'F20_TEV-sfGFP_ns',
'F20_M13AR',
'F20_HA_sfGFP2',
'F20_M13AR',
'F20_M13AR',
'F20_M13AR',
'F20_M13AR',
'F20_HA_sfGFP2',
'F20_HA_sfGFP2',
'F20_HA_sfGFP2',
'F20_M13AR',
'F20_TEV-sfGFP_ns',
'F20_M13AR',
'F20_HA_sfGFP2',
'F20_TEV-sfGFP_ns',
'F20_TEV-sfGFP_ns',
'F20_TEV-sfGFP_ns',
'F20_HA_sfGFP2',
'F20_M13AR',
'F20_HA_sfGFP2'
]

position = [
'A1',
'B1',
'C1',
'D1',
'E1',
'F1',
'G1',
'H1',
'A2',
'B2',
'C2',
'D2',
'E2',
'F2',
'G2',
'H2',
'A3',
'B3',
'C3',
'D3',
'E3',
'F3',
'G3',
'H3',
'A4',
'B4',
'C4',
'D4',
'E4',
'F4',
'G4',
'H4',
'A5',
'B5',
'C5',
'D5',
'E5',
'F5',
'G5',
'H5',
'A6',
'B6',
'C6',
'D6',
'E6'
]

print ("There are ", len(F_primer), " F primer and ", len(R_primer), " R primers.")

unique_F_primers = set(F_primer)
unique_R_primers = set(R_primer)
print ("Unique F primers: ", unique_F_primers)
print ("Unique R primers: ", unique_R_primers)

primer_locs = {
'F20_Bam-sfGFP': 'A2',
'F20_MA_sfGFP1': 'B2',
'F20_sfGFP.seq': 'C2',
'F20_HA_sfGFP2': 'D2',
'F20_TEV-sfGFP_ns': 'A3',
'F20_M13AR': 'B3'
}

# Procedure
# distribute MMix
p300.distribute(18, fuge_rack('A1'), pcr_plate.cols('1', '2', '3', '4', '5', '6'),
    disposal_vol=2, touch_tip=True, new_tip='always')

# distribute primers
# in which wells should we dispense 1ul F primer F20_Bam-sfGFP?
# find wells filtered where search = F20_BamsfGFP

for fwd in unique_F_primers: 
    print ("Pipetting FWD primer, ", fwd)
    # match this to array of positions e.g [A1, B2, B4]
    myposarray = []
    for pos, match in enumerate(F_primer):
        if fwd == match:
            myposarray.append(position[pos])
    # myposarray = df[df['F_primer']==fwd].Position.tolist() 
    # pipette 1ul at each of those positions
    print ("Will distribute 1 ul from fuge_rack", primer_locs[fwd], "into wells:", myposarray)
    # wellarray = tuple(myposarray)
    p10.distribute(1, fuge_rack(primer_locs[fwd]), pcr_plate.wells(myposarray), new_tip='always', touch_tip=True, disposal_vol=1)
    
for rev in unique_R_primers: 
    print ("Pipetting REV primer, ", rev)
    # match this to array of positions e.g [A1, B2, B4]
    myposarray = []
    for pos, match in enumerate(R_primer):
        if rev == match:
            myposarray.append(position[pos])
    # myposarray = df[df['F_primer']==fwd].Position.tolist() 
    # pipette 1ul at each of those positions
    print ("Will distribute 1 ul from fuge_rack", primer_locs[rev], "into wells:", myposarray)
    # wellarray = tuple(myposarray)
    p10.distribute(1, fuge_rack(primer_locs[rev]), pcr_plate.wells(myposarray), new_tip='always', touch_tip=True, disposal_vol=1)




