/*#include <Arduino.h>
#include "controle_pid.h"

float erro;
float erro_anterior;
float deltaerro;
float integral = 0;
float derivada;
unsigned long t_controle; //micros
unsigned long t_controle_anterior; //micros
float deltat;
float sinal_pid;


int controle_pid(float Kp, float Ki, float Kd, float * ac_ref, float * AcZ_ms){
    erro = &ac_ref - &AcZ_ms;
    deltaerro = erro - erro_anterior;
    erro_anterior = erro;
    t_controle = micros();
    deltat = (float) (t_controle - t_controle_anterior)/1000000; //segundos
    t_controle_anterior = t_controle;
    derivada = deltaerro/deltat;
    integral += erro*deltat;
    sinal_pid = Kp*erro + Ki*integral + Kd*derivada;
    int angulo = (int) constrain(sinal_pid, -90.0, 90.0); //Saturação
    angulo += 90; //offset para conformidade com biblioteca Servo do Arduino
    return angulo;
}*/