/*
 * hx710b.h
 *
 *  Created on: Feb 10, 2025
 *      Author: sunbeam
 */

#ifndef INC_HX710B_H_
#define INC_HX710B_H_
#include "main.h"
#include "stm32f4xx.h"

uint32_t readHX710B(void);
uint32_t convertToPa(uint32_t adcValue);
#define fr 0.0023841859331



#endif /* INC_HX710B_H_ */
