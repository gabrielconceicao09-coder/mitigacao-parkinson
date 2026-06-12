#Le arquivo de sinais e converte pra modelo legível pelo Octave + arquivo suporte pra armazenar o periodo de amostragem
def saveFileFormated(orig_name, x, y, z, interval):
    if orig_name == "NO!":
        print("FILE NOT SAVED!")
        return None
    else:
        file_name = orig_name[:-4]+"_formatado.txt"
        file = open(file_name, 'w')

        for i in range(len(x)):{
            file.write(str(x[i]) + " " + str(y[i]) + " " + str(z[i]) + "\n")
        }
        file.close()
        
        auxfile_name = orig_name[:-4]+"_formatado_aux.txt"

        auxfile = open(auxfile_name, 'w')
        auxfile.write(str(interval))
        auxfile.close()

        print("FILES '", file_name, "' AND '", auxfile_name, "' 'SAVED!")

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
    
file = input("Converte arquivo .txt do modelo usado no início do projeto para uma formatação mais acessível pelo Octave além de um arquivo auxiliar com o tempo de amostragem. FILE PATH(Empty to exit program):");

while(file != ''):
    x, y, z, interval = readAFileSignal(file, 0)
    saveFileFormated(file, x, y, z, interval)
    file = input("NEXT FILE PATH(Empty to exit program):")
    
print("EXITED PROGRAM")