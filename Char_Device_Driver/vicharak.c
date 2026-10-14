#include <linux/module.h>
#include <linux/fs.h>
#include <linux/device.h>
#include <linux/cdev.h>
#include <linux/kfifo.h>
#include <linux/uaccess.h>
#include <linux/slab.h>
#include <linux/mutex.h>
#include <linux/wait.h>
#include "vicharak_ioctl.h"

#define MAX 32
static struct kfifo my_fifo;
static char *queue_Buf = NULL;
static int Queue_size = MAX;

static dev_t dev_no;
static struct class *vicharak_class;
static struct cdev vicharak_cdev;

static DEFINE_MUTEX(queue_lock);
static DECLARE_WAIT_QUEUE_HEAD(queue_wait);

static int vicharak_open(struct inode *pinode, struct file *pfile) {
    pr_info("vicharak: Device opened\n");
    return 0;
}

static int vicharak_close(struct inode *pinode, struct file *pfile) {
    pr_info("vicharak: Device closed\n");
    return 0;
}

static long vicharak_ioctl(struct file *pfile, unsigned int cmd, unsigned long arg) {
    int size;
    struct data user_data;

    switch (cmd) {
        case SET_SIZE_OF_Queue:
            if(copy_from_user(&size, (void __user *)arg, sizeof(int))){
                return -EFAULT;
            }

            if(size <= 0){
                pr_err("Invalid Queue Size!\n");
                return -EINVAL;
            }

            mutex_lock(&queue_lock);
            
            kfifo_free(&my_fifo);
            kfree(queue_Buf);

            queue_Buf = kmalloc(size, GFP_KERNEL);
            if(!queue_Buf){
                mutex_unlock(&queue_lock);
                pr_err("Memory Allocation Failed!\n");
                return -ENOMEM;
            }

            Queue_size = size;
            kfifo_init(&my_fifo, queue_Buf, Queue_size);

            mutex_unlock(&queue_lock);

            pr_info("Queue Size Changed!\n");
            break;

        case PUSH_DATA:
            if (copy_from_user(&user_data, (struct data __user *)arg, sizeof(struct data)))
                return -EFAULT;

            if (kfifo_avail(&my_fifo) < user_data.len) {
                mutex_unlock(&queue_lock);
                pr_err("Queue Full! Cannot Push Data.\n");
                return -ENOSPC;
            }

            kfifo_in(&my_fifo, user_data.data, user_data.len);

            wake_up_interruptible(&queue_wait);
            
            pr_info("Data Pushed: %s\n", user_data.data);
            break;
        
        case POP_DATA:

            int out;

            if(copy_from_user(&user_data, (struct data __user *)arg, sizeof(struct data))){
                return -EFAULT;
            }

            wait_event_interruptible(queue_wait, !kfifo_is_empty(&my_fifo));
            
            out = kfifo_out(&my_fifo, user_data.data, user_data.len);
            
            if(out<= 0){
                pr_err("Queue is Empty!\n");
                return out;
            }

            if(copy_to_user((struct data __user *)arg, &user_data, sizeof(struct data)))
                return -EFAULT;

            pr_info("Data popped Sucessfully : %s\n",user_data.data);
            return 0;

        default:
            return -EINVAL;
    }
    return 0;
}

static struct file_operations fops = {
    .owner = THIS_MODULE,
    .open = vicharak_open,
    .release = vicharak_close,
    .unlocked_ioctl = vicharak_ioctl
};

static int __init vicharak_init(void) {
    int ret;
    struct device *pdev;

    // Allocate Char device in kernel
    ret = alloc_chrdev_region(&dev_no, 0, 1, "vicharak");
    if (ret) {
        pr_err("Device number allocation failed!\n");
        return ret;
    }

    // Create Device class
    vicharak_class = class_create("vicharak_class");
    if (IS_ERR(vicharak_class)) {
        unregister_chrdev_region(dev_no, 1);
        return PTR_ERR(vicharak_class);
    }

    // Create Device in kernel
    pdev = device_create(vicharak_class, NULL, dev_no, NULL, "vicharak");
    if (IS_ERR(pdev)) {
        class_destroy(vicharak_class);
        unregister_chrdev_region(dev_no, 1);
        return -1;
    }

    // Initialize Char Device into kernel.
    cdev_init(&vicharak_cdev, &fops);
    ret = cdev_add(&vicharak_cdev, dev_no, 1);
    if (ret) {
        device_destroy(vicharak_class, dev_no);
        class_destroy(vicharak_class);
        unregister_chrdev_region(dev_no, 1);
        return ret;
    }


    // Allocate memory for Queue
    queue_Buf = (char *)kmalloc(MAX, GFP_KERNEL);
    if (!queue_Buf) {
        pr_err("K");
        cdev_del(&vicharak_cdev);
        device_destroy(vicharak_class, dev_no);
        class_destroy(vicharak_class);
        unregister_chrdev_region(dev_no, 1);
        return -ENOMEM;
    }

    // Fifo Initialize
    kfifo_init(&my_fifo, queue_Buf, MAX);

    pr_info("vicharak: Device Initialized\n");
    return 0;
}

static void __exit vicharak_exit(void) {

    // Delete Cdev from kernel
    cdev_del(&vicharak_cdev);

    // Destroy Device (check if class exists)
    if (vicharak_class) {
        device_destroy(vicharak_class, dev_no);
        class_destroy(vicharak_class);
    }

    // Unregister device from kernel
    unregister_chrdev_region(dev_no, 1);

    // Free Kfifo
    kfifo_free(&my_fifo);

    // Free Memory Allocated for Kfifo (check before freeing)
    if (queue_Buf) {
        kfree(queue_Buf);
        queue_Buf = NULL;
    }

    pr_info("vicharak: Device Removed\n");
}
module_init(vicharak_init);
module_exit(vicharak_exit);

MODULE_LICENSE("GPL");
MODULE_DESCRIPTION("Char Device Driver");
MODULE_AUTHOR("Rounak Vhaskeri <rounakvhaskeri31@gmail.com>");
