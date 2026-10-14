/*
 * dht22.h
 *
 *  Created on: Dec 30, 2024
 *      Author: sunbeam
 */

#ifndef INC_DHT22_H_
#define INC_DHT22_H_

#include <stdint.h>
#include "main.h"
#include "stm32f4xx.h"
#include <string.h>

#define DHT22_Pin GPIO_PIN_1
#define DHT22_GPIO_Port GPIOA

extern TIM_HandleTypeDef htim6;
extern UART_HandleTypeDef huart2;

void delay_us(uint16_t);
void Start_Signal(void);
uint8_t check_response(void);
uint8_t read_byte(void);



#endif /* INC_DHT22_H_ */
