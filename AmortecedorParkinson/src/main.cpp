#include <Arduino.h>
#include <Servo.h>
#include "leitura_mpu.h"
#include <Wire.h>
#include <cppQueue.h>

#define MPU_INT_PIN 3
#define SERVO_CONTROL 10

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

int controle_pid(float Kp, float Ki, float Kd, float * ac_ref, float * AcZ_ms){
    erro = *ac_ref - *AcZ_ms;
    deltaerro = erro - erro_anterior;
    erro_anterior = erro;
    t_controle = micros();
    deltat = (float) (t_controle - t_controle_anterior)/1000000.0; //segundos
    t_controle_anterior = t_controle;
    derivada = deltaerro/deltat;
    integral += erro*deltat;
    sinal_pid = Kp*erro + Ki*integral + Kd*derivada;
    int angulo = (int) constrain(sinal_pid, -90.0, 90.0); //Saturação
    angulo += 90; //offset para conformidade com biblioteca Servo do Arduino
    return angulo;
};


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

#define AFS_SEL 0  // Configuração do acelerômetro (+/-2g)
#define DLPF_SEL 2 // Filtro passa-baixa (2: BW 94 Hz; 3: BW 44 Hz)


void init_MPU6050() {
  // Inicialização e reset do MPU6050
  Wire.beginTransmission(MPU_ADDR);
  Wire.write(0x6B);  // PWR_MGMT_1 register
  Wire.write(0);     // Acorda o MPU-6050
  Wire.endTransmission(true);

  // Configuração do clock
  Wire.beginTransmission(MPU_ADDR);
  Wire.write(0x6B);
  Wire.write(0x03);  // Seleciona clock 'PLL com referência do giroscópio Z'
  Wire.endTransmission(true);

  // Configuração do acelerômetro
  Wire.beginTransmission(MPU_ADDR);
  Wire.write(0x1C);  // Registro de configuração do acelerômetro
  if (AFS_SEL == 0) Wire.write(0x00);  // +/-2g
  else if (AFS_SEL == 1) Wire.write(0x08);  // +/-4g
  else if (AFS_SEL == 2) Wire.write(0x10);  // +/-8g
  else Wire.write(0x18);  // +/-16g
  Wire.endTransmission(true);

  // Configuração do filtro digital (DLPF)
  Wire.beginTransmission(MPU_ADDR);
  Wire.write(0x1A);  // Registro DLPF_CFG
  if (DLPF_SEL == 0) Wire.write(0x00);  // BW 260Hz
  else if (DLPF_SEL == 1) Wire.write(0x01);  // BW 184Hz
  else if (DLPF_SEL == 2) Wire.write(0x02);  // BW 94Hz
  else if (DLPF_SEL == 3) Wire.write(0x03);  // BW 44Hz
  else if (DLPF_SEL == 4) Wire.write(0x04);  // BW 21Hz
  else if (DLPF_SEL == 5) Wire.write(0x05);  // BW 10Hz
  else Wire.write(0x06);  // BW 5Hz
  Wire.endTransmission(true);

  //Configuração do pino de interrupt INT
  Wire.beginTransmission(MPU_ADDR);
  Wire.write(0x37); //Registrador INT_PIN_CFG
  Wire.write(0x10); // Configura bit INT_RD_CLEAR para 1, liberando o interrupt em qualquer operação de leitura
  Wire.endTransmission(true);

  //Configuração dos eventos de interrupt para que ele sinalize sempre que as medidas estiverem prontas
  Wire.beginTransmission(MPU_ADDR);
  Wire.write(0x38); // Registrador INT_ENABLE
  Wire.write(0x01); // Configura bit DATA_RDY_EN para 1. INT gera um pulso quando uma rodada de medidas está pronta
  Wire.endTransmission(true);
}

void Calc_Grvt(int acx, int acy, int acz, float* pAcX_ms, float* pAcY_ms, float* pAcZ_ms) {
  // Aplica calibração
  acx = (acx - Cal_AcX);
  acy = (acy - Cal_AcY);
  acz = (acz - Cal_AcZ);
      
  // Converte para valores de gravidade
  float GAcX = acx / Grvt_unit ;
  float GAcY = acy / Grvt_unit ;
  float GAcZ = acz / Grvt_unit ;

  // Calculo das acelerações em m/s^2
  *pAcX_ms = GAcX*aceleracao_g;
  *pAcY_ms = GAcY*aceleracao_g;
  *pAcZ_ms = GAcZ*aceleracao_g;

  // Calculo da aceleração resultante m/s^2
  //Ares = sqrt(pow(AcX_ms, 2) + pow(AcY_ms, 2) + pow(AcZ_ms, 2));

  return;
}

void leituraMPU_ISR(){ //Serviço de interrupt acionado pelo pino INT
  Wire.beginTransmission(MPU_ADDR);
  Wire.write(0x3B);  // Começa no registro 0x3B (ACCEL_XOUT_H)
  Wire.endTransmission(false);
  Wire.requestFrom(MPU_ADDR, 6, true);  // Solicita 6 registros
  acX = Wire.read() << 8 | Wire.read();  // 0x3B (ACCEL_XOUT_H) & 0x3C (ACCEL_XOUT_L)
  acY = Wire.read() << 8 | Wire.read();  // 0x3D (ACCEL_YOUT_H) & 0x3E (ACCEL_YOUT_L)
  acZ = Wire.read() << 8 | Wire.read();  // 0x3F (ACCEL_ZOUT_H) & 0x40 (ACCEL_ZOUT_L)
  t_medidas = millis();
  bufferAc.push(&acX); bufferAc.push(&acY); bufferAc.push(&acZ);
  bufferT.push(&t_medidas);
}

void Calib_MPU6050() {
  Serial.println("Iniciando calibragem...");
  int count = 0;
  for (; t-t0 < 2000; t = millis()){
    if (bufferAc.getCount() >= 3 && bufferT.getCount() >= 1){
      noInterrupts();
      bufferAc.pop(&AcX);
      bufferAc.pop(&AcY);
      bufferAc.pop(&AcZ);
      bufferT.pop(&t_stamp);
      interrupts();
      Cal_AcX += AcX;
      Cal_AcY += AcY;
      Cal_AcZ += AcZ;
      count ++;
    }
  }
  // Calcula médias de calibração
  Cal_AcX /= count;
  Cal_AcY /= count;
  Cal_AcZ /= count;

  Serial.print("Cal_AcX = "); Serial.print(Cal_AcX);
  Serial.print(" | Cal_AcY = "); Serial.print(Cal_AcY);
  Serial.print(" | Cal_AcZ = "); Serial.println(Cal_AcZ); 
}


void Gravity_Range_Option() {
  switch (AFS_SEL) {  // Seleciona unidade de gravidade (LSB/g)
    case 0:
      Grvt_unit = 16384;
      break;
    case 1:
      Grvt_unit = 8192;
      break;
    case 2:
      Grvt_unit = 4096;
      break;
    case 3:
      Grvt_unit = 2048;
      break;
  }
}

Servo servomotor;

void setup() {
  Serial.begin(115200);
  pinMode(MPU_INT_PIN, INPUT);
  pinMode(SERVO_CONTROL, OUTPUT);
  servomotor.attach(10, 1000, 2000); //Largura para posição 0 graus 1ms posição 180 graus 2ms
  init_MPU6050();
  attachInterrupt(digitalPinToInterrupt(MPU_INT_PIN), leituraMPU_ISR, RISING);
  Gravity_Range_Option();
  Calib_MPU6050();
};

int angulo_servo = 90;
float ac_ref = 0;
const float Kp = 1;
const float Ki = 1;
const float Kd = 0;

void loop() {
  if (bufferAc.getCount() > 3 && bufferT.getCount() > 1){ //Controle atualiza somente quando há medidas nos buffers
    noInterrupts();
    bufferAc.pop(&AcX);
    bufferAc.pop(&AcY);
    bufferAc.pop(&AcZ);
    bufferT.pop(&t_stamp);
    interrupts();
    Calc_Grvt(AcX, AcY, AcZ, &AcZ_ms, &AcZ_ms, &AcZ_ms);
    Serial.print("AcX = "); Serial.print(AcX_ms);  Serial.print("m/s^2");
    Serial.print(" | AcY = "); Serial.print(AcY_ms);  Serial.print("m/s^2");
    Serial.print(" | AcZ = "); Serial.print(AcZ_ms);  Serial.println("m/s^2");
    angulo_servo = controle_pid(Kp, Ki, Kd, &ac_ref, &AcZ_ms);
    servomotor.write(angulo_servo);
  }
}