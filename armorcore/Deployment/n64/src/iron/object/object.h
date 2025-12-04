// object.h - Object lifecycle management
#pragma once

#include "../../types.h"

#ifdef __cplusplus
extern "C" {
#endif

/**
 * Remove an object from the scene.
 * - Calls all trait on_remove callbacks
 * - Unsubscribes from physics contact events
 * - Removes physics body
 * - Hides the object
 *
 * Safe to call multiple times. Memory cleanup happens during scene_clear().
 */
void object_remove(ArmObject* obj);

// Future: light_remove, camera_remove

#ifdef __cplusplus
}
#endif
