/**
 * arm_array.h - Type-safe dynamic arrays for N64
 *
 * Uses macro-based type generation for zero-overhead type safety.
 * Static allocation with fixed capacity to avoid heap fragmentation.
 *
 * Usage:
 *   ARM_ARRAY_DECLARE(ArmSoundHandle, ArmSoundHandleArray, 16)
 *
 *   ArmSoundHandleArray my_array = {0};
 *   armsoundhandlearray_push(&my_array, handle);
 *   ArmSoundHandle h = armsoundhandlearray_get(&my_array, 0);
 *   int len = my_array.count;
 *
 * Generated function names are lowercase versions of the array type name.
 */

#ifndef ARM_ARRAY_H
#define ARM_ARRAY_H

#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <ctype.h>

/**
 * Declare a typed array with given element type, name, and max capacity.
 * This generates both the struct and inline functions.
 * Function names are lowercase: typename_push, typename_get, etc.
 */
#define ARM_ARRAY_DECLARE(elem_type, array_name, max_capacity) \
    typedef struct array_name { \
        elem_type items[max_capacity]; \
        uint16_t count; \
        uint16_t capacity; \
    } array_name; \
    \
    static inline void array_name##_init(array_name *arr) { \
        arr->count = 0; \
        arr->capacity = max_capacity; \
    } \
    \
    static inline bool array_name##_push(array_name *arr, elem_type item) { \
        if (arr->count >= max_capacity) return false; \
        arr->items[arr->count++] = item; \
        return true; \
    } \
    \
    static inline elem_type array_name##_get(array_name *arr, int index) { \
        if (index < 0 || index >= arr->count) { \
            elem_type zero = {0}; \
            return zero; \
        } \
        return arr->items[index]; \
    } \
    \
    static inline elem_type* array_name##_get_ptr(array_name *arr, int index) { \
        if (index < 0 || index >= arr->count) return NULL; \
        return &arr->items[index]; \
    } \
    \
    static inline void array_name##_set(array_name *arr, int index, elem_type item) { \
        if (index >= 0 && index < arr->count) { \
            arr->items[index] = item; \
        } \
    } \
    \
    static inline void array_name##_clear(array_name *arr) { \
        arr->count = 0; \
    } \
    \
    static inline int array_name##_length(array_name *arr) { \
        return arr->count; \
    } \
    \
    static inline elem_type array_name##_pop(array_name *arr) { \
        if (arr->count == 0) { \
            elem_type zero = {0}; \
            return zero; \
        } \
        return arr->items[--arr->count]; \
    }

/**
 * Convenience macro for common array types.
 * Pre-declare some common array types used in games.
 */

// Int array with default capacity 32
ARM_ARRAY_DECLARE(int32_t, ArmIntArray, 32)

// Float array with default capacity 32
ARM_ARRAY_DECLARE(float, ArmFloatArray, 32)

// String array (const char*) with default capacity 16
ARM_ARRAY_DECLARE(const char*, ArmStringArray, 16)

// Bool array with default capacity 32
ARM_ARRAY_DECLARE(bool, ArmBoolArray, 32)

#endif // ARM_ARRAY_H
