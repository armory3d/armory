// physics_events.c - Per-object physics contact event subscriptions
#include "physics_events.h"
#include "../oimo/physics.h"
#include <string.h>

// Static storage for body contact subscriptions
static BodyContactSubs g_body_subs[MAX_CONTACT_BODIES];
static int g_body_sub_count = 0;

void physics_contact_init(void)
{
    memset(g_body_subs, 0, sizeof(g_body_subs));
    g_body_sub_count = 0;
}

void physics_contact_clear(void)
{
    memset(g_body_subs, 0, sizeof(g_body_subs));
    g_body_sub_count = 0;
}

// Find or create subscription slot for a rigid body
static BodyContactSubs* find_or_create_body_subs(OimoRigidBody* rb)
{
    // Find existing
    for (int i = 0; i < g_body_sub_count; i++) {
        if (g_body_subs[i].rb == rb) {
            return &g_body_subs[i];
        }
    }
    // Create new if space available
    if (g_body_sub_count >= MAX_CONTACT_BODIES) {
        return NULL;
    }
    BodyContactSubs* slot = &g_body_subs[g_body_sub_count++];
    slot->rb = rb;
    slot->count = 0;
    return slot;
}

// Find subscription slot for a rigid body
static BodyContactSubs* find_body_subs(OimoRigidBody* rb)
{
    for (int i = 0; i < g_body_sub_count; i++) {
        if (g_body_subs[i].rb == rb) {
            return &g_body_subs[i];
        }
    }
    return NULL;
}

void physics_contact_subscribe(OimoRigidBody* rb, PhysicsContactHandler handler, void* obj, void* data)
{
    if (!rb || !handler) return;

    BodyContactSubs* subs = find_or_create_body_subs(rb);
    if (!subs || subs->count >= MAX_CONTACT_SUBSCRIBERS) return;

    subs->subs[subs->count].handler = handler;
    subs->subs[subs->count].obj = obj;
    subs->subs[subs->count].data = data;
    subs->count++;
}

void physics_contact_unsubscribe(OimoRigidBody* rb, PhysicsContactHandler handler, void* obj)
{
    if (!rb || !handler) return;

    BodyContactSubs* subs = find_body_subs(rb);
    if (!subs) return;

    // Find and remove matching subscription
    for (int i = 0; i < subs->count; ) {
        if (subs->subs[i].handler == handler && subs->subs[i].obj == obj) {
            // Shift remaining elements
            for (int j = i; j < subs->count - 1; j++) {
                subs->subs[j] = subs->subs[j + 1];
            }
            subs->count--;
        } else {
            i++;
        }
    }
}

void physics_contact_unsubscribe_all(void* obj)
{
    for (int b = 0; b < g_body_sub_count; b++) {
        BodyContactSubs* subs = &g_body_subs[b];
        for (int i = 0; i < subs->count; ) {
            if (subs->subs[i].obj == obj) {
                // Shift remaining elements
                for (int j = i; j < subs->count - 1; j++) {
                    subs->subs[j] = subs->subs[j + 1];
                }
                subs->count--;
            } else {
                i++;
            }
        }
    }
}

void physics_contact_dispatch(void)
{
    // Called after physics step
    // Iterate all touching contacts and dispatch to subscribed handlers
    OimoWorld* world = physics_get_world();
    if (!world) return;

    OimoContact* contact = world->_contactManager._contactList;
    while (contact != NULL) {
        // Only process touching contacts
        if (contact->_touching) {
            // Get both bodies' ArmObject pointers
            OimoRigidBody* rb1 = contact->_b1;
            OimoRigidBody* rb2 = contact->_b2;
            ArmObject* obj1 = (ArmObject*)rb1->userData;
            ArmObject* obj2 = (ArmObject*)rb2->userData;

            // Dispatch to body1's subscribers with body2 as "other"
            BodyContactSubs* subs1 = find_body_subs(rb1);
            if (subs1) {
                for (int i = 0; i < subs1->count; i++) {
                    subs1->subs[i].handler(subs1->subs[i].obj, subs1->subs[i].data, obj2);
                }
            }

            // Dispatch to body2's subscribers with body1 as "other"
            BodyContactSubs* subs2 = find_body_subs(rb2);
            if (subs2) {
                for (int i = 0; i < subs2->count; i++) {
                    subs2->subs[i].handler(subs2->subs[i].obj, subs2->subs[i].data, obj1);
                }
            }
        }
        contact = contact->_next;
    }
}
