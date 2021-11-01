# imports



def fifty_ml_heights(init_vol, steps, vol_dec):
    vols = []
    heights = []
    # these values originate from Excel spreadsheet "Exp803..."
    print (init_vol)
    b = 0
    m = 0.0024
    if init_vol > 51000:
        offset = 14  # model out of range; see sheet
    else:
        offset = 7  # mm Need to add offset to ensure tip reaches below liquid level
    print (offset)
    for i in range(steps):
        x = init_vol-vol_dec*i
        vols.append(x)
        h = m*x+b
        h = h-offset
        # print (h)
        if h < 12:  # If less than 5mL remain in 50mL tube, go to bottom for asp
            h = 2
            heights.append(h)
        else:
            heights.append(round(h, 1))
    return heights

##########################

# ##### COMMANDS #####
fifty_h=fifty_ml_heights(32400, 100, 200)
print(fifty_h)
