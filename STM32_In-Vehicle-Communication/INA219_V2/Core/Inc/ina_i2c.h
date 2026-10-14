	/*
	 * ina_i2c.h
	 *
	 *  Created on: Feb 2, 2025
	 *      Author: ROUNAK
	 */

	#ifndef INC_INA_I2C_H_
	#define INC_INA_I2C_H_

	#include "stm32f4xx_hal.h"

	extern I2C_HandleTypeDef hi2c1;

	uint16_t INA219_ReadReg(I2C_HandleTypeDef *hi2c1, uint8_t reg);
	HAL_StatusTypeDef INA219_WriteReg(I2C_HandleTypeDef *hi2c1, uint8_t reg, uint16_t data);


	#endif /* INC_INA_I2C_H_ */
