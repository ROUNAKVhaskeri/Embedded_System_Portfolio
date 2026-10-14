/*
 * ina_i2c.c
 *
 *  Created on: Feb 2, 2025
 *      Author: ROUNAK
 */



#include "ina_i2c.h"
#include "ina.h"

uint16_t INA219_ReadReg(I2C_HandleTypeDef *hi2c1, uint8_t reg){
    uint8_t rx_data[2];
    HAL_I2C_Mem_Read(hi2c1, INA219_I2C_ADDRESS << 1, reg, 1, rx_data, 2, 1000);
    return (rx_data[0] << 8) | rx_data[1];  // Combine MSB and LSB
}

HAL_StatusTypeDef INA219_WriteReg(I2C_HandleTypeDef *hi2c1, uint8_t reg, uint16_t data){
    uint8_t tx_data[2];
    tx_data[0] = (data >> 8) & 0xFF;
    tx_data[1] = data & 0xFF;
    return HAL_I2C_Mem_Write(hi2c1, INA219_I2C_ADDRESS << 1, reg, 1, tx_data, 2, 1000);
}
