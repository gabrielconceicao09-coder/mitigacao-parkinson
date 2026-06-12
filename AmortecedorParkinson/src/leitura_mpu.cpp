/*#include <Arduino.h>
#include "leitura_mpu.h"

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
*/