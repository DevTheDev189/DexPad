#ifndef _TUSB_CONFIG_H_
#define _TUSB_CONFIG_H_

#ifdef __cplusplus
extern "C" {
#endif

// --------------------------------------------------------------------+
// Board Specific Configuration
// --------------------------------------------------------------------+
#define CFG_TUSB_MCU                OPT_MCU_RP2040 // Covers RP2040 and RP2350 TinyUSB device mode
#define CFG_TUSB_OS                 OPT_OS_NONE

#ifndef CFG_TUSB_DEBUG
#define CFG_TUSB_DEBUG              0
#endif

#define CFG_TUD_ENDPOINT0_SIZE      64

// --------------------------------------------------------------------+
// USB Device Configuration (Composite CDC + HID)
// --------------------------------------------------------------------+
#define CFG_TUD_CDC                 1
#define CFG_TUD_HID                 1
#define CFG_TUD_MSC                 0
#define CFG_TUD_MIDI                0
#define CFG_TUD_VENDOR              0

// CDC FIFO size
#define CFG_TUD_CDC_RX_BUFSIZE      512
#define CFG_TUD_CDC_TX_BUFSIZE      512
#define CFG_TUD_CDC_EP_BUFSIZE      64

// HID buffer size
#define CFG_TUD_HID_EP_BUFSIZE      64

#ifdef __cplusplus
}
#endif

#endif // _TUSB_CONFIG_H_
