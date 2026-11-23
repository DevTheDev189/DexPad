#ifndef _USB_DESCRIPTORS_H_
#define _USB_DESCRIPTORS_H_

#include "tusb.h"

#ifdef __cplusplus
extern "C" {
#endif

enum {
    REPORT_ID_KEYBOARD = 1,
    REPORT_ID_MOUSE = 2,
    REPORT_ID_CONSUMER_CONTROL = 3
};

#ifdef __cplusplus
}
#endif

#endif // _USB_DESCRIPTORS_H_
