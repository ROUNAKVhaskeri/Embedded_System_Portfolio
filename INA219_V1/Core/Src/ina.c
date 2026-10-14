/*
 * ina.c
 *
 *  Created on: Feb 2, 2025
 *      Author: ROUNAK
 */

#include "ina.h"
#include "stm32f4xx_hal.h"
#include "ina_i2c.h"


/* Initialize the INA219 sensor */

HAL_StatusTypeDef INA219_init(I2C_HandleTypeDef *hi2c1) {
    uint16_t config = INA219_CONFIG_RESET | INA219_CONFIG_BUSVTGRNG_16V |
                      INA219_CONFIG_GAIN_1_40mV | INA219_CONFIG_MODE_SANDBVOLT_CONT;
    return INA219_WriteReg(hi2c1, INA219_REG_CONFIG, config);
}

/* Get Bus Voltage */
float INA219_GetBusVoltage(I2C_HandleTypeDef *hi2c1) {

    uint16_t raw_data = INA219_ReadReg(hi2c1, INA219_REG_BUSVTG);

    return raw_data * 0.004;  // Conversion factor for Bus Voltage
}

/* Get Shunt Voltage */
float INA219_GetShuntVoltage(I2C_HandleTypeDef *hi2c1) {
//	UART_HandleTypeDef huart2;
    uint16_t raw_data = INA219_ReadReg(hi2c1, INA219_REG_SHUNTVTG);
    return raw_data * 0.00001;  // Conversion factor for Shunt Voltage
}

/* Get Current */
float INA219_GetCurrent(I2C_HandleTypeDef *hi2c1) {
    uint16_t raw_data = INA219_ReadReg(hi2c1, INA219_REG_CURRENT);
    return raw_data * 0.001;  // Conversion factor for Current
}
