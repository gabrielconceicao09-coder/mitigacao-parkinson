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
import matplotlib.pyplot as plt


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

    a_np = np.array(a)[:len(a)//2]; 
    a_t = np.linspace(0, len(a)*w, len(a))[:len(a)//2] #Tempo de cada amostra, recuperado do período de amostragem w

    pwm_level = file.split('/')[-1]
    pwm_level = pwm_level.split('.')[0]
    pwm_level = pwm_level.split('m')[1]
    if 'n' in pwm_level:
        pwm_level = pwm_level.replace('n', '-')

    plt.figure()
    plt.plot(a_t, a_np, 'k')
    plt.title('Componente '+comp_title+', Aceleração (m/s\u00B2) vs. Tempo (s), Nível PWM: '+pwm_level)
    plt.savefig("/home/gabs/Documents/Pibic/RelacoesPWM/SIGNAL"+comp_title+file.split('/')[-1].replace(".txt",".pdf"))
    plt.show()

    file = input("NEXT FILE PATH? (Empty to exit program)");
print("Finished!")
