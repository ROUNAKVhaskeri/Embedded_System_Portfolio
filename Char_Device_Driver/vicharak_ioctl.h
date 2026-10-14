#ifndef VICHARAK_IOCTL_H
#define VICHARAK_IOCTL_H

#include <linux/ioctl.h>

#define SET_SIZE_OF_Queue       _IOW('a', 1, int)
#define PUSH_DATA               _IOW('a', 2, struct data*)
#define POP_DATA                _IOW('a', 3, struct data*)
#define MAX_BUF 256
struct data {
    int len;
    char data[MAX_BUF];
};

#endif