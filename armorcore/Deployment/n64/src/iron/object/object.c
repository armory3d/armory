// object.c - Object lifecycle management
#include "object.h"
#include "../../engine.h"
#include "../../data/scenes.h"

#if ENGINE_ENABLE_PHYSICS
#include "../../events/physics_events.h"
#include "../../oimo/physics.h"
#endif

// Deferred removal queue - objects are marked for removal but physics cleanup
// is deferred until safe (after contact dispatch completes)
#define MAX_PENDING_REMOVALS 32

typedef struct {
    ArmObject* obj;
    SceneId scene_id;
    bool recycle;  // Whether to recycle the slot back to pool
} PendingRemoval;

static PendingRemoval g_pending_removals[MAX_PENDING_REMOVALS];
static uint8_t g_pending_count = 0;

static void object_remove_internal(ArmObject* obj, SceneId scene_id, bool recycle)
{
    if (!obj || obj->is_removed) return;

    // Mark as removed immediately - prevents further trait callbacks and rendering
    obj->is_removed = true;
    obj->visible = false;

    // Call all trait on_remove callbacks
    for (int i = 0; i < obj->trait_count; i++) {
        if (obj->traits[i].on_remove) {
            obj->traits[i].on_remove(obj, obj->traits[i].data);
        }
    }

    // Clear traits
    obj->trait_count = 0;

    // Queue for deferred cleanup
    if (g_pending_count < MAX_PENDING_REMOVALS) {
        g_pending_removals[g_pending_count].obj = obj;
        g_pending_removals[g_pending_count].scene_id = scene_id;
        g_pending_removals[g_pending_count].recycle = recycle;
        g_pending_count++;
    }
}

void object_remove(ArmObject* obj)
{
    object_remove_internal(obj, scene_get_current_id(), false);
}

void object_remove_and_recycle(ArmObject* obj, SceneId scene_id)
{
    object_remove_internal(obj, scene_id, true);
}

void object_process_removals(void)
{
    for (uint8_t i = 0; i < g_pending_count; i++) {
        PendingRemoval* pr = &g_pending_removals[i];
        ArmObject* obj = pr->obj;

        if (!obj) continue;

#if ENGINE_ENABLE_PHYSICS
        if (obj->rigid_body) {
            physics_contact_unsubscribe_all(obj);
            physics_remove_body(obj);
        }
#endif

        // Recycle the slot back to the pool if requested
        if (pr->recycle && pr->scene_id < SCENE_COUNT) {
            scene_recycle_object(pr->scene_id, obj);
        }
    }
    g_pending_count = 0;
}
