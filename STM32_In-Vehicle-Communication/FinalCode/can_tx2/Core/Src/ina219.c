/*
 * ina219.c
 *
 *  Created on: Feb 9, 2025
 *      Author: ROUNAK
 */


#include "ina219.h"

float currentDevider = 11.12;
void INA219_Calibrate(I2C_HandleTypeDef *hi2c1, uint16_t CalValue){
	INA219_WriteReg(hi2c1, INA219_REG_CALIBRATION, CalValue);
}

HAL_StatusTypeDef INA219_init(I2C_HandleTypeDef *hi2c1){
	int status;
	if ((status = INA219_WriteReg(hi2c1, INA219_REG_CONFIG, INA219_CONFIG_RESET)) != HAL_OK) {
    	return status;
    }
    HAL_Delay(5);

    uint16_t config = (INA219_CONFIG_BUSVTGRNG_32V | INA219_CONFIG_GAIN_1_40mV | INA219_config_BADCRES_12BIT_1060us| INA219_CONFIG_MODE_SANDBVOLT_CONT);
    return INA219_WriteReg(hi2c1, INA219_REG_CONFIG, config);
}

float INA219_GetBusVoltage(I2C_HandleTypeDef *hi2c1){
	uint16_t raw_data = INA219_ReadReg(hi2c1, INA219_REG_BUSVTG);
    return (raw_data >> 3)*0.004;  // Conversion factor for Bus Voltage
}

float INA219_GetShuntVoltage(I2C_HandleTypeDef *hi2c1){
	int16_t raw_data = (int16_t)INA219_ReadReg(hi2c1, INA219_REG_SHUNTVTG);
	return (float)raw_data * 0.00001;  // Conversion factor for Shunt Voltage
}

float INA219_GetCurrent(I2C_HandleTypeDef *hi2c1){
	int16_t RawCurrent = (int16_t)INA219_ReadReg(hi2c1, INA219_REG_CURRENT);
	float current = (float)RawCurrent/currentDevider;
	return current;
}

uint16_t INA219_ReadReg(I2C_HandleTypeDef *hi2c1, uint8_t reg){
	 uint8_t rx_data[2];
	 HAL_I2C_Mem_Read(hi2c1, INA219_I2C_ADDRESS<<1 , reg, 1, rx_data, 2, HAL_MAX_DELAY);
	 return (rx_data[0] << 8) | rx_data[1];
}

HAL_StatusTypeDef INA219_WriteReg(I2C_HandleTypeDef *hi2c1, uint8_t reg, uint16_t data){
	uint8_t tx_data[2];
	tx_data[0] = (data >> 8) & 0xFF;
	tx_data[1] = data & 0xFF;
	return HAL_I2C_Mem_Write(hi2c1, INA219_I2C_ADDRESS << 1, reg, 1, tx_data, 2, 1000);
}
