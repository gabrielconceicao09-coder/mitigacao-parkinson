#include<Wire.h>
#include<arduinoFFT.h>
#include<MX1508.h>

// Envia Período de amostragem, Acc_msX, Acc_msY, Acc_msZ por comunicação serial, formato pro PGraphics_alterado.

void init_MPU6050();
void Gravity_Range_Option();
void Calib_MPU6050();
void ReadData_MPU6050();
void Calc_Grvt();
void PrintData_Python();
void PrintData_Serial();

const int MPU_ADDR = 0x68;  // Endereço I2C do MPU-6050
int AcX, AcY, AcZ;          // Valores do acelerômetro
int Acavg;                  // Média do acelerômetro

long Cal_AcX = 0, Cal_AcY = 0, Cal_AcZ = 0, Cal_AcRes;  // Valores de calibração

float GAcX, GAcY, GAcZ, GAcRes, AcX_ms, AcY_ms, AcZ_ms, Ares;  // Valores convertidos para gravidade

const float aceleracao_g = 9.81;

float Grvt_unit;  // Unidade de gravidade

#define AFS_SEL 0  // Configuração do acelerômetro (+/-2g)
#define DLPF_SEL 2 // Filtro passa-baixa (2: BW 94 Hz; 3: BW 44 Hz)

const unsigned long duration = 10000; //duração de aquisição de dados em milisegundos
const int delaytime = 5;
const float t_s = (float)delaytime;

//Pinos para controle dos motores
#define MOTOR_OUT_A 3
#define MOTOR_OUT_B 5 //PWM do arduino uno

void setup()
{
  Serial.begin(115200); // Iniciando objeto serial com parâmetro de taxa de transmissão
  init_MPU6050();
  Gravity_Range_Option();
  Calib_MPU6050();

  MX1508 motorDC(MOTOR_OUT_A, MOTOR_OUT_B, SLOW_DECAY, 2);
  
  //Recebe nível PWM por comunicação serial
  int pwm = -300;
  int received_pwm = 0;
  Serial.println(F("Ready to receive PWM level"));
  while (pwm <-200){
    if (Serial.available()){
      received_pwm = (int)Serial.parseInt();
    }
    if(received_pwm !=0){
      pwm = received_pwm;
      }
  }
  
  motorDC.motorGo(pwm);

  Serial.print(F("PWM:")); Serial.println(pwm);

  unsigned long t0 = millis(); //setup dos tempos de referência
  unsigned long t_atual = millis();

  Serial.println(F("START!"));
  Serial.print(F("INTERVAL:")); Serial.println(delaytime); //Comunica o tempo de amostragem em ms
  
  while (t_atual-t0 < duration){ //Código vai correr durante duração
    ReadData_MPU6050();
    Calc_Grvt();
    
    PrintData_Python(AcX_ms, AcY_ms, AcZ_ms, Ares, 1);

    delay(delaytime);
    t_atual = millis();
  }
  Serial.println(F("END!"));
  motorDC.stopMotor();
}

void loop(){
}


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
}


void Calib_MPU6050() {
  Serial.println("Iniciando calibragem...");
  for (int i = 0; i < 200; i++) {  // Iteração para cálculo de calibração
    ReadData_MPU6050(); 
    delay(10);
    // Soma os dados para calibração
    Cal_AcX += AcX;
    Cal_AcY += AcY;
    Cal_AcZ += AcZ;
  }

  // Calcula médias de calibração
  Cal_AcX /= 200;
  Cal_AcY /= 200;
  Cal_AcZ /= 200;

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

void ReadData_MPU6050() {
  Wire.beginTransmission(MPU_ADDR);
  Wire.write(0x3B);  // Começa no registro 0x3B (ACCEL_XOUT_H)
  Wire.endTransmission(false);
  Wire.requestFrom(MPU_ADDR, 6, true);  // Solicita 6 registros
  AcX = Wire.read() << 8 | Wire.read();  // 0x3B (ACCEL_XOUT_H) & 0x3C (ACCEL_XOUT_L)
  AcY = Wire.read() << 8 | Wire.read();  // 0x3D (ACCEL_YOUT_H) & 0x3E (ACCEL_YOUT_L)
  AcZ = Wire.read() << 8 | Wire.read();  // 0x3F (ACCEL_ZOUT_H) & 0x40 (ACCEL_ZOUT_L)
}

void Calc_Grvt() {
  // Aplica calibração
  AcX = (AcX - Cal_AcX);
  AcY = (AcY - Cal_AcY);
  AcZ = (AcZ - Cal_AcZ);
      
  // Converte para valores de gravidade
  GAcX = AcX / Grvt_unit ;
  GAcY = AcY / Grvt_unit ;
  GAcZ = AcZ / Grvt_unit ;
  
  // Calculo das acelerações em m/s^2
  AcX_ms = GAcX*aceleracao_g;
  AcY_ms = GAcY*aceleracao_g;
  AcZ_ms = GAcZ*aceleracao_g;

  // Calculo da aceleração resultante m/s^2
  Ares = sqrt(pow(AcX_ms, 2) + pow(AcY_ms, 2) + pow(AcZ_ms, 2));
}

void PrintData_Serial(float acxms, float acyms, float aczms, float gacx, float gacy, float gacz, float ares){
  //Imprime no monitor serial os valores de aceleração em termos de g
  Serial.print("GAcX = "); Serial.print(gacx,2); Serial.print("g");
  Serial.print(" | GAcY = "); Serial.print(gacy,2); Serial.print("g");
  Serial.print(" | GAcZ = "); Serial.print(gacz,2); Serial.println("g");

  //Imprime no monitor serial os valores de aceleração em m/s^2
  Serial.print("AcX = "); Serial.print(acxms);  Serial.print("m/s^2");
  Serial.print(" | AcY = "); Serial.print(acyms);  Serial.print("m/s^2");
  Serial.print(" | AcZ = "); Serial.print(aczms);  Serial.println("m/s^2");
}

void PrintData_Python(float acxms, float acyms, float aczms, float ares, int mode){
  // Modo 0 é só Ares, Modo 1 é as 3 acelerações ms2
  if (mode == 0){
    Serial.println(ares);
  }
  else if (mode == 1){
    Serial.print(acxms); Serial.print(","); 
    Serial.print(acyms); Serial.print(",");
    Serial.println(aczms);
  }
}