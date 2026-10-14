# STM32 In-Vehicle-Communication

A collection of STM32-based embedded system****periments and peripheral interfacing projects, including CAN communication, sensor interfacing, and ESP32 integration.

> **Note:** This repository contains multiple subprojects. Their exact hardware, firmware configuration, and implementation details may differ. Check each subproject's source code and configuration files before building or running it.

## Overview

This repository brings together practical embedded C work developed around STM32 microcontrollers and connected peripherals. It is intended to demonstrate hands-on learning in microcontroller programming, peripheral communication, and sensor integration.

## Project Areas

The repository currently includes these folders:

| Folder | Area |
|---|---|
| `CAN_Communication/` | CAN communication experiments |
| `Accel_V1/` | Accelerometer interfacing — version 1 |
| `Acclerometer_V2/` | Accelerometer interfacing — version 2 |
| `DHT_22_interfacing_v4/` | DHT22 temperature and humidity sensor interfacing |
| `INA219_V1/` | INA219 voltage/current monitoring — version 1 |
| `INA219_V2/` | INA219 voltage/current monitoring — version 2 |
| `Esp32_integration/` | ESP32 integration experiments |
| `FinalCode/` | Integrated/final project code; inspect this folder to confirm its scope |

## Technologies and Concepts

- **Embedded C / STM32** — microcontroller firmware development
- **CAN** — Controller Area Network communication
- **I2C** — communication with supported sensors and peripherals
- **SPI** — serial peripheral communication, where implemented in the relevant subproject
- **Sensor interfacing** — accelerometer, DHT22, and INA219 modules
- **STM32 development tools** — use the IDE and toolchain required by each subproject (for example, STM32CubeIDE if the project files are configured for it)

Only claim the interfaces and tools you have personally implemented and can explain in an interview.

## Repository Structure

```text
STM32_In-Vehicle-Communication/
├── Accel_V1/
├── Acclerometer_V2/
├── CAN_Communication/
├── DHT_22_interfacing_v4/
├── Esp32_integration/
├── FinalCode/
├── INA219_V1/
└── INA219_V2/
```

## Getting Started

1. Open the folder for the subproject you want to explore.
2. Inspect its source files and any project configuration files.
3. Identify the target STM32 board, connected modules, pin assignments, and required libraries.
4. Import the project into the IDE/toolchain expected by its configuration.
5. Build the firmware, flash it to the appropriate board, and test it with the required hardware.

Because this repository contains multiple subprojects, there may not be one build procedure that applies to every folder. Add exact board models, wiring diagrams, dependencies, build steps, and test results to each subproject as you verify them.

## Collaboration and Contributions

This project was developed collaboratively. The repository owner and collaborators should be credited accurately, and individual contributions should be described honestly. Publish source code only when you have permission to share it and it contains no credentials or confidential material.

## Future Improvements

- Add a wiring diagram and hardware list for each subproject.
- Document the exact STM32 board and peripheral configuration.
- Include build and flashing instructions verified on the target hardware.
- Add test results, screenshots, or demonstration videos where available.
- Explain the CAN message format, identifiers, baud rate, and transmit/receive behavior in the CAN subproject.
- Consolidate duplicate or older versions only after confirming what differs between them.

## Author

**Rounak V. Haskeri**

GitHub: [ROUNAKVhaskeri](https://github.com/ROUNAKVhaskeri)

---

This README describes the repository at a high level. Update it with verified board details, implementation specifics, test evidence, and collaborator credits before using it as a formal project portfolio.
