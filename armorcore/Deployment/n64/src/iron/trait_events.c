#include "trait_events.h"
#include "system/input.h"
#include <string.h>

static TraitEventState g_events;

void trait_events_init(void)
{
    memset(&g_events, 0, sizeof(g_events));
}

void trait_events_clear(void)
{
    memset(&g_events, 0, sizeof(g_events));
}

void trait_events_subscribe_started(N64Button btn, TraitEventHandler handler, void* obj, void* data)
{
    if (btn >= N64_BTN_COUNT) return;
    ButtonEventSubs* subs = &g_events.buttons[btn];
    if (subs->started_count >= MAX_BUTTON_SUBSCRIBERS) return;

    subs->started[subs->started_count].handler = handler;
    subs->started[subs->started_count].obj = obj;
    subs->started[subs->started_count].data = data;
    subs->started_count++;
}

void trait_events_subscribe_released(N64Button btn, TraitEventHandler handler, void* obj, void* data)
{
    if (btn >= N64_BTN_COUNT) return;
    ButtonEventSubs* subs = &g_events.buttons[btn];
    if (subs->released_count >= MAX_BUTTON_SUBSCRIBERS) return;

    subs->released[subs->released_count].handler = handler;
    subs->released[subs->released_count].obj = obj;
    subs->released[subs->released_count].data = data;
    subs->released_count++;
}

void trait_events_subscribe_down(N64Button btn, TraitEventHandler handler, void* obj, void* data)
{
    if (btn >= N64_BTN_COUNT) return;
    ButtonEventSubs* subs = &g_events.buttons[btn];
    if (subs->down_count >= MAX_BUTTON_SUBSCRIBERS) return;

    subs->down[subs->down_count].handler = handler;
    subs->down[subs->down_count].obj = obj;
    subs->down[subs->down_count].data = data;
    subs->down_count++;
}

void trait_events_dispatch(float dt)
{
    for (int btn = 0; btn < N64_BTN_COUNT; btn++) {
        ButtonEventSubs* subs = &g_events.buttons[btn];

        // Dispatch "started" events
        if (input_started((N64Button)btn)) {
            for (uint8_t i = 0; i < subs->started_count; i++) {
                if (subs->started[i].handler) {
                    subs->started[i].handler(
                        subs->started[i].obj,
                        subs->started[i].data,
                        dt
                    );
                }
            }
        }

        // Dispatch "released" events
        if (input_released((N64Button)btn)) {
            for (uint8_t i = 0; i < subs->released_count; i++) {
                if (subs->released[i].handler) {
                    subs->released[i].handler(
                        subs->released[i].obj,
                        subs->released[i].data,
                        dt
                    );
                }
            }
        }

        // Dispatch "down" events (held)
        if (input_down((N64Button)btn)) {
            for (uint8_t i = 0; i < subs->down_count; i++) {
                if (subs->down[i].handler) {
                    subs->down[i].handler(
                        subs->down[i].obj,
                        subs->down[i].data,
                        dt
                    );
                }
            }
        }
    }
}
