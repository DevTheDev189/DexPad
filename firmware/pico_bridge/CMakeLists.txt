# ==============================================================================
# 8BitDo Ultimate 2C & Pico 2 W USB Hardware Bridge
# Dual Target: Raspberry Pi Pico 2 W (RP2350) & Pico W (RP2040)
# ==============================================================================

cmake_minimum_required(VERSION 3.13)

# Default to pico2_w if not explicitly passed via -DPICO_BOARD
if (NOT DEFINED PICO_BOARD)
    set(PICO_BOARD pico2_w)
endif()

# Pull in SDK (must be before project)
include(pico_sdk_import.cmake)

project(pico_8bitdo_bridge C CXX ASM)
set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)

# Initialize the Pico SDK
pico_sdk_init()

add_executable(pico_8bitdo_bridge
    main.c
    usb_descriptors.c
    flash_storage.c
)

# Include current directory for headers
target_include_directories(pico_8bitdo_bridge PRIVATE
    ${CMAKE_CURRENT_LIST_DIR}
)

# Link hardware libraries, TinyUSB, and Pico core
target_link_libraries(pico_8bitdo_bridge
    pico_stdlib
    pico_unique_id
    hardware_flash
    hardware_sync
    hardware_watchdog
    tinyusb_device
    tinyusb_board
)

# Enable TinyUSB device mode, disable default stdio usb/uart to prevent conflict
pico_enable_stdio_usb(pico_8bitdo_bridge 0)
pico_enable_stdio_uart(pico_8bitdo_bridge 0)

# Create map/bin/hex/uf2 file targets automatically
pico_add_extra_outputs(pico_8bitdo_bridge)
