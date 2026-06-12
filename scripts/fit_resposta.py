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
    import scipy.optimize
except Exception as exc:
    os.system("pip install scipy")
    import scipy.optimize

try:
    import math
except Exception as exc:
    os.system("pip install math")
    import math

try:
    import control as ct
except Exception as exc:
    os.system("pip install control")

import read_and_save_signal_functions as rsu



file = input("Esse programa ajusta as medições obtidas sobre a resposta da aceleração esperada para um sistema massa-mola-amortecedor \n FILE PATH(Empty to exit program):");

while(file != ''):

    x, y, z, w = rsu.readAFileSignal(file, 0)
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

    #Ajustar função:

    def acc_step_resp(t, tau, beta, omega_0, phi, G, t_d): #Define resposta ao degrau esperada
        return G*( beta*np.exp(-1*(t-t_d)/tau)*( (omega_0**2 + np.cos(phi)/tau)*np.cos(omega_0*(t-t_d)) + (omega_0*(1 - (1/tau)) + np.sin(phi)/tau)*np.sin(omega_0*(t-t_d))) )
    
    def acc_imp_resp(t, tau, omega_0, G, t_d): #Resposta ao impulso esperada
        return -1*G*np.exp(-1*(t-t_d)/tau)*( (omega_0/tau**2 - omega_0**2)*(np.cos(omega_0*(t-t_d)) + np.sin(omega_0*(t-t_d))) -2*omega_0/tau*((np.cos(omega_0*(t-t_d)) - np.sin(omega_0*(t-t_d)))) )
    

    while(True):
        mode = int(input("Ajustar para resposta ao degrau (0) ou para resposta ao impulso (1)?"))
        print("Chutes iniciais? (degrau: [tau, beta, omega_0, phi, G, t_d]; impulso: [tau, omega_0, G, t_d])")
        tau_ = float(input("tau:"))
        beta_ = float(input("beta:"))
        omega_0_ = float(input("omega_0:"))
        phi_ = float(input("phi:"))
        g_ = float(input("G:"))
        t_d_ = float(input("Deslocamento no tempo:"))
        

        if mode == 0:
            resposta = "Resposta ao degrau"
            popt, pcov = scipy.optimize.curve_fit(acc_step_resp, a_t, a_np, [tau_, beta_, omega_0_, phi_, g_, t_d_]) #Realiza o ajuste pelo método dos quadrados mínimos
            fit_y = acc_step_resp(a_t, popt[0], popt[1], popt[2], popt[3], popt[4], popt[5])
        elif mode == 1:
            resposta = "Resposta ao impulso"
            popt, pcov = scipy.optimize.curve_fit(acc_imp_resp, a_t, a_np, [tau_, omega_0_, g_, t_d_]) #Realiza o ajuste pelo método dos quadrados mínimos
            fit_y = acc_imp_resp(a_t, popt[0], popt[1], popt[2], popt[3])
        print("Parâmetros ajustados (degrau: [tau, beta, omega_0, phi, G, t_d]; impulso: [tau, omega_0, G, t_d]): "+str(popt))
        print(pcov)
        fit_y_np = np.array(fit_y)
        
        plt.figure()
        plt.plot(a_t, a_np, 'k')
        plt.plot(a_t, fit_y_np, 'r')
        plt.title('Componente '+comp_title+', '+resposta+', Aceleração (m/s\u00B2) e Função ajustada (m/s\u00B2) vs. Tempo (s))')
        plt.show()

        if input("Tentar outro ajuste com esse arquivo? (y/n)") == "n":
            break


    file = input("NEXT FILE PATH? (Empty to exit program)");
print("Finished!")