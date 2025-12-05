// object.c - Object lifecycle management
#include "object.h"
#include "../../engine.h"

#if ENGINE_ENABLE_PHYSICS
#include "../../events/physics_events.h"
#include "../../oimo/physics.h"
#endif

// Deferred removal queue - objects are marked for removal but physics cleanup
// is deferred until safe (after contact dispatch completes)
#define MAX_PENDING_REMOVALS 32
static ArmObject* g_pending_removals[MAX_PENDING_REMOVALS];
static uint8_t g_pending_count = 0;

void object_remove(ArmObject* obj)
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

#if ENGINE_ENABLE_PHYSICS
    // Queue for deferred physics cleanup (safe after contact dispatch)
    if (obj->rigid_body && g_pending_count < MAX_PENDING_REMOVALS) {
        g_pending_removals[g_pending_count++] = obj;
    }
#endif
}

void object_process_removals(void)
{
#if ENGINE_ENABLE_PHYSICS
    // Process deferred physics removals - called after contact dispatch
    for (uint8_t i = 0; i < g_pending_count; i++) {
        ArmObject* obj = g_pending_removals[i];
        if (obj && obj->rigid_body) {
            physics_contact_unsubscribe_all(obj);
            physics_remove_body(obj);
        }
    }
    g_pending_count = 0;
#endif
}
