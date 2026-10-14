/*
 * ina219.h
 *
 *  Created on: Feb 9, 2025
 *      Author: ROUNAK
 */

#ifndef INA219_H_
#define INA219_H_

#include "stm32f4xx_hal.h"
#include <stdio.h>
#include <string.h>



#define INA219_I2C_ADDRESS          		(0x40)    // INA219 I2C slave Address

#define INA219_REG_CONFIG           		0x00    // Config register
#define INA219_REG_SHUNTVTG         		0x01    // Shunt voltage register
#define INA219_REG_BUSVTG           		0x02    // Bus voltage register
#define INA219_REG_POWER            		0x03    // Power register
#define INA219_REG_CURRENT          		0x04    // Current register
#define INA219_REG_CALIBRATION				0x05	// calibration register

#define INA219_CONFIG_RESET         		0x8000
#define INA219_CONFIG_BUSVTGRNG_16V 		0x0000
#define INA219_CONFIG_BUSVTGRNG_32V 		0x2000
#define INA219_CONFIG_GAIN_1_40mV   		0x0000
#define INA219_CONFIG_GAIN_8_320mV			0x1800
#define INA219_CONFIG_MODE_SANDBVOLT_CONT 	0x07
#define INA219_config_BADCRES_12BIT_1060us	0x0400


extern I2C_HandleTypeDef hi2c1;


void INA219_Calibrate(I2C_HandleTypeDef *hi2c1, uint16_t CalValue);
HAL_StatusTypeDef INA219_init(I2C_HandleTypeDef *hi2c1);
float INA219_GetBusVoltage(I2C_HandleTypeDef *hi2c1);
float INA219_GetShuntVoltage(I2C_HandleTypeDef *hi2c1);
float INA219_GetCurrent(I2C_HandleTypeDef *hi2c1);
uint16_t INA219_ReadReg(I2C_HandleTypeDef *hi2c1, uint8_t reg);
HAL_StatusTypeDef INA219_WriteReg(I2C_HandleTypeDef *hi2c1, uint8_t reg, uint16_t data);


#endif /* INA219_H_ */
