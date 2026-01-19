#include "input.h"
#include <libdragon.h>

#define STICK_MAX 85.0f

static joypad_inputs_t current_inputs;
static joypad_buttons_t pressed_buttons;
static joypad_buttons_t released_buttons;

void input_init(void)
{
    joypad_init();
}

void input_poll(void)
{
    joypad_poll();
    current_inputs = joypad_get_inputs(JOYPAD_PORT_1);
    pressed_buttons = joypad_get_buttons_pressed(JOYPAD_PORT_1);
    released_buttons = joypad_get_buttons_released(JOYPAD_PORT_1);
}

static bool get_button(joypad_buttons_t buttons, N64Button btn)
{
    switch (btn) {
        case N64_BTN_A:      return buttons.a;
        case N64_BTN_B:      return buttons.b;
        case N64_BTN_Z:      return buttons.z;
        case N64_BTN_START:  return buttons.start;
        case N64_BTN_DUP:    return buttons.d_up;
        case N64_BTN_DDOWN:  return buttons.d_down;
        case N64_BTN_DLEFT:  return buttons.d_left;
        case N64_BTN_DRIGHT: return buttons.d_right;
        case N64_BTN_L:      return buttons.l;
        case N64_BTN_R:      return buttons.r;
        case N64_BTN_CUP:    return buttons.c_up;
        case N64_BTN_CDOWN:  return buttons.c_down;
        case N64_BTN_CLEFT:  return buttons.c_left;
        case N64_BTN_CRIGHT: return buttons.c_right;
        default:             return false;
    }
}

bool input_started(N64Button btn)
{
    return get_button(pressed_buttons, btn);
}

bool input_down(N64Button btn)
{
    return get_button(current_inputs.btn, btn);
}

bool input_released(N64Button btn)
{
    return get_button(released_buttons, btn);
}

float input_stick_x(void)
{
    float val = (float)current_inputs.stick_x / STICK_MAX;
    if (val > 1.0f) val = 1.0f;
    if (val < -1.0f) val = -1.0f;
    return val;
}

float input_stick_y(void)
{
    float val = (float)current_inputs.stick_y / STICK_MAX;
    if (val > 1.0f) val = 1.0f;
    if (val < -1.0f) val = -1.0f;
    return val;
}
