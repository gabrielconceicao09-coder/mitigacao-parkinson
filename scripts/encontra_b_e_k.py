import os
import scipy.optimize
import numpy as np

#Encontrar omega_n, zeta, b e k, dado um valor de m

def EncontraParams(m, omega_0, tau):
    def eq_wn(omega_n_):
        return omega_n_[0] - omega_0/(np.sqrt(1- (1/(tau**2*omega_n_[0]**2)) ))
    omega_n = scipy.optimize.fsolve(eq_wn, [15.0])
    zeta = 1/(tau*omega_n)
    k = m*omega_n**2
    b = 2*m/tau
    return omega_n, zeta, b, k




while(True):
    print("Encontra omega_n, fator de amortecimento, b e k para um sistema massa-mola-amortecedor de 1 grau de liberdade (sistema de segundo grau), dado uma massa m, omega_0 e constante de tempo tau")
    m = float(input("m (kg):"))
    omega_0 = float(input("omega_0:"))
    tau = float(input("tau:"))
    wn, fatamor, coefamor, coefelas = EncontraParams(m, omega_0, tau)
    print("Omega_n: "+str(wn)+"\nFator de amortecimento: "+str(fatamor)+"\nb: "+str(coefamor)+"\nk: "+str(coefelas))

    if input("Encontrar outros parâmetros? (s/n)") == "n":
        break