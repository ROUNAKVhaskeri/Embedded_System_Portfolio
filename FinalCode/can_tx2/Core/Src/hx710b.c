/*
 * hx710b.c
 *
 *  Created on: Feb 10, 2025
 *      Author: sunbeam
 */


#include "hx710b.h"
//long long map_pressure_value(long adcvalue){
//
//	return (adcvalue - IN_MIN) * (OUT_MAX - OUT_MIN) / (IN_MAX - IN_MIN) + OUT_MIN;
//}

uint32_t readHX710B(void)
{
  uint32_t result = 0;

  // Wait until DOUT is low, indicating data is ready
  while (HAL_GPIO_ReadPin(GPIOD, GPIO_PIN_12) == GPIO_PIN_SET);  // DOUT is high when not ready

  // Read 24 bits of data
  for (int i = 0; i < 26; i++)
  {
    HAL_GPIO_WritePin(GPIOD, GPIO_PIN_13, GPIO_PIN_SET);  // SCK high
    result = (result << 1) | HAL_GPIO_ReadPin(GPIOD, GPIO_PIN_12);  // Shift in bit from DOUT
    HAL_GPIO_WritePin(GPIOD, GPIO_PIN_13, GPIO_PIN_RESET);  // SCK low
  }

  // Apply one more clock pulse to complete the data transfer
  HAL_GPIO_WritePin(GPIOD, GPIO_PIN_13, GPIO_PIN_SET);
  HAL_Delay(1);  // Short delay for pulse timing
  HAL_GPIO_WritePin(GPIOD, GPIO_PIN_13, GPIO_PIN_RESET);
  HAL_Delay(1);

  if (result & 0x800000)
      {
          result |= 0xFF000000;  // Correct sign extension
      }

  return result;  // Return the 24-bit pressure value
}

uint32_t convertToPa(uint32_t adcValue) {

        //return (adcValue * 40000) / 16777215;
		return  adcValue * fr;
}
