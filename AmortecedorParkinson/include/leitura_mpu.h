/*#pragma once
#ifndef LEITURA_MPU_H_
#define LEITURA_MPU_H_
#include <Arduino.h>
#include <Wire.h>
#include <cppQueue.h>

//Leitura do MPU


void init_MPU6050(int AFS_SEL, int DLPF_SEL); //inicializa mpu, acessando registrador que acorda o sensor, aplicando configurações escolhidas.
//Configuração do acelerômetro AFS_SEL (0: +/-2g; 1: +/-4g; 2: +/-8g)
//Filtro passa-baixa DLPF_SEL (0: BW 260 Hz; 1: BW 184 Hz; 2: BW 94 Hz; 3: BW 44 Hz; 4: BW 21 Hz; 5: BW 10 Hz, 6: BW 5 Hz)

void Calc_Grvt(int acx, int acy, int acz, float* pAcX_ms, float* pAcY_ms, float* pAcZ_ms); //calcula gravidade em m/s^2

void leituraMPU_ISR(); //Serviço de interrupt acionado pelo pino INT, obtem as medidas de aceleração;

void Calib_MPU6050(); //Lê o sensor por alguns segundos e aplica calibração para remover offsets.

void Gravity_Range_Option(int AFS_SEL); //

#endif*/