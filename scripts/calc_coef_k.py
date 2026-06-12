#Calcula coeficiente k da bancada
print("Calcula coeficiente k para o modelo de deflexão de viga devido a força pontual")
print("L: Comprimento da viga em cm (ponta engastada até força pontual)\n")
print("l: Distância da força pontual em cm (até ponto da viga onde deflexão é calculada, no caso, dist. da massa até o MPU6050)\n")
print("E: Módulo de Young do material da viga em GPa\n")
print("b: Largura da sessão transversal retangular em mm\n")
print("h: Altura da sessão transversal retangular em mm\n")
entrada = input("Forneça os parâmetros (L, l, E, b, h): ")

args = []
for param in entrada.split(', '):
    args.append(float(param))
cL = args[0]*10**(-2)
cl = args[1]*10**(-2)
cE = args[2]*10**6
cb = args[3]*10**(-3)
ch = args[4]*10**(-3)

k = 6*cE*(cb*ch**3/12)/(3*cL**2*cl+2*cL**3-cl**3)
print(f"Coeficiente k: {k}")