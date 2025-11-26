#pragma once

#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

// N64 button mapping (matches libdragon joypad)
typedef enum {
    N64_BTN_A = 0,
    N64_BTN_B,
    N64_BTN_Z,
    N64_BTN_START,
    N64_BTN_DUP,
    N64_BTN_DDOWN,
    N64_BTN_DLEFT,
    N64_BTN_DRIGHT,
    N64_BTN_L,
    N64_BTN_R,
    N64_BTN_CUP,
    N64_BTN_CDOWN,
    N64_BTN_CLEFT,
    N64_BTN_CRIGHT,
    N64_BTN_COUNT
} N64Button;

// Initialize input system (call once at startup)
void input_init(void);

// Poll input state (call once per frame, before update)
void input_poll(void);

// Button state queries
bool input_started(N64Button btn);
bool input_down(N64Button btn);
bool input_released(N64Button btn);

// Analog stick (-1.0 to 1.0)
float input_stick_x(void);
float input_stick_y(void);

#ifdef __cplusplus
}
#endif
