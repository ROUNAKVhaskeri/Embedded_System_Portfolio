#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include "vicharak_ioctl.h"

#define DRIVER "/dev/vicharak"

void pop_data(int fd){
    struct data user_data;
    user_data.len = MAX_BUF;

    if(ioctl(fd, POP_DATA, &user_data)<0)
    {
        perror("IOCTL Failed for POP_DATA\n");
    }
    else{
        printf("Data Popped Sucessfully : %s\n",user_data.data);
    }
}

int main(){
    int fd = open(DRIVER,O_RDWR);
    if(fd<0){
        perror("Error Openning the File\n");
        return -1;
    }

    pop_data(fd);

    close(fd);
    return 0;
}