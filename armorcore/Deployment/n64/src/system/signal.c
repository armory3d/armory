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

void signal_connect(ArmSignal *signal, ArmSignalHandler handler, void *ctx)
{
    if (signal == NULL || handler == NULL) return;
    if (signal->count >= ARM_SIGNAL_MAX_SUBS) return;  // Full, silently ignore

    // Check if already connected (avoid duplicates)
    for (uint8_t i = 0; i < signal->count; i++) {
        ArmSignalEntry *e = &signal->entries[i];
        if (e->handler == handler && e->ctx == ctx) {
            return;  // Already connected
        }
    }

    // Add new subscriber
    ArmSignalEntry *entry = &signal->entries[signal->count++];
    entry->handler = handler;
    entry->ctx = ctx;
}

void signal_disconnect(ArmSignal *signal, ArmSignalHandler handler)
{
    if (signal == NULL || handler == NULL) return;

    for (uint8_t i = 0; i < signal->count; i++) {
        if (signal->entries[i].handler == handler) {
            // Shift remaining entries down (single struct copy per iteration)
            for (uint8_t j = i; j < signal->count - 1; j++) {
                signal->entries[j] = signal->entries[j + 1];
            }
            signal->count--;
            return;
        }
    }
}

void signal_emit(ArmSignal *signal, void *payload)
{
    if (signal == NULL || signal->count == 0) return;

    // Call all handlers - AoS layout keeps handler+context together for cache efficiency
    for (uint8_t i = 0; i < signal->count; i++) {
        ArmSignalEntry *e = &signal->entries[i];
        if (e->handler != NULL) {
            e->handler(e->ctx, payload);
        }
    }
}

void signal_clear(ArmSignal *signal)
{
    if (signal == NULL) return;
    memset(signal, 0, sizeof(ArmSignal));
}
