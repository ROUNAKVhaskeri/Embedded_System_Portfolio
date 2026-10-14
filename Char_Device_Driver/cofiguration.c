#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include "vicharak_ioctl.h"

#define DRIVER "/dev/vicharak"

typedef enum {
    SET_QUEUE_SIZE = 1,
    Push_Data,
    EXIT
} config_cmd_t;

void set_queue_size(int fd) {
    int size;
    printf("Enter the Queue Size to set: ");
    if (scanf("%d", &size) != 1 || size <= 0) {
        printf("Invalid Input!\n");
        return;
    }

    if (ioctl(fd, SET_SIZE_OF_Queue, &size) < 0) {
        perror("IOCTL for SET_SIZE failed");
    } else {
        printf("Queue Size is Set to %d\n", size);
    }
}

int main() {
    int fd = open(DRIVER, O_RDWR);
    if (fd < 0) {
        perror("Open Failed");
        return -1;
    }
   
    set_queue_size(fd);
    close(fd);
    return 0;
}
