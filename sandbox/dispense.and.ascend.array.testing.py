def d_dispense(vol:int, steps:int, height:float):
    # what is the height of total volume?
    lowestHeight = 1 # don't go lower than this
    heightIncrement = (height-lowestHeight)/steps
    heightList = list(range(1,steps))
    heightArray =[1] + [1+x*heightIncrement for x in heightList]
    volArray = [vol/steps]*steps
    return zip(volArray, heightArray)

# d_dispense(200, 20, 12)
for volD, hD in d_dispense(200, 20, 12):
    print (volD, hD)