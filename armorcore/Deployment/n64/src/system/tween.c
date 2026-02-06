/**
 * Tween system for N64 - Fixed pool implementation
 *
 * Design decisions for N64 hardware:
 * - Fixed pool of MAX_TWEENS (16) - no malloc/free during gameplay
 * - All easing functions are inline for speed
 * - Deferred cleanup to avoid iteration issues
 * - Callbacks receive object + data pointers for full capture support
 */

#include "tween.h"
#include <string.h>
#include <math.h>
#include <libdragon.h>

// Tween pool - statically allocated
static ArmTween tween_pool[MAX_TWEENS];
static bool pool_initialized = false;

// Forward declarations for easing functions
static float ease_linear(float t);
static float ease_quad_in(float t);
static float ease_quad_out(float t);
static float ease_quad_in_out(float t);
static float ease_cubic_in(float t);
static float ease_cubic_out(float t);
static float ease_cubic_in_out(float t);
static float ease_sine_in(float t);
static float ease_sine_out(float t);
static float ease_sine_in_out(float t);

// Initialize pool if needed
static void ensure_pool_init(void) {
    if (pool_initialized) return;
    memset(tween_pool, 0, sizeof(tween_pool));
    pool_initialized = true;
}

// Allocate a tween from the pool
ArmTween* tween_alloc(void) {
    ensure_pool_init();

    for (int i = 0; i < MAX_TWEENS; i++) {
        if (tween_pool[i].type == TWEEN_NONE && !tween_pool[i].active && !tween_pool[i].pending_free) {
            ArmTween* t = &tween_pool[i];
            memset(t, 0, sizeof(ArmTween));
            t->type = TWEEN_ALLOCATED;  // Mark as allocated to prevent double-allocation
            return t;
        }
    }

    // Pool exhausted - return NULL
    return NULL;
}

// Free a tween back to the pool
void tween_free(ArmTween* tween) {
    if (!tween) return;
    tween->active = false;
    tween->pending_free = false;
    tween->type = TWEEN_NONE;
}

// Configure float tween
void tween_float(ArmTween* tween, float from, float to, float duration,
                 TweenFloatCallback on_update, TweenDoneCallback on_done,
                 TweenEase ease, void* object, void* data) {
    if (!tween) return;

    tween->type = TWEEN_FLOAT;
    tween->from_f = from;
    tween->to_f = to;
    tween->duration = duration > 0.0f ? duration : 0.001f;  // Avoid div by zero
    tween->elapsed = 0.0f;
    tween->ease = ease;
    tween->on_float = on_update;
    tween->on_done = on_done;
    tween->object = object;
    tween->data = data;
    tween->paused = false;
    tween->pending_free = false;
}

// Configure vec4 tween
void tween_vec4(ArmTween* tween, ArmVec4* from, ArmVec4* to, float duration,
                TweenVec4Callback on_update, TweenDoneCallback on_done,
                TweenEase ease, void* object, void* data) {
    if (!tween || !from || !to) return;

    tween->type = TWEEN_VEC4;
    tween->from_v = *from;
    tween->to_v = *to;
    tween->duration = duration > 0.0f ? duration : 0.001f;
    tween->elapsed = 0.0f;
    tween->ease = ease;
    tween->on_vec4 = on_update;
    tween->on_done = on_done;
    tween->object = object;
    tween->data = data;
    tween->paused = false;
    tween->pending_free = false;
}

// Configure delay (timer) tween
void tween_delay(ArmTween* tween, float duration,
                 TweenDoneCallback on_done, void* object, void* data) {
    if (!tween) return;

    tween->type = TWEEN_DELAY;
    tween->duration = duration > 0.0f ? duration : 0.001f;
    tween->elapsed = 0.0f;
    tween->ease = EASE_LINEAR;
    tween->on_float = NULL;
    tween->on_vec4 = NULL;
    tween->on_done = on_done;
    tween->object = object;
    tween->data = data;
    tween->paused = false;
    tween->pending_free = false;
}

// Start a tween
void tween_start(ArmTween* tween) {
    if (!tween) return;
    tween->active = true;
    tween->paused = false;
    tween->elapsed = 0.0f;
}

// Pause a tween
void tween_pause(ArmTween* tween) {
    if (!tween) return;
    tween->paused = true;
}

// Stop a tween (mark for cleanup)
void tween_stop(ArmTween* tween) {
    if (!tween) return;
    tween->pending_free = true;
}

// Check if tween is stopped
bool tween_is_stopped(ArmTween* tween) {
    if (!tween) return true;
    return !tween->active || tween->pending_free;
}

// Apply easing function
static float apply_ease(TweenEase ease, float t) {
    switch (ease) {
        case EASE_LINEAR:       return ease_linear(t);
        case EASE_QUAD_IN:      return ease_quad_in(t);
        case EASE_QUAD_OUT:     return ease_quad_out(t);
        case EASE_QUAD_IN_OUT:  return ease_quad_in_out(t);
        case EASE_CUBIC_IN:     return ease_cubic_in(t);
        case EASE_CUBIC_OUT:    return ease_cubic_out(t);
        case EASE_CUBIC_IN_OUT: return ease_cubic_in_out(t);
        case EASE_SINE_IN:      return ease_sine_in(t);
        case EASE_SINE_OUT:     return ease_sine_out(t);
        case EASE_SINE_IN_OUT:  return ease_sine_in_out(t);
        default:                return t;
    }
}

// Update a single tween, returns true if completed
static bool update_tween(ArmTween* tween, float dt) {
    if (!tween->active || tween->paused || tween->pending_free) {
        return false;
    }

    tween->elapsed += dt;

    // Calculate progress (0 to 1)
    float t = tween->elapsed / tween->duration;
    if (t > 1.0f) t = 1.0f;

    // Apply easing
    float eased = apply_ease(tween->ease, t);

    // Call update callback based on type
    switch (tween->type) {
        case TWEEN_FLOAT:
            if (tween->on_float) {
                float value = tween->from_f + (tween->to_f - tween->from_f) * eased;
                tween->on_float(value, tween->object, tween->data);
            }
            break;

        case TWEEN_VEC4:
            if (tween->on_vec4) {
                tween->current_v.x = tween->from_v.x + (tween->to_v.x - tween->from_v.x) * eased;
                tween->current_v.y = tween->from_v.y + (tween->to_v.y - tween->from_v.y) * eased;
                tween->current_v.z = tween->from_v.z + (tween->to_v.z - tween->from_v.z) * eased;
                tween->current_v.w = tween->from_v.w + (tween->to_v.w - tween->from_v.w) * eased;
                tween->on_vec4(&tween->current_v, tween->object, tween->data);
            }
            break;

        case TWEEN_DELAY:
            // No update callback for delay
            break;

        default:
            break;
    }

    // Check if completed
    if (tween->elapsed >= tween->duration) {
        return true;
    }

    return false;
}

// Update all active tweens
void tween_update_all(float dt) {
    ensure_pool_init();

    for (int i = 0; i < MAX_TWEENS; i++) {
        ArmTween* t = &tween_pool[i];

        // Skip inactive tweens
        if (!t->active) {
            continue;
        }

        // Update and check for completion
        bool completed = update_tween(t, dt);

        if (completed) {
            // Save callback info before marking inactive
            // (callback may restart this same tween)
            TweenDoneCallback done_cb = t->on_done;
            void* cb_obj = t->object;
            void* cb_data = t->data;

            // Mark as inactive BEFORE calling callback
            // This allows the callback to restart the tween
            t->active = false;
            t->on_done = NULL;  // Prevent double-fire

            // Call done callback (may restart this tween)
            if (done_cb) {
                done_cb(cb_obj, cb_data);
            }
        }
    }
}

// ============================================================================
// Easing functions - optimized for N64
// ============================================================================

static float ease_linear(float t) {
    return t;
}

static float ease_quad_in(float t) {
    return t * t;
}

static float ease_quad_out(float t) {
    return t * (2.0f - t);
}

static float ease_quad_in_out(float t) {
    if (t < 0.5f) {
        return 2.0f * t * t;
    }
    return -1.0f + (4.0f - 2.0f * t) * t;
}

static float ease_cubic_in(float t) {
    return t * t * t;
}

static float ease_cubic_out(float t) {
    float t1 = t - 1.0f;
    return t1 * t1 * t1 + 1.0f;
}

static float ease_cubic_in_out(float t) {
    if (t < 0.5f) {
        return 4.0f * t * t * t;
    }
    float t1 = 2.0f * t - 2.0f;
    return 0.5f * t1 * t1 * t1 + 1.0f;
}

// PI constant for sine easing
#ifndef M_PI
#define M_PI 3.14159265358979323846f
#endif

static float ease_sine_in(float t) {
    return 1.0f - fm_cosf(t * M_PI * 0.5f);
}

static float ease_sine_out(float t) {
    return fm_sinf(t * M_PI * 0.5f);
}

static float ease_sine_in_out(float t) {
    return 0.5f * (1.0f - fm_cosf(M_PI * t));
}
