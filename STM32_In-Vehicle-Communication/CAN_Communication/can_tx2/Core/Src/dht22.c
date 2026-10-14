/*
 * dht22.c
 *
 *  Created on: Dec 30, 2024
 *      Author: sunbeam
 */

#include "dht22.h"

void delay_us(uint16_t us) {
    __HAL_TIM_SET_COUNTER(&htim6, 0);
    while (__HAL_TIM_GET_COUNTER(&htim6) < us);
}


void Start_Signal(void) {
    GPIO_InitTypeDef GPIO_InitStruct = {0};

    // Configure PA1 as output (using HAL for initial setup)
    GPIO_InitStruct.Pin = DHT22_Pin;
    GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
    GPIO_InitStruct.Pull = GPIO_NOPULL;
    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
    HAL_GPIO_Init(DHT22_GPIO_Port, &GPIO_InitStruct);

    HAL_GPIO_WritePin(DHT22_GPIO_Port, DHT22_Pin, GPIO_PIN_RESET);
    HAL_Delay(18);
    HAL_GPIO_WritePin(DHT22_GPIO_Port, DHT22_Pin, GPIO_PIN_SET);
    delay_us(30);

    // Configure PA1 as input (using HAL)
    GPIO_InitStruct.Mode = GPIO_MODE_INPUT;
    GPIO_InitStruct.Pull = GPIO_PULLUP;

    HAL_GPIO_Init(DHT22_GPIO_Port, &GPIO_InitStruct);
    delay_us(5); // Important delay after mode change
}



uint8_t check_response(void) {
    __HAL_TIM_SET_COUNTER(&htim6, 0);
    while (!(DHT22_PORT->IDR & (1 << DHT22_PIN_NUMBER)) && __HAL_TIM_GET_COUNTER(&htim6) < 100);
    if (__HAL_TIM_GET_COUNTER(&htim6) >= 100) return 0;

    __HAL_TIM_SET_COUNTER(&htim6, 0);
    while ((DHT22_PORT->IDR & (1 << DHT22_PIN_NUMBER)) && __HAL_TIM_GET_COUNTER(&htim6) < 100);
    if (__HAL_TIM_GET_COUNTER(&htim6) >= 100) return 0;

    return 1;
}


uint8_t read_byte(void) {
    uint8_t num = 0;
    for (int i = 0; i < 8; i++) {
        while (!(DHT22_PORT->IDR & (1 << DHT22_PIN_NUMBER))); // Wait for HIGH
        __HAL_TIM_SET_COUNTER(&htim6, 0);
        while ((DHT22_PORT->IDR & (1 << DHT22_PIN_NUMBER)) && __HAL_TIM_GET_COUNTER(&htim6) < 100);
        if (__HAL_TIM_GET_COUNTER(&htim6) > 40) {
            num |= (1 << (7 - i));
        }
        delay_us(5);
    }
    return num;
}



void send_uart(char *str) {
    HAL_UART_Transmit(&huart2, (uint8_t *)str, strlen(str), HAL_MAX_DELAY);
}
