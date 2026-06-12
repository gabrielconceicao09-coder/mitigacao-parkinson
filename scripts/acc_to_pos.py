import os
import numpy as np
import matplotlib.pyplot as plt

def saveFileSignal_1D(file_name, x, t): #Salva as 3 acelerações no teste do PWM
    if file_name == "NO!":
        print("FILE NOT SAVED!")
        return None
    else:
        file = open(file_name, 'w')

        for i in range(len(x)):{
            file.write(str(x[i]) + "," + str(t[i]) + "\n")
        }
        
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

file = input("FILE PATH(Empty to exit program):");

while(file != ''):
    x, y, z, w = readAFileSignal(file, 0)
    component = int(input("COMPONENT? (0 for x, 1 for y, 2 for z)"))
    if (component == 0): 
        a = x
        comp_title = 'X'
    elif component ==1: 
        a = y
        comp_title = 'Y'
    elif component ==2: 
        a = z
        comp_title = 'Z'
    else: 
        a = x
        comp_title = 'X'

    a_np = np.array(a);
    a_t = np.linspace(0, len(a)*w, len(a)) #Tempo de cada amostra, recuperado do período de amostragem w
    
    v = []
    for i in range(len(a_np)):
        v.append(np.trapz(a_np[:i], a_t[:i]))
    v_np = np.array(v)
    p = []
    for i in range(len(v)):
        p.append(np.trapz(v[:i], a_t[:i]))
    p_np = np.array(p)

    plt.figure()
    plt.plot(a_t[:len(v)], v, 'k')
    plt.title('Componente '+comp_title+', Velocidade (m/s) vs. Tempo (s))')
    #plt.savefig("/home/gabs/Documents/Pibic/RelacoesPWM/SIGNAL"+comp_title+file.split('/')[-1].replace(".txt",".pdf"))
    plt.show()
    plt.figure()
    plt.plot(a_t[:len(p)], p, 'k')
    plt.title('Componente '+comp_title+', Posição (m) vs. Tempo (s))')
    plt.show()

    file = input("NEXT FILE PATH? (Empty to exit program)");
print("Finished!")

