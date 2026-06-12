import os

def saveFileSignal(file_name, x, y, z, interval): #Salva as 3 acelerações no teste do PWM
    if file_name == "NO!":
        print("FILE NOT SAVED!")
        return None
    else:
        file = open(file_name, 'w')

        for i in range(len(x)):{
            file.write(str(x[i]) + "," + str(y[i]) + "," + str(z[i]) + "\n")
        }
        
        file.write("INTERVAL:" + str(interval)) #interval deve estar em segundos

        file.close()

        print("FILE '", file_name, "'SAVED!")

        return None
    
def readAFileSignal(path, mode):
    ##Mode = 0 for 3 dimensions + interval; Mode = 1 for [Mag, Freq];
    interval = 0
    x = []
    y = []
    z = []

    file = open(path, 'r')
    if mode == 0:        
        for line in file:
            if "INTERVAL" in line.upper():
                interval = float(line.split(':')[1])
            elif "time" not in line.lower():
                x.append(float(line.split(",")[0]))
                y.append(float(line.split(",")[1]))
                z.append(float(line.split(",")[2]))
        file.close()
        return x, y, z, interval
    elif mode == 1:
        for line in file:
                x.append(float(line.split(",")[0]))
                y.append(float(line.split(",")[1]))
        file.close()
        return x, y #x = Mag; y = Freq