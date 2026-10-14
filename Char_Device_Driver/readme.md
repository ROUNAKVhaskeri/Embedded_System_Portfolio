# Linux Character Device Driver

A Linux kernel character-device driver project written in C, with companion user-space programs for interacting with the device.

> This README is a project overview based on the known repository filenames. Verify the device name, IOCTL definitions, build targets, and behavior against the source code before using the instructions below.

## Project Overview

Character devices allow user-space programs to interact with a kernel driver through a device file, commonly located under `/dev`. Applications can use familiar file operations, such as `open()`, `read()`, `write()`, and `close()`, while a driver may additionally expose device-specific controls through `ioctl()`.

This project explores the interface between **user space** and **kernel space** through a Linux character device.

## Repository Files

| File | Description |
|---|---|
| `vicharak.c` | Main driver source; inspect it for registration, file operations, and cleanup |
| `vicharak_ioctl.h` | Shared definitions for device-specific IOCTL requests |
| `reader.c` | User-space program intended for reading data |
| `filler.c` | User-space program intended for supplying data |
| `cofiguration.c` | Configuration-related source file (filename spelling as in the original repository) |
| `Makefile` | Build instructions for the driver and/or user-space programs |

The exact functionality of each file should be confirmed in the code.

## Architecture

```text
+-----------------------------+
|       User-space apps       |
| reader / filler / config    |
+--------------+--------------+
               |
+--------------v----------------+
|      Linux system calls       |
|  open / read / write / ioctl  |
+--------------+----------------+
               |
+--------------v--------------+
|       Linux VFS layer       |
+--------------+--------------+
               |
+--------------v--------------+
|   Character device driver   |
|       (kernel space)        |
+--------------+--------------+
               |
+--------------v--------------+
|     Driver-managed data     |
|     or hardware interface   |
+-----------------------------+
```

This is a conceptual diagram; it does not claim that the driver controls physical hardware.

## Core Concepts

### Character device registration

A character driver registers a device number (major and minor numbers) and connects the device to a `struct file_operations` implementation. Depending on its design, it may create a device class and device node or require manual node creation.

### File operations

A typical character driver may implement:

- `open()` — initialize or validate access to the device.
- `read()` — transfer data from the driver to a user-space buffer.
- `write()` — accept data from a user-space buffer.
- `release()` — clean up when the device is closed.
- `unlocked_ioctl()` — process device-specific control commands.

**Important:** Check `vicharak.c` to see which operations this project actually implements.

### User/kernel memory boundary

User pointers must not be dereferenced directly in kernel code. Kernel drivers commonly use `copy_to_user()` and `copy_from_user()` to move data across the user/kernel boundary while checking for failures.

## Build and Run

### Prerequisites

- A Linux environment suitable for loading kernel modules.
- GCC and Make.
- Kernel headers/build files that match the running kernel.
- Sufficient privileges to load and unload kernel modules.

**Caution:** Kernel module****ecute with kernel privileges. Build and test experimental drivers on a VM or noncritical test machine.

### Build

From the directory containing the Makefile:

```bash
make
```

Inspect the Makefile for the actual targets and generated filenames. A successful out-of-tree module build commonly produces a `.ko` file.

### Load the module

After confirming the module filename:

```bash
sudo insmod ./<module-name>.ko
dmesg | tail -n 30
```

Replace `<module-name>` with the generated module name.

### Find the device node

Check the driver's source and kernel messages for its device name and number:

```bash
dmesg | tail -n 30
ls -l /dev/
```

If the driver does not create a device node automatically, follow its actual registration logic to determine whether `mknod` is necessary. Do not guess the major/minor numbers.

### Test user-space interaction

Compile and run the companion programs using the commands and device path defined by the Makefile and source code. Check each program's arguments before executing it.

### Unload the module

```bash
sudo rmmod <module-name>
dmesg | tail -n 30
```

## Validation Checklist

Before presenting the project in an interview or job application, verify and document:

1. Which file operations are implemented and how errors are returned.
2. How device numbers and `/dev` entries are created.
3. What the IOCTL commands do and how their arguments are validated.
4. Whether reads and writes respect buffer bounds and file offsets.
5. Whether user-space copies handle partial failures correctly.
6. Whether shared state needs synchronization.
7. Whether initialization failures and module removal release all resources.
8. Which kernel version and architecture were used for testing.

## Possible Improvements

- Add sample commands and their actual output.
- Document IOCTL request codes and expected arguments.
- Include test cases for invalid pointers, oversized requests, and repeated opens.
- Add concurrency tests where shared mutable state exists.
- Record the supported kernel versions and known limitations.

## Author

**Rounak V. Haskeri**

GitHub: [ROUNAKVhaskeri](https://github.com/ROUNAKVhaskeri)

## Project Link

[VICHARAK_DD](https://github.com/ROUNAKVhaskeri/VICHARAK_DD)

---
