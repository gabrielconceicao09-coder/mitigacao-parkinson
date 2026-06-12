/*#pragma once
#include <Arduino.h>

//Controle PID
float erro;
float erro_anterior;
float deltaerro;
float integral = 0;
float derivada;
unsigned long t_controle; //micros
unsigned long t_controle_anterior = micros();
float deltat;
float sinal_pid;

int controle_pid(float Kp, float Ki, float Kd, float * ac_ref, float * AcZ_ms);
*/