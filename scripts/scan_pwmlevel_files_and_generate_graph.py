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

def readAFileSignal(path, mode):
    ##Mode = 0 for 3 dimensions + windowing; Mode = 1 for 2 dimensions;
    windowing = 0
    x = []
    y = []
    z = []

    file = open(path, 'r')
    if mode == 0:        
        for line in file:
            if "WINDOWING" in line.upper():
                windowing = float(line.split(':')[1])
            elif "time" not in line.lower():
                #abscissas.append(float(line.split(',')[0]))
                #ordenates.append(float(line.split(',')[1]))
                x.append(float(line.split(",")[0]))
                y.append(float(line.split(",")[1]))
                z.append(float(line.split(",")[2]))
        file.close()
        return x, y, z, windowing
    elif mode == 1:
        p = []
        for line in file:
                x.append(float(line.split(",")[0]))
                y.append(float(line.split(",")[1]))
                z.append(float(line.split(",")[2]))
                p.append(float(line.split(",")[3]))
        file.close()
        return x, y, z, p
        

def saveFileSignal(file_name, x, y, z, windowing): #Alterado para salvar as 3 acelerações no teste do PWM
    if file_name == "NO!":
        print("FILE NOT SAVED!")
        return None
    else:
        file = open(file_name, 'w')

        #file.write("time,signal\n")
        #for i in range(len(ordenates)):
        #    file.write(abscissas[i] + ',' + ordenates[i] + '\n')

        for i in range(len(x)):{
            file.write(str(x[i]) + "," + str(y[i]) + "," + str(z[i]) + "\n")
        }
        
        file.write("WINDOWING:" + str(windowing)) #windowing deve estar em segundos.

        file.close()

        print("FILE '", file_name, "'SAVED!")

        return None

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
    dom_freq_vector = [[],[],[],[],[]] #Array com listas para abrigar as frequencias dominantes em cada componente (x, y, z), para cada arquivo lido
    dom_mag_vector = [[],[],[],[],[[],[],[]]] #Quinto array contem 3 arrays para abrigar as magnitudes dominantes para x, y e z, de acordo com as frequências dominantes obtidas com a média dos espectros.
    pwm = [] #Lista com niveis pwm

    for file in file_list:
        path_to_file = directory_path+'/'+file
        x, y, z, w = readAFileSignal(path_to_file, 0)
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
                a_f = fft(a_np);
                a_f = np.absolute(a_f)
                a_freq = fftfreq(len(a_f), w)[:len(a_f)//2];
                a_f = a_f[:len(a_f)//2]

                eval_a_f = a_f[1:]
                eval_a_freq = a_freq[1:]

                dom_freq = eval_a_freq[np.argmax(eval_a_f)]
                dom_mag = eval_a_f[np.argmax(eval_a_f)]
                
                dom_freq_vector[i].append(dom_freq)
                dom_mag_vector[i].append(dom_mag)

            elif i ==4:
                x_np = np.array(x); 
                x_f = fft(x_np);
                x_f = np.absolute(x_f)
                x_freq = fftfreq(len(x_f), w)[:len(x_f)//2];
                x_f = x_f[:len(x_f)//2]

                y_np = np.array(y); 
                y_f = fft(y_np);
                y_f = np.absolute(y_f)
                y_freq = fftfreq(len(y_f), w)[:len(y_f)//2];
                y_f = y_f[:len(y_f)//2]
        
                z_np = np.array(z); 
                z_f = fft(z_np);
                z_f = np.absolute(z_f)
                z_freq = fftfreq(len(z_f), w)[:len(z_f)//2];
                z_f = z_f[:len(z_f)//2]

                a_f = []
                for k in range(0,len(x_f)):
                    a_f.append((x_f[k]+y_f[k]+z_f[k])/3) ##Tira media simples dos resultados *dos espectros* para produzir um resultado mais consistente e representativo da resposta do sistema inteiro a entrada do motor.
                a_f = np.array(a_f)
                a_freq = x_freq

                eval_a_f = a_f[1:]
                eval_x_f = x_f[1:]
                eval_y_f = y_f[1:]
                eval_z_f = z_f[1:]

                eval_a_freq = a_freq[1:]

                dom_freq = eval_a_freq[np.argmax(eval_a_f)]
                dom_mag_x = eval_x_f[np.argmax(eval_a_f)]
                dom_mag_y = eval_y_f[np.argmax(eval_a_f)]
                dom_mag_z = eval_z_f[np.argmax(eval_a_f)]

                dom_freq_vector[i].append(dom_freq)

                dom_mag_vector[i][0].append(dom_mag_x)
                dom_mag_vector[i][1].append(dom_mag_y)
                dom_mag_vector[i][2].append(dom_mag_z)
    

    return dom_mag_vector, dom_freq_vector, pwm #os vetores sao listas contendo x,y,z da magnitude na frequencia dominante e da frequencia dominante


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
        plt.plot(p, dom_freq_vector[4], 'ro') #Freq. vs. nível pwm
        plt.xlabel("Nível PWM")
        plt.ylabel("\u03C9 (Hz)")
        plt.title("Frequência dominante (\u03C9) vs. Nível PWM, Média dos espectros")
        plt.savefig('/home/gabs/Documents/Pibic/RelacoesPWM/DomFreqVsPWM_neat.pdf')
        plt.show()

        plt.figure()
        plt.title("Densidade de aceleração na frequência dominante vs. Nível PWM")
        plt.subplot(3, 1, 1)
        plt.plot(p, dom_mag_vector[4][0], 'bo')
        plt.xlabel("Nível PWM")
        plt.ylabel("Dx (m/s)")
        plt.title("Componente X")

        plt.subplot(3,1,2)
        plt.plot(p, dom_mag_vector[4][1], 'go')
        plt.xlabel("Nível PWM")
        plt.ylabel("Dy (m/s)")
        plt.title("Componente Y")

        plt.subplot(3,1,3)
        plt.plot(p, dom_mag_vector[4][2], 'ro')
        plt.xlabel("Nível PWM")
        plt.ylabel("Dz (m/s)")
        plt.title("Componente Z")

        plt.savefig('/home/gabs/Documents/Pibic/RelacoesPWM/DomMag3CompVsPWM_neat.pdf')
        plt.show()
        
    file_save_path_freq = '/home/gabs/Documents/Pibic/RelacoesPWM/FreqXPwm1.txt' #input('Path to save .txt file for dominant frequencies? (includes all components)')
    saveFileDomFreqMag(file_save_path_freq, dom_freq_vector[0], dom_freq_vector[1], dom_freq_vector[2], p)
    file_save_path_mag = '/home/gabs/Documents/Pibic/RelacoesPWM/MagAtFreqXPwm1.txt' #input('Parh to save .txt file for magnitudes at dominant frequency? (includes all components)')
    saveFileDomFreqMag(file_save_path_mag, dom_mag_vector[0], dom_mag_vector[1], dom_mag_vector[2], p)

    directory_path = input("Next directory path? (Empty to exit program)")

