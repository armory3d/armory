/**
 * Signal System Implementation
 * ============================
 *
 * Per-instance signals with connect/disconnect/emit support.
 * Each signal can have up to ARM_SIGNAL_MAX_SUBS subscribers (default 16).
 *
 * Memory: Each ArmSignal is ~200 bytes (16 handlers * 12 bytes + count)
 * Performance: O(n) for all operations where n = subscriber count
 */

#include "../types.h"
#include <string.h>

void signal_connect(ArmSignal *signal, ArmSignalHandler handler, void *obj, void *data)
{
    if (signal == NULL || handler == NULL) return;
    if (signal->count >= ARM_SIGNAL_MAX_SUBS) return;  // Full, silently ignore

    // Check if already connected (avoid duplicates)
    for (uint8_t i = 0; i < signal->count; i++) {
        if (signal->handlers[i] == handler &&
            signal->handler_objs[i] == obj &&
            signal->handler_data[i] == data) {
            return;  // Already connected
        }
    }

    // Add new subscriber
    uint8_t idx = signal->count++;
    signal->handlers[idx] = handler;
    signal->handler_objs[idx] = obj;
    signal->handler_data[idx] = data;
}

void signal_disconnect(ArmSignal *signal, ArmSignalHandler handler)
{
    if (signal == NULL || handler == NULL) return;

    for (uint8_t i = 0; i < signal->count; i++) {
        if (signal->handlers[i] == handler) {
            // Shift remaining handlers down
            for (uint8_t j = i; j < signal->count - 1; j++) {
                signal->handlers[j] = signal->handlers[j + 1];
                signal->handler_objs[j] = signal->handler_objs[j + 1];
                signal->handler_data[j] = signal->handler_data[j + 1];
            }
            signal->count--;
            return;
        }
    }
}

void signal_emit(ArmSignal *signal, void *sender, void *arg0, void *arg1, void *arg2, void *arg3)
{
    if (signal == NULL || signal->count == 0) return;

    // Call all handlers with their stored obj/data plus the emit args
    for (uint8_t i = 0; i < signal->count; i++) {
        if (signal->handlers[i] != NULL) {
            signal->handlers[i](signal->handler_objs[i], signal->handler_data[i], arg0, arg1, arg2, arg3);
        }
    }
}

void signal_clear(ArmSignal *signal)
{
    if (signal == NULL) return;
    memset(signal, 0, sizeof(ArmSignal));
}
