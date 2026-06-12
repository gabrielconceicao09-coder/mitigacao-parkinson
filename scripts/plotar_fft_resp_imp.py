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
    import serial
    import serial.tools.list_ports
except Exception as exc3:
    os.system("pip install pyserial")
    import serial
    import serial.tools.list_ports

try:
    from scipy.fft import fft, fftfreq
except Exception as exc4:
    os.system("pip install scipy")
    from scipy.fft import fft, fftfreq

import scipy.signal.windows


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
    hann_filter = scipy.signal.windows.hann(len(x))  
    exclude_zero = bool(input("Exclude 0 Hz component? (0 for No, 1 for Yes)")) ##Check if user wants to exclude 0 Hz component
    component = int(input("COMPONENT? (0 for x, 1 for y, 2 for z, 3 for magnitude of vector, 4 for average of the 3 component spectra)"))
    if (component == 0): 
        a = x
        comp_title = 'Eixo X'
    elif component ==1:  
        a = y
        comp_title = 'Eixo Y'
    elif component ==2: 
        a = z
        comp_title = 'Eixo Z'
    elif component ==3:
        a = []
        for i in range(0, len(x)):
            a.append(np.sqrt((np.square(x[i])+np.square(y[i])+np.square(z[i]))))
        comp_title = 'Magnitude of vector'
    elif component ==4:
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

        if exclude_zero:
            x_f = x_f[1:]
            x_freq = x_freq[1:]
            y_f = y_f[1:]
            y_freq = y_freq[1:]
            z_f = z_f[1:]
            z_freq = z_freq[1:]
        
        a_f = []
        for i in range(0,len(x_f)):
            a_f.append((x_f[i]+y_f[i]+z_f[i])/3)
        a_f = np.array(a_f)
        a_freq = x_freq

        comp_title="Média dos 3 espectros"
    else:
        a = x
        comp_title = 'Eixo X'
    
    if component != 4:
        a_np = np.array(a); 
        a_np = np.multiply(a_np, hann_filter)
        a_f = fft(a_np);
        a_f = np.absolute(a_f)
        a_freq = fftfreq(len(a_f), w)[:len(a_f)//2];
        a_f = a_f[:len(a_f)//2]
        if exclude_zero:
            a_f = a_f[1:]
            a_freq = a_freq[1:]
    
    dom_mag = a_f[np.argmax(a_f)]
    dom_freq = a_freq[np.argmax(a_f)]

    print('Dominant frequency:'+str(dom_freq))
    plt.plot(a_freq, a_f)
    plt.plot(dom_freq, dom_mag, '*k')
    plt.title('Resposta ao impulso da bancada, '+comp_title+', Magnitude (M) vs. Frequência (\u03C9)')
    plt.xlabel("\u03C9 (Hz)")
    plt.ylabel("M (m/s)")
    plt.show()
    file = input("NEXT FILE PATH? (Empty to exit program)");
print("Finished!")
