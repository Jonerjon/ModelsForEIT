import csv
import plotly.graph_objects as go
import pandas as pd
import numpy as numpy

#Key Variables
powerConsumption = 300.4 #per second, we're working as if it was every 10th minute #actually 201.268+27.42
usedPower = 201.268+27.42
powerConsumption = usedPower
bufferLength = 24*50 #in hours
bufferCapacity = 39571.2 * bufferLength/16 #total MW capacity of buffer. 23742720 MW for 18 hours 39571.2 divided by 10 minutes. data is for installed capacity, not utilized
bufferFillingEfficiency = 0.5 #how many % of millpower get turned to buffer, seems to be about 50% for ammonia with electrolysis
bufferUsingEfficiency = 0.6 #how much energy do you need to use in the buffer to gain enough in the fill
bufferCurrentSize = bufferCapacity #
windmillAmount = 33 #33 from excel, 16 for basically covering the minimum (above), 41 for covering the numbers today rounded up for all platforms

windmillMaxCapacity = 15*windmillAmount
MWtoCO2Rate = 0.0625426727765 #how much 1 mw10m co2
print(MWtoCO2Rate)
CarbonTax = 590 #590 nok/meteric ton currently

#comment out below when running with buffers and
#windmillMaxCapacity = 0 #for pure C02
#bufferCurrentSize = 0
#bufferCapacity = 0

#total produksjon tonn co2 gassturbiner:
#179876 oseberg sør
#337380 + 234497 feltsenter
#228,988 MW





print(windmillMaxCapacity)

def CalculateForBuffer(differenceToPower, bufferCurrentSize):
    writeToArray = 0
    writeAccessPower = 0
    if differenceToPower>0:
        if differenceToPower*bufferFillingEfficiency + bufferCurrentSize > bufferCapacity:
            bufferCurrentSize = bufferCapacity
            writeToArray = bufferCapacity - bufferCurrentSize*bufferFillingEfficiency
            writeAccessPower = differenceToPower - (bufferCapacity - bufferCurrentSize)/bufferCurrentSize
            print("ye hallo")
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
df = pd.read_csv('windForOseberg.csv')
print(df)
for row in csvreader:
    windData.append(row[1])
    dates.append(row[2])
#print(windData)
file.close()
windData = pd.array(windData, dtype= float)
dates = pd.array(dates, dtype = 'datetime64')
print(len(windData))
windA = windData[0:51359]
datesA = dates[0:51359]
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
DatesUse = datesA
powerUsage = numpy.full(len(windDataUse), powerConsumption)
currentBufferCurrentSize = numpy.full(len(windDataUse), 0, dtype=numpy.double)
currentBufferPowerOutput = numpy.full(len(windDataUse), 0, dtype=numpy.double)
currentBufferusedEnergy = numpy.full(len(windDataUse), 0, dtype=numpy.double)
excessEnergy = numpy.full(len(windDataUse), 0, dtype=numpy.double)
extraOutput = numpy.full(len(windDataUse), 0)
print("buffersize", bufferCurrentSize , "max ", bufferCapacity)
for i in range(len(windDataUse)):
    bufferCurrentSize, currentBufferPowerOutput[i], excessEnergy[i] = CalculateForBuffer(windDataUse[i]-powerConsumption, bufferCurrentSize)
    currentBufferCurrentSize[i] = bufferCurrentSize
    if currentBufferPowerOutput[i]<0 :
        currentBufferusedEnergy[i] = -currentBufferPowerOutput[i]
    if windDataUse<=powerConsumption and windDataUse[i] < powerConsumption:
        extraOutput[i] = powerConsumption - windDataUse[i] - currentBufferusedEnergy[i]
print(powerUsage)
fig = go.Figure()

fig.add_trace(go.Scatter(x=DatesUse, y=windDataUse, mode='lines',
        name="Wind",
        line=dict(color='rgb(0,0,0)', width=2),
        connectgaps=True,
    ))

fig.add_trace(go.Scatter(x=DatesUse, y=powerUsage, mode='lines',
        name="used_Energy",
        line=dict(color='rgb(0,255,0)', width=2),
        connectgaps=True,
        ))

fig.add_trace(go.Scatter(x=DatesUse, y=currentBufferusedEnergy, mode='lines',
        name="buffer_energy_used",
        line=dict(color='rgb(255,0,0)', width=2),
        connectgaps=True,
        ))

fig.add_trace(go.Scatter(x=DatesUse, y=extraOutput, mode='lines',
        name="extra energy",
        line=dict(color='rgb(0,0,255)', width=2),
        connectgaps=True,
        ))

fig.add_trace(go.Scatter(x=DatesUse, y=excessEnergy, mode='lines',
        name="excess energy (wasted)",
        line=dict(color='rgb(255,0,255)', width=2),
        connectgaps=True,
        ))


fig.show()

fig2 = go.Figure()

fig2.add_trace(go.Scatter(x=DatesUse, y=currentBufferCurrentSize, mode='lines',
        name="extra energy",
        line=dict(color='rgb(0,0,255)', width=2),
        connectgaps=True,
        ))
fig2.show()
longestCounter = 0
counter = 0
lastWasZero = False
totalEmptyTime = 0
totalCo2Output = 0
totalExcess = 0
for i in range(len(windDataUse)):
    totalExcess += excessEnergy[i]
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
print(longestCounter)
print("longest time with burning gas in hours:", longestCounter/(6))
print("longest time with burning in days:", longestCounter/(6*24))
print(totalEmptyTime)
print("total time with burning gas in hours:", totalEmptyTime/(6))
print("total time with burning ga in days:", totalEmptyTime/(6*24))
print("total tonns CO2 released:", totalCo2Output)
print("price of CO2 released", totalCo2Output*CarbonTax, "NOK")
print("total amount of wasted (excess) energy", totalExcess, "MW10M")
