import os
try:
    import serial
    import serial.tools.list_ports
except Exception as exc3:
    os.system("pip install pyserial")
    import serial
    import serial.tools.list_ports



def saveFileSignal(file_name, x, y, z, interval): #Salva as 3 acelerações no teste do PWM
    if file_name == "NO!":
        print("FILE NOT SAVED!")
        return None
    else:
        file = open(file_name, 'w')

        for i in range(len(x)):{
            file.write(str(x[i]) + "," + str(y[i]) + "," + str(z[i]) + "\n")
        }
        
        file.write("INTERVAL:" + str(interval)) #interval deve estar em segundos

        file.close()

        print("FILE '", file_name, "'SAVED!")

        return None


def batchReadSerial(port_name, baud):
    x = []
    y = []
    z = []
    windowing = 0

    device_port = serial.Serial()
    device_port.baudrate = baud
    device_port.timeout = 2

    try:
        device_port.port = port_name
        device_port.open()
    except Exception as exc2:
        print("COULD NOT CONNECTED TO:", port_name)
        print("ERROR:", exc2)
        return
    
    print("CONNECTED TO:", port_name)
    
    i = 0
    message = str(device_port.readline())[2:-5]
    print(message)
    while "START!" not in message:
        message = str(device_port.readline())[2:-5]
        print(message)
        if 'receive PWM' in message:
            pwm_level = input('Pwm level? (-200 to 200)')+"\n" ##Setup PWM pela comunicação serial
            pwm_level = pwm_level.encode("utf-8")
            device_port.write(pwm_level)


    while "END!" not in message:
        message = str(device_port.readline())[2:-5]
        print(message)
 
        if "INTERVAL:" not in message and "END!" not in message:
            values = message
            if len(values.split(',')) == 1:
                y.append(float(values))
                x.append(i)
                i += 1
            
            elif len(values.split(',')) == 2:
                x.append(float(values.split(',')[0]))
                y.append(float(values.split(',')[1]))
                i += 1

            elif len(values.split(',')) == 3:
                x.append(float(values.split(',')[0]))
                y.append(float(values.split(',')[1]))
                z.append(float(values.split(',')[2]))
                i += 1

        elif "INTERVAL:" in message:
            interval = float(message.split(':')[1]) #Obtém o tempo de amostragem em ms
         
    device_port.close()

    return x, y, z, interval


def listSerialPorts():
    ports_list = []
    ports = serial.tools.list_ports.comports()
    for p in ports:
        ports_list.append(p.device)
        print(p.device)
    
    return ports_list


listSerialPorts()
port_name = input("PORT?")

x, y, z, w = batchReadSerial(port_name, 115200)
interval = w/1000

#file_name = input("FILE PATH?")
#saveFileSignal(file_name, x, y, z, interval)
print("Finished")