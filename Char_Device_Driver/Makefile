obj-m = vicharak.o

vicharak.ko: vicharak.c
	make -C /lib/modules/$(shell uname -r)/build M=$(shell pwd) modules

clean:
	make -C /lib/modules/$(shell uname -r)/build M=$(shell pwd) clean

load:
	sudo insmod vicharak.ko

unload:
	sudo rmmod vicharak

.PHONY: clean load unload
