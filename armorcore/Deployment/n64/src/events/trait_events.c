#include "trait_events.h"
#include "../iron/system/input.h"
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

    // Set bitmask flag for fast dispatch
    g_events.has_started_subs |= (1 << btn);
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

    // Set bitmask flag for fast dispatch
    g_events.has_released_subs |= (1 << btn);
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

    // Set bitmask flag for fast dispatch
    g_events.has_down_subs |= (1 << btn);
}

// Helper to remove subscription from an array by object pointer
static void remove_sub_by_obj(TraitEventSub* subs, uint8_t* count, void* obj)
{
    for (int i = 0; i < *count; ) {
        if (subs[i].obj == obj) {
            // Shift remaining elements down
            for (int j = i; j < *count - 1; j++) {
                subs[j] = subs[j + 1];
            }
            (*count)--;
        } else {
            i++;
        }
    }
}

// Helper to update bitmask after unsubscribe
static void update_bitmask(uint16_t* mask, int btn, uint8_t count)
{
    if (count == 0) {
        *mask &= ~(1 << btn);
    }
}

void trait_events_unsubscribe_started(N64Button btn, void* obj)
{
    if (btn >= N64_BTN_COUNT) return;
    ButtonEventSubs* subs = &g_events.buttons[btn];
    remove_sub_by_obj(subs->started, &subs->started_count, obj);
    update_bitmask(&g_events.has_started_subs, btn, subs->started_count);
}

void trait_events_unsubscribe_released(N64Button btn, void* obj)
{
    if (btn >= N64_BTN_COUNT) return;
    ButtonEventSubs* subs = &g_events.buttons[btn];
    remove_sub_by_obj(subs->released, &subs->released_count, obj);
    update_bitmask(&g_events.has_released_subs, btn, subs->released_count);
}

void trait_events_unsubscribe_down(N64Button btn, void* obj)
{
    if (btn >= N64_BTN_COUNT) return;
    ButtonEventSubs* subs = &g_events.buttons[btn];
    remove_sub_by_obj(subs->down, &subs->down_count, obj);
    update_bitmask(&g_events.has_down_subs, btn, subs->down_count);
}

void trait_events_unsubscribe_all(void* obj)
{
    for (int btn = 0; btn < N64_BTN_COUNT; btn++) {
        ButtonEventSubs* subs = &g_events.buttons[btn];
        remove_sub_by_obj(subs->started, &subs->started_count, obj);
        remove_sub_by_obj(subs->released, &subs->released_count, obj);
        remove_sub_by_obj(subs->down, &subs->down_count, obj);
        update_bitmask(&g_events.has_started_subs, btn, subs->started_count);
        update_bitmask(&g_events.has_released_subs, btn, subs->released_count);
        update_bitmask(&g_events.has_down_subs, btn, subs->down_count);
    }
}

void trait_events_dispatch(float dt)
{
    // Fast path: skip entirely if no subscribers at all
    if (g_events.has_started_subs == 0 &&
        g_events.has_released_subs == 0 &&
        g_events.has_down_subs == 0) {
        return;
    }

    for (int btn = 0; btn < N64_BTN_COUNT; btn++) {
        uint16_t btn_mask = (1 << btn);

        // Dispatch "started" events - skip if no subscribers for this button
        if ((g_events.has_started_subs & btn_mask) && input_started((N64Button)btn)) {
            ButtonEventSubs* subs = &g_events.buttons[btn];
            for (uint8_t i = 0; i < subs->started_count; i++) {
                subs->started[i].handler(
                    subs->started[i].obj,
                    subs->started[i].data,
                    dt
                );
            }
        }

        // Dispatch "released" events - skip if no subscribers for this button
        if ((g_events.has_released_subs & btn_mask) && input_released((N64Button)btn)) {
            ButtonEventSubs* subs = &g_events.buttons[btn];
            for (uint8_t i = 0; i < subs->released_count; i++) {
                subs->released[i].handler(
                    subs->released[i].obj,
                    subs->released[i].data,
                    dt
                );
            }
        }

        // Dispatch "down" events - skip if no subscribers for this button
        if ((g_events.has_down_subs & btn_mask) && input_down((N64Button)btn)) {
            ButtonEventSubs* subs = &g_events.buttons[btn];
            for (uint8_t i = 0; i < subs->down_count; i++) {
                subs->down[i].handler(
                    subs->down[i].obj,
                    subs->down[i].data,
                    dt
                );
            }
        }
    }
}
