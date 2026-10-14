/*
 * ina.c
 *
 *  Created on: Feb 2, 2025
 *      Author: ROUNAK
 */

#include "ina.h"
#include "stm32f4xx_hal.h"
#include "ina_i2c.h"

uint16_t currentDevider = 10;  //Current LSB = 100uA per bit (1000/100 = 10)


/* Initialize the INA219 sensor */
void INA219_Calibrate(I2C_HandleTypeDef *hi2c1, uint16_t CalValue){
	INA219_WriteReg(hi2c1, INA219_REG_CALIBRATION, CalValue);
}

HAL_StatusTypeDef INA219_init(I2C_HandleTypeDef *hi2c1) {
    HAL_StatusTypeDef status = INA219_WriteReg(hi2c1, INA219_REG_CONFIG, INA219_CONFIG_RESET);
    if (status != HAL_OK) {
    	return status; // Return if reset fails
    }
    HAL_Delay(10);

    uint16_t config = (INA219_CONFIG_BUSVTGRNG_16V | INA219_CONFIG_GAIN_8_320mV | INA219_config_BADCRES_12BIT_1060us| INA219_CONFIG_MODE_SANDBVOLT_CONT);
    return INA219_WriteReg(hi2c1, INA219_REG_CONFIG, config);
}

/* Get Bus Voltage */
float INA219_GetBusVoltage(I2C_HandleTypeDef *hi2c1) {

	uint16_t raw_data = INA219_ReadReg(hi2c1, INA219_REG_BUSVTG);

    return (raw_data >> 3)*0.004;  // Conversion factor for Bus Voltage
}

/* Get Shunt Voltage */
float INA219_GetShuntVoltage(I2C_HandleTypeDef *hi2c1) {
//	UART_HandleTypeDef huart2;
    int16_t raw_data = (int16_t)INA219_ReadReg(hi2c1, INA219_REG_SHUNTVTG);
    return raw_data * 0.01;  // Conversion factor for Shunt Voltage
}

/* Get Current */
float INA219_GetCurrent(I2C_HandleTypeDef *hi2c1) {

	int16_t RawCurrent = (int16_t)INA219_ReadReg(hi2c1, INA219_REG_CURRENT);
	float current = (float)RawCurrent/currentDevider;
    return current;
}
