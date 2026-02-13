// object.h - Object lifecycle management
#pragma once

#include "../../types.h"
#include "../../data/scenes.h"

#ifdef __cplusplus
extern "C" {
#endif

/**
 * Remove an object from the scene.
 * - Queues the object for deferred removal (safe during physics callbacks)
 * - Immediately hides the object
 * - Actual cleanup happens in object_process_removals()
 *
 * Safe to call multiple times. Memory cleanup happens during scene_clear().
 */
void object_remove(ArmObject* obj);

/**
 * Remove an object and recycle its slot back to the pool.
 * Use this version when you want the slot to be available for scene_alloc_object().
 */
void object_remove_and_recycle(ArmObject* obj, SceneId scene_id);

/**
 * Process all queued object removals.
 * Call this after physics_update() / physics_contact_dispatch().
 * - Calls all trait on_remove callbacks
 * - Unsubscribes from physics contact events
 * - Removes physics bodies
 */
void object_process_removals(void);

// Future: light_remove, camera_remove

#ifdef __cplusplus
}
#endif
