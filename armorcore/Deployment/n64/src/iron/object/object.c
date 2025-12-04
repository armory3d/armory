// object.c - Object lifecycle management
#include "object.h"
#include "../../engine.h"

#if ENGINE_ENABLE_PHYSICS
#include "../../events/physics_events.h"
#include "../../oimo/physics.h"
#endif

void object_remove(ArmObject* obj)
{
    if (!obj) return;

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

    // Hide the object and clear traits
    obj->visible = false;
    obj->trait_count = 0;
}
