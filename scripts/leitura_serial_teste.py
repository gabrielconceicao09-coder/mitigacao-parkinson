import numpy as np;
from scipy.fft import fft, fftfreq;
import serial;
import time;
import matplotlib.pyplot as plt;

#Recebe a saida do arduino por comunicacao serial e extrai as aceleraçoes medidas, seguindo o formato de output do 'le_sensorMPU'

serial_port = '/dev/ttyUSB0';

ser = serial.Serial(serial_port, baudrate= 115200, timeout= 1, bytesize=8, stopbits=1);

#definindo os arrays para as diferentes acelerações recebidas
accGx = np.array([]);
accGy = np.array([]);
accGz = np.array([]);
acc_ms2x = np.array([]);
acc_ms2y = np.array([]);
acc_ms2z = np.array([]);
acc_avg = np.array([]);

#frequência de amostragem
f_s = 100;
#espaçamento de amostragem
T = 1/f_s;

#lê linha a linha da saída serial do arduino por cinco segundos

count = 0;
time0 = time.time();
while(time.time() - time0 < 5){
    #Alterna entre uma função para ler acc em g e acc em ms2
    linha = ser.readline();
    if (count == 0){
        linha_itens =  linha.split(' ');
        accGx.append(float(linha_itens[2]));
        accGy.append(float(linha_itens[6]));
        accGz.append(float(linha_itens[10]));
        count = 1;
        linha_itens = [];
    }
    else if (count == 1){
        linha_itens = linha.split(' ');
        acc_ms2x.append(float(linha_itens[2]));
        acc_ms2y.append(float(linha_itens[6]));
        acc_ms2z.append(float(linha_itens[10]));
        count = 0;
        linha_itens = [];     
    }
     }



#fft da aceleraçao
accGx_f = fft(accGx);
accGy_f = fft(accGy);
accGz_f = fft(accGz);

acc_ms2x_f = fft(acc_ms2x);
acc_ms2y_f = fft(acc_ms2y);
acc_ms2z_f = fft(acc_ms2z);

#pontos de frequencia de acordo com a amostragem da aceleraçao no tempo
omegaG = fftfreq(len(accGx), T);
omegaMs2 = fftfreq(len(acc_ms2x, T));

#plota a transformada da aceleraçao contra a frequencia
plt.plot(omegaMs2, acc_ms2x_f);
plt.grid();
plt.show();