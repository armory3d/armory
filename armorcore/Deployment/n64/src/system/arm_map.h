/**
 * arm_map.h - String-keyed maps for N64
 *
 * Linear search implementation optimized for small maps (<20 entries).
 * Static allocation with fixed capacity to avoid heap fragmentation.
 *
 * Usage:
 *   ARM_MAP_DECLARE(ArmSoundHandleArray, SoundChannelMap, 8)
 *
 *   SoundChannelMap my_map = {0};
 *   SoundChannelMap_set(&my_map, "gem_collect", &array);
 *   ArmSoundHandleArray* arr = SoundChannelMap_get(&my_map, "gem_collect");
 */

#ifndef ARM_MAP_H
#define ARM_MAP_H

#include <stdint.h>
#include <stdbool.h>
#include <string.h>

// Maximum key length for string keys
#define ARM_MAP_MAX_KEY_LEN 32

/**
 * Declare a string-keyed map with given value type, name, and max capacity.
 * Values are stored by copy, so use pointers for large structs.
 */
#define ARM_MAP_DECLARE(value_type, map_name, max_capacity) \
    typedef struct map_name##_entry { \
        char key[ARM_MAP_MAX_KEY_LEN]; \
        value_type value; \
        bool occupied; \
    } map_name##_entry; \
    \
    typedef struct map_name { \
        map_name##_entry entries[max_capacity]; \
        uint16_t count; \
        uint16_t capacity; \
    } map_name; \
    \
    static inline void map_name##_init(map_name *map) { \
        memset(map, 0, sizeof(map_name)); \
        map->capacity = max_capacity; \
    } \
    \
    static inline bool map_name##_set(map_name *map, const char *key, value_type value) { \
        /* First check if key exists */ \
        for (int i = 0; i < max_capacity; i++) { \
            if (map->entries[i].occupied && strcmp(map->entries[i].key, key) == 0) { \
                map->entries[i].value = value; \
                return true; \
            } \
        } \
        /* Find empty slot */ \
        for (int i = 0; i < max_capacity; i++) { \
            if (!map->entries[i].occupied) { \
                strncpy(map->entries[i].key, key, ARM_MAP_MAX_KEY_LEN - 1); \
                map->entries[i].key[ARM_MAP_MAX_KEY_LEN - 1] = '\0'; \
                map->entries[i].value = value; \
                map->entries[i].occupied = true; \
                map->count++; \
                return true; \
            } \
        } \
        return false; /* Map full */ \
    } \
    \
    static inline value_type* map_name##_get(map_name *map, const char *key) { \
        for (int i = 0; i < max_capacity; i++) { \
            if (map->entries[i].occupied && strcmp(map->entries[i].key, key) == 0) { \
                return &map->entries[i].value; \
            } \
        } \
        return NULL; \
    } \
    \
    static inline bool map_name##_exists(map_name *map, const char *key) { \
        return map_name##_get(map, key) != NULL; \
    } \
    \
    static inline bool map_name##_remove(map_name *map, const char *key) { \
        for (int i = 0; i < max_capacity; i++) { \
            if (map->entries[i].occupied && strcmp(map->entries[i].key, key) == 0) { \
                map->entries[i].occupied = false; \
                map->count--; \
                return true; \
            } \
        } \
        return false; \
    } \
    \
    static inline void map_name##_clear(map_name *map) { \
        memset(map->entries, 0, sizeof(map->entries)); \
        map->count = 0; \
    } \
    \
    static inline int map_name##_size(map_name *map) { \
        return map->count; \
    }

#endif // ARM_MAP_H
