// object.c - Object lifecycle management
#include "object.h"
#include "../../engine.h"

#if ENGINE_ENABLE_PHYSICS
#include "../../events/physics_events.h"
#include "../../oimo/physics.h"
#endif

void object_remove(ArmObject* obj)
{
    if (!obj || obj->is_removed) return;

    // Mark as removed immediately - physics dispatch checks this
    obj->is_removed = true;
    obj->visible = false;

    // Call all trait on_remove callbacks
    for (int i = 0; i < obj->trait_count; i++) {
        if (obj->traits[i].on_remove) {
            obj->traits[i].on_remove(obj, obj->traits[i].data);
        }
    }

#if ENGINE_ENABLE_PHYSICS
    // Unsubscribe from contact events
    physics_contact_unsubscribe_all(obj);

    // Remove physics body
    if (obj->rigid_body) {
        physics_remove_body(obj);
    }
#endif

    // Clear traits
    obj->trait_count = 0;
}

void object_process_removals(void)
{
    // No-op - removals are now immediate
    // Kept for API compatibility
}
