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

try:
    from scipy.fft import fft, fftfreq
except Exception as exc4:
    os.system("pip install scipy")
    from scipy.fft import fft, fftfreq

import scipy.signal.windows

from scipy.optimize import curve_fit

def readAFileSignal(path, mode):
    ##Mode = 0 for 3 dimensions + sampling interval; Mode = 1 for 2 dimensions;
    interval = 0
    x = []
    y = []
    z = []

    file = open(path, 'r')
    if mode == 0:        
        for line in file:
            if "INTERVAL" in line.upper():
                interval = float(line.split(':')[1])
            else:
                x.append(float(line.split(",")[0]))
                y.append(float(line.split(",")[1]))
                z.append(float(line.split(",")[2]))
        file.close()
        return x, y, z, interval
    elif mode == 1:
        p = []
        for line in file:
                x.append(float(line.split(",")[0]))
                y.append(float(line.split(",")[1]))
                z.append(float(line.split(",")[2]))
                p.append(float(line.split(",")[3]))
        file.close()
        return x, y, z, p
        

def saveFileDomFreqMag(file_path, x, y, z, p): #Salva resultados da frequencia dominante ou magnitude na frequencia dominante em funçao do nivel pwm.
    if file_path == "NO!":
        print("FILE NOT SAVED!")
        return None
    else:
        file = open(file_path, 'w')

        for i in range(len(p)):{
            file.write(str(x[i]) + "," + str(y[i]) + "," + str(z[i]) + "," + str(p[i]) + "\n")
        }
        
        file.close()

        print("FILE '", file_path, "'SAVED!")
        return None

def scanDirGenerateDomFreqMagXPWM(directory_path):
    file_list = os.listdir(directory_path)
    dom_freq_vector = [[],[],[],[],[]] #Array com listas para abrigar as frequencias dominantes em cada componente (x, y, z), para cada arquivo lido, além da frequência dominante do vetor resultante e a frequência dominante da média dos espectros
    dom_mag_vector = [[],[],[],[],[[],[],[]]] #Quinto array contem 3 arrays para abrigar as magnitudes dominantes para x, y e z, de acordo com as frequências dominantes obtidas com a média dos espectros.
    pwm = [] #Lista com niveis pwm

    for file in file_list:
        path_to_file = directory_path+'/'+file
        x, y, z, w = readAFileSignal(path_to_file, 0)
        hann_filter = scipy.signal.windows.hann(len(x))
        title = file.split('/')[-1]
        title = title.split('.')[0]
        title = title.split('m')[1]
        if 'n' in title:
            title = title.replace('n', '')
            pwm_level = -1*float(title)
        elif 'n' not in title:
            pwm_level = float(title)
        pwm.append(pwm_level)

        components = [x, y, z]

        for i in range(0,5):
            if i<4: 
                if i==3:
                    a = []
                    for j in range(0,len(x)): 
                        a.append(np.sqrt((np.square(x[j])+np.square(y[j])+np.square(z[j]))))
                else: 
                    a = components[i]

                a_np = np.array(a);
                a_np = np.multiply(a_np,hann_filter)
                a_f = fft(a_np);
                a_f = np.absolute(a_f)
                a_freq = fftfreq(len(a_f), w)[:len(a_f)//2];
                a_f = a_f[:len(a_f)//2]

            elif i ==4:
                x_np = np.array(x); 
                x_np = np.multiply(x_np,hann_filter)
                x_f = fft(x_np);
                x_f = np.absolute(x_f)
                x_freq = fftfreq(len(x_f), w)[:len(x_f)//2];
                x_f = x_f[:len(x_f)//2]

                y_np = np.array(y); 
                y_np = np.multiply(y_np,hann_filter)
                y_f = fft(y_np);
                y_f = np.absolute(y_f)
                y_freq = fftfreq(len(y_f), w)[:len(y_f)//2];
                y_f = y_f[:len(y_f)//2]
        
                z_np = np.array(z); 
                z_np = np.multiply(z_np, hann_filter)
                z_f = fft(z_np);
                z_f = np.absolute(z_f)
                z_freq = fftfreq(len(z_f), w)[:len(z_f)//2];
                z_f = z_f[:len(z_f)//2]

                a_f = []
                for k in range(0,len(x_f)):
                    a_f.append((x_f[k]+y_f[k]+z_f[k])/3) ##Tira media simples dos resultados *dos espectros*.
                a_f = np.array(a_f)
                a_freq = x_freq

            eval_a_f = a_f[1:]
            eval_a_freq = a_freq[1:]

            dom_mag = eval_a_f[np.argmax(eval_a_f)] #Obtem frequência dominante e magnitude correspondente para cada componente
            dom_freq = eval_a_freq[np.argmax(eval_a_f)]
            dom_freq_vector[i].append(dom_freq)
            
            if i<4:
                dom_mag_vector[i].append(dom_mag)
            elif i ==4:
                eval_x_f = x_f[1:]
                eval_y_f = y_f[1:]
                eval_z_f = z_f[1:]

                dom_mag_x = eval_x_f[np.argmax(eval_a_f)]
                dom_mag_y = eval_y_f[np.argmax(eval_a_f)]
                dom_mag_z = eval_z_f[np.argmax(eval_a_f)]

                dom_mag_vector[i][0].append(dom_mag_x)
                dom_mag_vector[i][1].append(dom_mag_y)
                dom_mag_vector[i][2].append(dom_mag_z)


    return dom_mag_vector, dom_freq_vector, pwm #os vetores sao listas contendo x,y,z da magnitude na frequencia dominante e da frequencia dominante


def fitLinear(x, y):
    def func(t, a, b):
        return float(a)*np.array(t) + float(b)
    popt, pcov = curve_fit(func, x, y)
    return func(x, popt[0], popt[1]), popt[0], popt[1]

directory_path = input("Directory path? (Empty to exit program)")
while directory_path != '':
    dom_mag_vector, dom_freq_vector, p = scanDirGenerateDomFreqMagXPWM(directory_path)

    component = int(input('Component to plot? (0 for x, 1 for y, 2 for z, 3 for magnitude of vector, 4 for results after average of spectra), 5 for neat results'))
    if component <5:
        print(p, dom_freq_vector[component])
        plt.figure()
        plt.subplot(2,1,1)
        plt.plot(p, dom_freq_vector[component], 'ro') #Plota freq. vs. nivel pwm.
        plt.subplot(2,1,2)
        plt.plot(p, dom_mag_vector[component], 'bo') #Plota mag. na freq dominante vs. nível pwm
        plt.show()
    elif component == 5:
        print(p, dom_freq_vector[4])
        plt.figure()
        lin_fit_pos, apos, bpos = fitLinear(p[13:], dom_freq_vector[4][13:]) 
        lin_fit_neg, aneg, bneg = fitLinear(p[:13], dom_freq_vector[4][:13])
        neglabel = "Ajuste Linear a*x + b; a = "+str(-0.56)+", b = "+str(10.56)
        poslabel = "Ajuste Linear c*x + d; c = "+str(0.48)+", d = "+str(6.36)
        plt.plot(p[:13], lin_fit_neg, 'k-', label=neglabel) #ajuste linear níveis PWM negativos
        plt.legend()
        plt.plot(p[13:], lin_fit_pos, 'b-', label=poslabel) #ajuste linear níveis PWM positivos
        plt.legend()
        plt.plot(p, dom_freq_vector[4], 'ro', label="Frequência dominante vs. Nível PWM") #Freq. vs. nível pwm
        plt.legend()
        plt.xlabel("Nível PWM")
        plt.ylabel("\u03C9 (Hz)")
        plt.title("Frequência dominante (\u03C9) vs. Nível PWM, Média dos espectros")
        plt.savefig('/home/gabs/Documents/Pibic/RelacoesPWM/DomFreqVsPWM_media.pdf')

        plt.close()
        plt.figure(None,[6.4,10.0])
        lin_fit_pos, apos, bpos = fitLinear(p[13:], dom_freq_vector[0][13:]) 
        lin_fit_neg, aneg, bneg = fitLinear(p[:13], dom_freq_vector[0][:13])
        neglabel = "Ajuste Linear a*x + b; a = "+str(0.16)+", b = "+str(70.50)
        poslabel = "Ajuste Linear c*x + d; c = "+str(0.08)+", d = "+str(43.68)
        plt.subplot(311)
        plt.title("Frequência dominante (\u03C9x, \u03C9y, \u03C9z) vs. Nível PWM")
        plt.plot(p[:13], lin_fit_neg, 'k-', label=neglabel) #ajuste linear níveis PWM negativos
        plt.legend()
        plt.plot(p[13:], lin_fit_pos, 'r-', label=poslabel) #ajuste linear níveis PWM positivos
        plt.legend()
        plt.plot(p, dom_freq_vector[0], 'bo', label="Frequência dominante (\u03C9x) vs. Nível PWM")
        plt.legend()
        plt.xlabel("Nível PWM")
        plt.ylabel("\u03C9x (Hz)")
    
        plt.subplot(312)
        lin_fit_pos, apos, bpos = fitLinear(p[13:], dom_freq_vector[1][13:]) 
        lin_fit_neg, aneg, bneg = fitLinear(p[:13], dom_freq_vector[1][:13])
        neglabel = "Ajuste Linear a*x + b; a = "+str(-0.56)+", b = "+str(10.48)
        poslabel = "Ajuste Linear c*x + d; c = "+str(0.36)+", d = "+str(18.91)
        plt.plot(p[:13], lin_fit_neg, 'k-', label=neglabel) #ajuste linear níveis PWM negativos
        plt.legend()
        plt.plot(p[13:], lin_fit_pos, 'b-', label=poslabel) #ajuste linear níveis PWM positivos
        plt.legend()
        plt.plot(p, dom_freq_vector[1], 'go', label="Frequência dominante (\u03C9y) vs. Nível PWM")
        plt.legend()
        plt.xlabel("Nível PWM")
        plt.ylabel("\u03C9y (Hz)")
        
        plt.subplot(313)
        lin_fit_pos, apos, bpos = fitLinear(p[13:], dom_freq_vector[2][13:]) 
        lin_fit_neg, aneg, bneg = fitLinear(p[:13], dom_freq_vector[2][:13])
        neglabel = "Ajuste Linear a*x + b; a = "+str(0.19)+", b = "+str(50.86)
        poslabel = "Ajuste Linear c*x + d; c = "+str(0.24)+", d = "+str(22.74)
        plt.plot(p[:13], lin_fit_neg, 'k-', label=neglabel) #ajuste linear níveis PWM negativos
        plt.legend()
        plt.plot(p[13:], lin_fit_pos, 'g-', label=poslabel) #ajuste linear níveis PWM positivos
        plt.legend()
        plt.plot(p, dom_freq_vector[2], 'ro', label="Frequência dominante (\u03C9z) vs. Nível PWM")
        plt.legend()
        plt.xlabel("Nível PWM")
        plt.ylabel("\u03C9z (Hz)")
        plt.savefig('/home/gabs/Documents/Pibic/RelacoesPWM/DomFreq3CompVsPWM.pdf')


        plt.close()
        plt.figure(None,[6.4,10.0])
        plt.subplot(311)
        plt.title("Magnitude (Mx, MY, Mz) vs. Nível PWM")
        plt.plot(p, dom_mag_vector[4][0], 'bo')
        plt.xlabel("Nível PWM")
        plt.ylabel("Mx (m/s)")
    
        plt.subplot(312)
        plt.plot(p, dom_mag_vector[4][1], 'go')
        plt.xlabel("Nível PWM")
        plt.ylabel("My (m/s)")
        
        plt.subplot(313)
        plt.plot(p, dom_mag_vector[4][2], 'ro')
        plt.xlabel("Nível PWM")
        plt.ylabel("Mz (m/s)")
        plt.savefig('/home/gabs/Documents/Pibic/RelacoesPWM/DomMag3CompVsPWM.pdf')


    file_save_path_freq = '/home/gabs/Documents/Pibic/RelacoesPWM/FreqXPwm2.txt' #input('Path to save .txt file for dominant frequencies? (includes all components)')
    saveFileDomFreqMag(file_save_path_freq, dom_freq_vector[0], dom_freq_vector[1], dom_freq_vector[2], p)
    file_save_path_mag = '/home/gabs/Documents/Pibic/RelacoesPWM/MagAtFreqXPwm2.txt' #input('Parh to save .txt file for magnitudes at dominant frequency? (includes all components)')
    saveFileDomFreqMag(file_save_path_mag, dom_mag_vector[0], dom_mag_vector[1], dom_mag_vector[2], p)

    directory_path = input("Next directory path? (Empty to exit program)")

