/*
 * accel.h
 *
 *  Created on: Dec 30, 2024
 *      Author: sunbeam
 */

#ifndef INC_ACCEL_H_
#define INC_ACCEL_H_

#include "stm32f4xx_hal.h"

#define LIS_Ctrl_Reg_addr		0x20
#define LIS3DSH_STATUS_REG_ADDR      0x27
#define LIS3DSH_OUT_XL_ADDR          0x28
#define LIS3DSH_OUT_YL_ADDR          0x2A
#define LIS3DSH_OUT_ZL_ADDR          0x2C

#define LIS3DSH_CR4_ODR_OFF          (0x00 << 4)
#define LIS3DSH_CR4_ODR_25HZ         (0x04 << 4)
#define LIS3DSH_CR4_XEN              (1 << 0)
#define LIS3DSH_CR4_YEN              (1 << 1)
#define LIS3DSH_CR4_ZEN              (1 << 2)

#define LIS3DSH_SR_XDA               (1 << 0)
#define LIS3DSH_SR_YDA               (1 << 1)
#define LIS3DSH_SR_ZDA               (1 << 2)
#define LIS3DSH_SR_ZYXDA             (1 << 3)
#define LIS3DSH_SR_XYZ_MSK           (LIS3DSH_SR_XDA | LIS3DSH_SR_YDA | LIS3DSH_SR_ZDA)


void LIS3DSH_Init(SPI_HandleTypeDef *hspi, GPIO_TypeDef *GPIOx, uint16_t GPIO_Pin);
void LIS3DSH_WaitForDataAvail(SPI_HandleTypeDef *hspi, GPIO_TypeDef *GPIOx, uint16_t GPIO_Pin);
void LIS3DSH_ReadDataArray(SPI_HandleTypeDef *hspi, GPIO_TypeDef *GPIOx, uint16_t GPIO_Pin, uint8_t *dataArray);


#endif /* INC_ACCEL_H_ */
