/*#pragma once
#ifndef LEITURA_MPU_H_
#define LEITURA_MPU_H_
#include <Arduino.h>
#include <Wire.h>
#include <cppQueue.h>

//Leitura do MPU
const int MPU_ADDR = 0x68;  // Endereço I2C do MPU-6050
const float aceleracao_g = 9.81;

float Grvt_unit;  // Unidade de gravidade
float Cal_AcX;
float Cal_AcY;
float Cal_AcZ;

int acX, acY, acZ; // Variáveis para leitura da aceleração
cppQueue bufferAc(sizeof(int));
unsigned long t_medidas;
cppQueue bufferT(sizeof(unsigned long));

int AcX, AcY, AcZ; //Variáveis para cálculos e transmissão
float AcX_ms, AcY_ms, AcZ_ms;
unsigned long t_stamp;

unsigned long t0, t;

void init_MPU6050(); //inicializa mpu

void Calc_Grvt(int acx, int acy, int acz, float* pAcX_ms, float* pAcY_ms, float* pAcZ_ms); //calcula gravidade em m/s^2

void leituraMPU_ISR(); //Serviço de interrupt acionado pelo pino INT

void Calib_MPU6050();

void Gravity_Range_Option();

#endif*/