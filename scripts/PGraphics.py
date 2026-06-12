import os

try:
    import numpy as np 
except Exception as exc:
    os.system("pip install numpy")
    import numpy as np

try:
    import matplotlib.pyplot as plt
except Exception as exc2:
    os.system("pip install matplotlib")
    import matplotlib.pyplot as plt

try:
    import serial
    import serial.tools.list_ports
except Exception as exc3:
    os.system("pip install pyserial")
    import serial
    import serial.tools.list_ports


def polynomialFunction(coeffients, step, interval):
    x = []
    y = []

    for i in range(interval[0], interval[1] + step, step):
        x.append(i)

        f_x = 0
        for j in range(len(coeffients)):
            f_x += i**j * coeffients[j]
        
        y.append(f_x)
    
    return x, y

def plotGraphic2D(x, y, style, col, points = None, title_x = None, title_y = None):
    x = np.array(x)
    y = np.array(y)

    col = col.lower()

    if title_x != None:
        plt.xlabel(title_x)
    if title_y != None:
        plt.ylabel(title_y)

    plt.axhline(0, color="gray", linewidth="0.5")
    plt.axvline(0, color="gray", linewidth="0.5")

    if style == 1:
        plt.plot(x, y, '-', color=col)
        plt.plot(x[0], y[0], 'ro')
        plt.plot(x[-1], y[-1], 'ro')
    elif style == 2:
        plt.plot(x, y, '-', color=col)
        plt.plot(x, y, 'ro')
    else:
        plt.plot(x, y, '-', color=col)

    if points != None:
        plt.plot(points[0], points[1], 'o', color="magenta")

    return None

def findPeaks(x, y):
    x_peak = []
    y_peak = []

    middle = np.mean(y)

    i = 0
    candidate = 0
    while i < (len(y) -1):
        if i < (len(y) -1) and y[i] < y[i+1] and y[i] > middle:

            while i < (len(y) -1) and y[i] > middle:
                if y[i] >= y[candidate]:
                    candidate = i

                i += 1

            x_peak.append(x[candidate])
            y_peak.append(y[candidate])
        
        else:
            i += 1

    return x_peak, y_peak

def readAFileSignal(path):
    abscissas = []
    ordenates = []
    window = 0

    file = open(path, 'r')

    for line in file:
        if "WINDOWING" in line.upper():
            window = float(line.split(':')[1])
        elif "time" not in line.lower():
            abscissas.append(float(line.split(',')[0]))
            ordenates.append(float(line.split(',')[1]))

    file.close()

    sample_rate = len(ordenates)/(window/1000)

    abscissas = list(map(lambda x: x * 1/sample_rate, abscissas))

    return abscissas, ordenates, sample_rate

def saveFileSignal(file_name, abscissas, ordenates, windowing):
    if file_name == "NO!":
        print("FILE NO SAVED!")
        return None
    else:
        file = open(file_name, 'r')

        file.write("time,signal\n")
        for i in range(len(ordenates)):
            file.write(abscissas[i] + ',' + ordenates[i] + '\n')
        
        file.write("WINDOWING:" + windowing)

        file.close()

        print("FILE '", file_name, "'SAVED!")

        return None


def batchReadSerial(port_name, baud):
    x = []
    y = []
    z = []
    windowing = 0

    device_port = serial.Serial()
    device_port.baudrate = baud
    device_port.timeout = 2

    try:
        device_port.port = port_name
        device_port.open()
    except Exception as exc2:
        print("COULD NOT CONNECTED TO:", port_name)
        print("ERROR:", exc2)
        return
    
    print("CONNECTED TO:", port_name)

    i = 0
    message = str(device_port.readline())[2:-5]
    print(message)
    while "START!" not in message:
        message = str(device_port.readline())[2:-5]
        print(message)

    while "END!" not in message:
        message = str(device_port.readline())[2:-5]
        print(message)

        if "D:" in message:
            values = message.split(':')[1]
            if len(values.split(',')) == 1:
                y.append(float(values))
                x.append(i)
                i += 1
            
            elif len(values.split(',')) == 2:
                x.append(float(values.split(',')[0]))
                y.append(float(values.split(',')[1]))
                i += 1

            elif len(values.split(':')) == 3:
                x.append(float(values.split(',')[0]))
                y.append(float(values.split(',')[1]))
                z.append(float(values.split(',')[2]))
                i += 1

        elif "WINDOWING:" in message:
            windowing = float(message.split(':')[1])
         
    device_port.close()

    return x, y, z, windowing


def listSerialPorts():
    ports_list = []
    ports = serial.tools.list_ports.comports()
    for p in ports:
        ports_list.append(p.device)
        print(p.device)
    
    return ports_list


listSerialPorts()
port_name = input("PORT?")

x, y, w = batchReadSerial(port_name, 115200)

rate = len(x)/(w/1000)

x = list(map(lambda x: x * 1/rate, x))

x_peaks, y_peaks = findPeaks(x, y)

file_name = input("FILE NAME?")
saveFileSignal(file_name, x, y, w)
plotGraphic2D(x, y, 0, 'blue', [x_peaks, y_peaks])

plt.show()