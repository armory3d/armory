#pragma once

#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

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

void input_init(void);
void input_poll(void);

bool input_started(N64Button btn);
bool input_down(N64Button btn);
bool input_released(N64Button btn);

float input_stick_x(void);
float input_stick_y(void);

#ifdef __cplusplus
}
#endif
