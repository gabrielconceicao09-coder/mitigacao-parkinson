#include <Arduino.h>
#include <Servo.h>
#include <Wire.h>
#include <cppQueue.h>

#define SERVO_CONTROL 10
#define AFS_SEL 0 //Configuração do acelerômetro AFS_SEL (0: +/-2g; 1: +/-4g; 2: +/-8g)
#define DLPF_SEL 2 //Filtro passa-baixa DLPF_SEL (0: BW 260 Hz; 1: BW 184 Hz; 2: BW 94 Hz; 3: BW 44 Hz; 4: BW 21 Hz; 5: BW 10 Hz, 6: BW 5 Hz)

int controle_pid(float Kp, float Ki, float Kd, float Kg, float * ac_ref, float * AcZ_ms);
float zonaMorta(float sinal, float limite);
void init_MPU6050();
void Calc_Grvt(int acx, int acy, int acz, float* pAcX_ms, float* pAcY_ms, float* pAcZ_ms);
void leituraMPU_ISR();
void leituraMPU();
void Calib_MPU6050();
void Gravity_Range_Option();

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
float ac_ref = 0;
float Kp = 3;
float Ki = 1;
float Kd = 0;
float Kg = 10;

//Leitura MPU
const int MPU_ADDR = 0x68;  // Endereço I2C do MPU-6050
const float aceleracao_g = 9.81;
float Grvt_unit;  // Unidade de gravidade
float Cal_AcX;
float Cal_AcY;
float Cal_AcZ;
int acX, acY, acZ; // Variáveis para leitura da aceleração
unsigned long t_medidas;
float AcX_ms, AcY_ms, AcZ_ms;
unsigned long t_stamp;
unsigned long t0, t;

//Servomotor
Servo servomotor;
int angulo_servo = 90;

void setup() {
  Serial.begin(115200);
  Serial.println("Setup...");
  pinMode(SERVO_CONTROL, OUTPUT);
  servomotor.attach(SERVO_CONTROL, 420, 2400);
  init_MPU6050();
  Gravity_Range_Option();
  Calib_MPU6050();
  Serial.println("Setup finalizado.");
};


void loop() {
  leituraMPU();
  Calc_Grvt(acX, acY, acZ, &AcX_ms, &AcY_ms, &AcZ_ms);
  //Serial.print("AcX = "); Serial.print(AcX_ms);  Serial.print("m/s^2");
  //Serial.print(" | AcY = "); Serial.print(AcY_ms);  Serial.print("m/s^2");
  //Serial.print(" | AcZ = "); Serial.print(AcZ_ms);  Serial.println("m/s^2");
  if (Serial.available()){
    Kg = Serial.parseFloat();
  }
  angulo_servo = controle_pid(Kp, Ki, Kd, Kg, &ac_ref, &AcZ_ms);
  servomotor.write(angulo_servo);
}


//Controle PID =================================================================================
//=======================================================================================

int controle_pid(float Kp, float Ki, float Kd, float Kg, float * ac_ref, float * AcZ_ms){
    erro = *ac_ref - *AcZ_ms;
    erro = zonaMorta(erro, 0.001);
    deltaerro = erro - erro_anterior;
    erro_anterior = erro;
    t_controle = micros();
    deltat = (float) (t_controle - t_controle_anterior)/1000000.0; //segundos
    t_controle_anterior = t_controle;
    derivada = deltaerro/deltat;
    integral += erro*deltat;
    sinal_pid = Kp*erro + Ki*integral + Kd*derivada;
    Serial.print(">Erro:"); Serial.print(erro, 6); Serial.print(",Deltat:"); Serial.print(deltat, 8);
    Serial.print(",Integral:"); Serial.print(integral, 8); Serial.print(",Saida PID:"); Serial.print(sinal_pid);
    int angulo = (int) constrain(sinal_pid, -90.0, 90.0); //Saturação
    angulo *= Kg;
    angulo += 90; //offset para conformidade com biblioteca Servo do Arduino
    Serial.print(",Angulo:"); Serial.println(angulo);
    return angulo;
};

float zonaMorta(float sinal, float limite){
  if (sinal < 0){
    if (sinal >= -1*limite) return 0.0;
    else return sinal;
  }
  else {
    if (sinal <= limite) return 0.0;
    else return sinal;
  }
}


//Leitura do MPU =================================================================================
//==============================================================================================

void init_MPU6050() {
  Serial.println("Inicialização do MPU6050...");
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
  Serial.println("Inicialização do MPU6050 finalizada");
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


void leituraMPU(){
  //Serial.println("leituraMPU chamada...");
  Wire.beginTransmission(MPU_ADDR);
  Wire.write(0x3B);  // Começa no registro 0x3B (ACCEL_XOUT_H)
  Wire.endTransmission(false);
  Wire.requestFrom(MPU_ADDR, 6, true);  // Solicita 6 registros
  acX = Wire.read() << 8 | Wire.read();  // 0x3B (ACCEL_XOUT_H) & 0x3C (ACCEL_XOUT_L)
  acY = Wire.read() << 8 | Wire.read();  // 0x3D (ACCEL_YOUT_H) & 0x3E (ACCEL_YOUT_L)
  acZ = Wire.read() << 8 | Wire.read();  // 0x3F (ACCEL_ZOUT_H) & 0x40 (ACCEL_ZOUT_L)
  t_medidas = millis();
}

void Calib_MPU6050() {
  Serial.println("Iniciando calibragem...");
  int count = 0;
  for (; count < 200; count++){
    leituraMPU();
    Cal_AcX += acX;
    Cal_AcY += acY;
    Cal_AcZ += acZ;
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