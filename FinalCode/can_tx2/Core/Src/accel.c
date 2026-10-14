/*
 * accel.c
 *
 *  Created on: Dec 30, 2024
 *      Author: sunbeam
 */

#ifndef SRC_ACCEL_C_
#define SRC_ACCEL_C_

#include "accel.h"

static void SPI_Write(SPI_HandleTypeDef *hspi, GPIO_TypeDef *GPIOx, uint16_t GPIO_Pin, uint8_t reg, uint8_t *data, uint8_t size){
	HAL_GPIO_WritePin(GPIOx, GPIO_Pin, GPIO_PIN_RESET);		// CS enable
	HAL_SPI_Transmit(hspi, &reg, 1, HAL_MAX_DELAY);			// Send 1 bit reg address
	HAL_SPI_Transmit(hspi, data, size, HAL_MAX_DELAY);		// send data of size bits
	HAL_GPIO_WritePin(GPIOx, GPIO_Pin, GPIO_PIN_SET);		// disable CS
}
static void SPI_Read(SPI_HandleTypeDef *hspi, GPIO_TypeDef *GPIOx, uint16_t GPIO_Pin, uint8_t reg, uint8_t *data, uint8_t size){
	reg |= 0x80;		// Set MSB for Read operation
    HAL_GPIO_WritePin(GPIOx, GPIO_Pin, GPIO_PIN_RESET); // CS Enable
    HAL_SPI_Transmit(hspi, &reg, 1, HAL_MAX_DELAY);     // Send 1 bit Register address
    HAL_SPI_Receive(hspi, data, size, HAL_MAX_DELAY);   // Get the Data
    HAL_GPIO_WritePin(GPIOx, GPIO_Pin, GPIO_PIN_SET);   // CS disable

}
void LIS3DSH_Init(SPI_HandleTypeDef *hspi, GPIO_TypeDef *GPIOx, uint16_t GPIO_Pin){
	uint8_t config = LIS3DSH_CR4_ODR_25HZ | LIS3DSH_CR4_XEN | LIS3DSH_CR4_YEN | LIS3DSH_CR4_ZEN;
	SPI_Write(hspi, GPIOx, GPIO_Pin, LIS_Ctrl_Reg_addr, &config, 1);
}
void LIS3DSH_WaitForDataAvail(SPI_HandleTypeDef *hspi, GPIO_TypeDef *GPIOx, uint16_t GPIO_Pin){
	uint8_t status;
	while((status & LIS3DSH_SR_XYZ_MSK)==0){
		SPI_Read(hspi, GPIOx, GPIO_Pin, LIS3DSH_STATUS_REG_ADDR, &status, 1);
	}
}
void LIS3DSH_ReadDataArray(SPI_HandleTypeDef *hspi, GPIO_TypeDef *GPIOx, uint16_t GPIO_Pin, uint8_t *AxisArray){
	uint8_t buf[2];
	SPI_Read(hspi, GPIOx, GPIO_Pin, LIS3DSH_OUT_XL_ADDR, buf, 2);		// Read 2 bit data for X axis
	AxisArray[0] = buf[0];
	AxisArray[1] = buf[1];

	SPI_Read(hspi, GPIOx, GPIO_Pin, LIS3DSH_OUT_YL_ADDR, buf, 2);		// Read 2 bit data for y axis
	AxisArray[2] = buf[0];
	AxisArray[3] = buf[1];

	SPI_Read(hspi, GPIOx, GPIO_Pin, LIS3DSH_OUT_ZL_ADDR, buf, 2);		// Read 2 bit data for z axis
	AxisArray[4] = buf[0];
	AxisArray[5] = buf[1];

}


#endif /* SRC_ACCEL_C_ */
