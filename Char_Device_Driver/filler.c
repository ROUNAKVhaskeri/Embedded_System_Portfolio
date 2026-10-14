#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include "vicharak_ioctl.h"

#define DRIVER "/dev/vicharak"


void Push_data(int fd){
    struct data user_data;

    printf("Enter Data to Push : ");
    if(scanf("%31s",user_data.data)!=1){
        printf("Invalid Input!\n");
        return;
    }

    if(ioctl(fd, PUSH_DATA,&user_data)<0){
        perror("IOCTL for PUSH Data Failed\n");
    }
    else{
        printf("Data Pushed Sucessfully!\n");
    }
}


int main(){
    int fd = open(DRIVER, O_RDWR);
    if (fd < 0) {
        perror("Open Failed");
        return -1;
    }

    Push_data(fd);
    close(fd);
    return 0;
}