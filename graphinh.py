import csv
import plotly.graph_objects as go
import pandas as pd
import numpy as numpy

#Key Variables
powerConsumption = 300.4 #per second, we're working as if it was every 10th minute #actually 201.268+27.72
usedPower = 201.268+27.72
powerConsumption = usedPower
bufferLength = 24*0 +0 #in hours 24*48 + 9 4*33 + 15 for new 45 windmills 24*4 + 7 25: 3 + 18
bufferCapacity = 1373.928 * bufferLength #total MW capacity of buffer. 23742720 MW for 18 hours 39571.2 divided by 10 minutes. data is for installed capacity, not utilized
#14818982.4 for 18 hours with actual usedPower, which is 823276.8 for 1 hours. for this task 24698.304 for 18, 1372.128 for 1 hours
bufferFillingEfficiency = 0.5 #how many % of millpower get turned to buffer, seems to be about 50% for ammonia with electrolysis
bufferUsingEfficiency = 0.6 #how much energy do you need to use in the buffer to gain enough in the fill 0.6
bufferCurrentSize = bufferCapacity #
windmillAmount = 25 #33 from excel, 16 for basically covering the minimum (above), 41 for covering the numbers today rounded up for all platforms, actually 45 based on model 39

windmillMaxCapacity = 15*windmillAmount
#windmillMaxCapacity = 0
#windmillMaxCapacity = usedPower
#bufferCapacity = 0
MWtoCO2Rate = 0.0651977072657 #how much 1 mw10m co2 0.06254267277645784 0.0625426727765 0.0637079346929

print(MWtoCO2Rate)
CarbonTax = 1812.43 #590 nok/meteric ton currently, 632 after update
defaultCarbon = 766763.81

#comment out below when running with buffers and
#windmillMaxCapacity = 0 #for pure C02
#bufferCurrentSize = 0
#bufferCapacity = 0

#total produksjon tonn co2 gassturbiner:
#179876 oseberg sør
#337380 + 234497 feltsenter
#228,988 MW
co2aa = 337380 + 234497 + 179876
MWs = usedPower*6*24*365 #51359 actual, 52560 calculated
print(co2aa/MWs, " Megawatts: ", MWs)





print(windmillMaxCapacity)

def CalculateForBuffer(differenceToPower, bufferCurrentSize):
    writeToArray = 0
    writeAccessPower = 0
    if differenceToPower>0:
        if differenceToPower*bufferFillingEfficiency + bufferCurrentSize > bufferCapacity:
            bufferCurrentSize = bufferCapacity
            writeToArray = bufferCapacity - bufferCurrentSize*bufferFillingEfficiency
            if bufferCurrentSize == 0:
                writeAccessPower = differenceToPower
            else:
                writeAccessPower = differenceToPower - (bufferCapacity - bufferCurrentSize)/bufferCurrentSize
            #print("ye hallo")
        else:
            bufferCurrentSize += differenceToPower*bufferFillingEfficiency
            writeToArray = differenceToPower*bufferFillingEfficiency
    else:
        if (differenceToPower + bufferCurrentSize*bufferUsingEfficiency) < 0:
            writeToArray = bufferCurrentSize*bufferUsingEfficiency
            bufferCurrentSize = 0
            #writeAccessPower = differenceToPower -
        else:
            bufferCurrentSize += differenceToPower/bufferUsingEfficiency
            writeToArray = differenceToPower
    return bufferCurrentSize, writeToArray, writeAccessPower






file = open("windForOseberg.csv")
csvreader = csv.reader(file)
header = next(csvreader)
print(header)
windData = []
dates = []
actualWindSpeeds = []
windData25 = []
df = pd.read_csv('windForOseberg.csv')
print(df)
for row in csvreader:
    windData.append(row[1])
    dates.append(row[2])
    actualWindSpeeds.append(row[3])
    windData25.append(row[5])
#print(windData)
file.close()
windData = pd.array(windData, dtype= float)
windData25 = pd.array(windData25, dtype= float)
dates = pd.array(dates, dtype = 'datetime64')
actualWindSpeeds = pd.array(actualWindSpeeds, dtype= float)
print(len(windData))
windA = windData[0:51359]
datesA = dates[0:51359]
windSpeedA = actualWindSpeeds[0:51359]
wind25A = windData25[0:51359]
print(numpy.mean(windA)) #averages provide the exact lower value for where the wind provides enough energy for one year
windC = windData[51359:103366]
datesC = dates[51359:103366]
print(numpy.mean(windC))
windSor = windData[103366:] #corrected for the various positions, tested to be correct
datesSor = dates[103366:]
print(numpy.mean(windSor))
#windData = windData.apply(pd.to_numeric)
tempWind = windData[:1000]
tempDate = dates[:1000]
pickWind = windData[0::500]
pickDate = dates[0::500]
longestZero = 0
counter = 0
for number in windSor: #longest for windA with all zeroes is a little bit more than 24 hours
    if number == 0:
        counter += 1
    else:
        counter = 0
    if longestZero<counter:
        longestZero = counter
print("longest zero", longestZero)

windDataUse = windA*windmillMaxCapacity
windSpeedUse = windSpeedA
DatesUse = datesA
powerUsage = numpy.full(len(windDataUse), powerConsumption)
currentBufferCurrentSize = numpy.full(len(windDataUse), 0, dtype=numpy.double)
currentBufferPowerOutput = numpy.full(len(windDataUse), 0, dtype=numpy.double)
currentBufferusedEnergy = numpy.full(len(windDataUse), 0, dtype=numpy.double)
excessEnergy = numpy.full(len(windDataUse), 0, dtype=numpy.double)
extraOutput = numpy.full(len(windDataUse), 0)
print("buffersize", bufferCurrentSize , "max ", bufferCapacity)
totalWastedEnergy = numpy.full(len(windDataUse), 0, dtype=numpy.double)
averageOutput = 0
counterRefill = 0
landPowerIn = numpy.full(len(windDataUse), 0, dtype=numpy.double)
cableLimit = 150
for i in range(len(windDataUse)):
    bufferCurrentSize, currentBufferPowerOutput[i], excessEnergy[i] = CalculateForBuffer(windDataUse[i]-powerConsumption, bufferCurrentSize)

    if counterRefill >= 6*24*7:
        #bufferCurrentSize = bufferCapacity
        counterRefill = 0
    else:
        counterRefill = counterRefill + 1
    currentBufferCurrentSize[i] = bufferCurrentSize
    averageOutput += windDataUse[i]
    if currentBufferPowerOutput[i]<0 :
        currentBufferusedEnergy[i] = -currentBufferPowerOutput[i]
    if windDataUse<=powerConsumption and windDataUse[i] < powerConsumption:
        extraOutput[i] = powerConsumption - windDataUse[i] - currentBufferusedEnergy[i]
        if extraOutput[i] > cableLimit:
            extraOutput[i] = extraOutput[i] - cableLimit
            landPowerIn[i] = cableLimit
        else:
            landPowerIn[i] = extraOutput[i]
            extraOutput[i] = 0
print(powerUsage)
averageOutput = averageOutput/len(windDataUse)
print("average output ", averageOutput)
fig = go.Figure()
timeUse = len(windDataUse) #6*24*7
windDataUse = windDataUse[0:timeUse]
currentBufferusedEnergy = currentBufferusedEnergy[0:timeUse]
extraOutput = extraOutput[0:timeUse]
excessEnergy = excessEnergy[0:timeUse]
DatesUse = DatesUse[0:timeUse]
fig.add_trace(go.Scatter(x=DatesUse, y=windDataUse, mode='lines',
        name="Windmill effect output",
        line=dict(color='rgb(0,0,0)', width=2),
        connectgaps=True,
    ))

#fig.add_trace(go.Scatter(x=DatesUse, y=currentBufferusedEnergy, mode='lines',
#        name="Buffer effect output",
#        line=dict(color='rgb(255,0,0)', width=2),
#        connectgaps=True,
#        ))

fig.add_trace(go.Scatter(x=DatesUse, y=landPowerIn, mode='lines',
        name="Land Power used",
        line=dict(color='rgb(255,0,0)', width=2),
        connectgaps=True,
        ))

fig.add_trace(go.Scatter(x=DatesUse, y=extraOutput, mode='lines',
        name="Gas turbine effect output",
        line=dict(color='rgb(0,0,255)', width=2),
        connectgaps=True,
        ))

fig.add_trace(go.Scatter(x=DatesUse, y=excessEnergy, mode='lines',
        name="Excess windmill effect (wasted)",
        line=dict(color='rgb(255,0,255)', width=2),
        connectgaps=True,
        ))


fig.show()


longestCounter = 0
counter = 0
lastWasZero = False
totalEmptyTime = 0
totalCo2Output = 0
totalExcess = 0

for i in range(len(windDataUse)):
    totalExcess += excessEnergy[i]
    totalWastedEnergy[i] = totalExcess
    if currentBufferCurrentSize[i] == 0 and windDataUse[i] < powerConsumption:
        totalEmptyTime = totalEmptyTime + 1
        totalCo2Output = totalCo2Output + (extraOutput[i] * MWtoCO2Rate)
        if lastWasZero:
            counter = counter +1
            if counter > longestCounter:
                longestCounter = counter
        lastWasZero = True
    else:
        lastWasZero = False
        counter = 0

fig2 = go.Figure()

fig2.add_trace(go.Scatter(x=DatesUse, y=currentBufferCurrentSize, mode='lines',
        name="Buffer avaliable effect",
        line=dict(color='rgb(0,0,255)', width=2),
        connectgaps=True,
        ))
#fig2.add_trace(go.Scatter(x=DatesUse, y=totalWastedEnergy, mode='lines',
#        name="Accumulated effect overproduced (wasted)",
#        line=dict(color='rgb(0,255,0)', width=2),
#        connectgaps=True,
#        ))

fig2.add_trace(go.Scatter(x=DatesUse, y=totalWastedEnergy, mode='lines',
        name="Energy sent to land",
        line=dict(color='rgb(0,255,0)', width=2),
        connectgaps=True,
        ))
fig2.show()
print(longestCounter)
print("longest time with burning gas in hours:", longestCounter/(6))
print("longest time with burning in days:", longestCounter/(6*24))
print(totalEmptyTime)
print("total time with burning gas in hours:", totalEmptyTime/(6))
print("total time with burning ga in days:", totalEmptyTime/(6*24))
print("total tonns CO2 released:", totalCo2Output)
print("price of CO2 released", totalCo2Output*CarbonTax, "NOK")
print("total amount of wasted (excess) energy", totalExcess, "MW10M")
print("percentage of original C02 released", totalCo2Output*100/defaultCarbon, "%")

MW_size = bufferCapacity/(6)
print("MWh buffer", MW_size)
