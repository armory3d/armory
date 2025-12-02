// contact_manager.h
// 1:1 port from OimoPhysics ContactManager.hx
#ifndef OIMO_DYNAMICS_CONTACT_MANAGER_H
#define OIMO_DYNAMICS_CONTACT_MANAGER_H

#include <libdragon.h>
#include "../collision/broadphase/broadphase.h"
#include "../collision/broadphase/proxy_pair.h"
#include "../collision/narrowphase/collision_matrix.h"
#include "rigidbody/shape.h"
#include "rigidbody/rigid_body.h"
#include "rigidbody/rigid_body_type.h"
#include "contact.h"

// Maximum contacts (for N64 memory constraints)
#define OIMO_MAX_CONTACTS 64

typedef struct OimoContactManager {
    int _numContacts;
    OimoContact* _contactList;
    OimoContact* _contactListLast;

    // Contact pool for reuse
    OimoContact _contactPool[OIMO_MAX_CONTACTS];
    int _contactPoolUsed;
    OimoContact* _freeList;
    bool _poolOverflowWarned;

    OimoBroadPhase* _broadPhase;
    OimoCollisionMatrix _collisionMatrix;
} OimoContactManager;

static inline void oimo_contact_manager_init(OimoContactManager* cm, OimoBroadPhase* broadPhase) {
    cm->_numContacts = 0;
    cm->_contactList = NULL;
    cm->_contactListLast = NULL;
    cm->_broadPhase = broadPhase;
    cm->_collisionMatrix = oimo_collision_matrix_create();

    // Initialize contact pool
    cm->_contactPoolUsed = 0;
    cm->_freeList = NULL;
    cm->_poolOverflowWarned = false;
    for (int i = 0; i < OIMO_MAX_CONTACTS; i++) {
        oimo_contact_init(&cm->_contactPool[i]);
    }
}

// Get a contact from the pool
static inline OimoContact* oimo_contact_manager_alloc_contact(OimoContactManager* cm) {
    if (cm->_freeList != NULL) {
        OimoContact* c = cm->_freeList;
        cm->_freeList = c->_next;
        oimo_contact_init(c);
        return c;
    }
    if (cm->_contactPoolUsed < OIMO_MAX_CONTACTS) {
        OimoContact* c = &cm->_contactPool[cm->_contactPoolUsed++];
        oimo_contact_init(c);
        return c;
    }
    if (!cm->_poolOverflowWarned) {
        debugf("Oimo: contact pool exhausted (%d max). Increase OIMO_MAX_CONTACTS.\n", OIMO_MAX_CONTACTS);
        cm->_poolOverflowWarned = true;
    }
    return NULL; // Pool exhausted
}

// Return a contact to the pool
static inline void oimo_contact_manager_free_contact(OimoContactManager* cm, OimoContact* c) {
    c->_next = cm->_freeList;
    cm->_freeList = c;
    cm->_poolOverflowWarned = false;
}

// Check if two shapes should collide - 1:1 from ContactManager.shouldCollide
static inline bool oimo_contact_manager_should_collide(OimoShape* s1, OimoShape* s2) {
    OimoRigidBody* r1 = s1->_rigidBody;
    OimoRigidBody* r2 = s2->_rigidBody;

    if (r1 == r2) {
        return false;  // Same parent
    }

    if (r1->_type != OIMO_RIGID_BODY_DYNAMIC && r2->_type != OIMO_RIGID_BODY_DYNAMIC) {
        return false;  // Neither is dynamic
    }

    // Collision filtering
    if ((s1->_collisionGroup & s2->_collisionMask) == 0 ||
        (s2->_collisionGroup & s1->_collisionMask) == 0) {
        return false;
    }

    return true;
}

// Create contacts from broadphase pairs - 1:1 from ContactManager.createContacts
static inline void oimo_contact_manager_create_contacts(OimoContactManager* cm) {
    OimoProxyPair* pp = cm->_broadPhase->_proxyPairList;

    while (pp != NULL) {
        OimoShape* s1;
        OimoShape* s2;

        if (pp->_p1->_id < pp->_p2->_id) {
            s1 = (OimoShape*)pp->_p1->userData;
            s2 = (OimoShape*)pp->_p2->userData;
        } else {
            s1 = (OimoShape*)pp->_p2->userData;
            s2 = (OimoShape*)pp->_p1->userData;
        }

        // Collision filtering
        if (!oimo_contact_manager_should_collide(s1, s2)) {
            pp = pp->_next;
            continue;
        }

        // Search for existing contact
        OimoRigidBody* b1 = s1->_rigidBody;
        OimoRigidBody* b2 = s2->_rigidBody;
        int n1 = b1->_numContactLinks;
        int n2 = b2->_numContactLinks;

        OimoContactLink* l;
        if (n1 < n2) {
            l = b1->_contactLinkList;
        } else {
            l = b2->_contactLinkList;
        }

        int id1 = s1->_id;
        int id2 = s2->_id;
        bool found = false;

        while (l != NULL) {
            OimoContact* c = l->_contact;
            if (c->_s1->_id == id1 && c->_s2->_id == id2) {
                c->_latest = true;
                found = true;
                break;
            }
            l = l->_next;
        }

        // If not found, create new contact
        if (!found) {
            OimoContact* c = oimo_contact_manager_alloc_contact(cm);
            if (c != NULL) {
                // Add to contact list
                c->_prev = cm->_contactListLast;
                c->_next = NULL;
                if (cm->_contactListLast != NULL) {
                    cm->_contactListLast->_next = c;
                } else {
                    cm->_contactList = c;
                }
                cm->_contactListLast = c;

                c->_latest = true;
                OimoDetector* detector = oimo_collision_matrix_get_detector(&cm->_collisionMatrix, s1->_geom->type, s2->_geom->type);
                oimo_contact_attach(c, s1, s2, detector);
                cm->_numContacts++;
            }
        }

        pp = pp->_next;
    }
}

// Destroy a contact - 1:1 from ContactManager._destroyContact
static inline void oimo_contact_manager_destroy_contact(OimoContactManager* cm, OimoContact* contact) {
    // Remove from list
    if (contact->_prev != NULL) {
        contact->_prev->_next = contact->_next;
    } else {
        cm->_contactList = contact->_next;
    }
    if (contact->_next != NULL) {
        contact->_next->_prev = contact->_prev;
    } else {
        cm->_contactListLast = contact->_prev;
    }

    oimo_contact_detach(contact);
    oimo_contact_manager_free_contact(cm, contact);
    cm->_numContacts--;
}

// Destroy outdated contacts - 1:1 from ContactManager.destroyOutdatedContacts
static inline void oimo_contact_manager_destroy_outdated_contacts(OimoContactManager* cm) {
    bool incremental = cm->_broadPhase->_incremental;

    OimoContact* c = cm->_contactList;
    while (c != NULL) {
        OimoContact* next = c->_next;

        if (c->_latest) {
            c->_latest = false;
            c->_shouldBeSkipped = false;
        } else if (!incremental) {
            oimo_contact_manager_destroy_contact(cm, c);
        } else {
            OimoShape* s1 = c->_s1;
            OimoShape* s2 = c->_s2;
            OimoRigidBody* r1 = s1->_rigidBody;
            OimoRigidBody* r2 = s2->_rigidBody;

            bool active1 = !r1->_sleeping && r1->_type != OIMO_RIGID_BODY_STATIC;
            bool active2 = !r2->_sleeping && r2->_type != OIMO_RIGID_BODY_STATIC;

            if (!active1 && !active2) {
                c->_shouldBeSkipped = true;
            } else if (!oimo_broadphase_is_overlapping(s1->_proxy, s2->_proxy) ||
                       !oimo_contact_manager_should_collide(s1, s2)) {
                oimo_contact_manager_destroy_contact(cm, c);
            } else {
                // Check AABB overlap
                bool aabbOverlapping = oimo_aabb_overlap(&s1->_aabb, &s2->_aabb);
                c->_shouldBeSkipped = !aabbOverlapping;
            }
        }

        c = next;
    }
}

// Update contacts (broadphase) - 1:1 from ContactManager._updateContacts
static inline void oimo_contact_manager_update_contacts(OimoContactManager* cm) {
    oimo_broadphase_collect_pairs(cm->_broadPhase);
    oimo_contact_manager_create_contacts(cm);
    oimo_contact_manager_destroy_outdated_contacts(cm);
}

// Update manifolds (narrowphase) - 1:1 from ContactManager._updateManifolds
static inline void oimo_contact_manager_update_manifolds(OimoContactManager* cm) {
    OimoContact* c = cm->_contactList;
    while (c != NULL) {
        if (!c->_shouldBeSkipped) {
            oimo_contact_update_manifold_with_matrix(c, &cm->_collisionMatrix);
        }
        c = c->_next;
    }
}

// Post solve
static inline void oimo_contact_manager_post_solve(OimoContactManager* cm) {
    // Currently no callbacks needed for N64
}

static inline int oimo_contact_manager_get_num_contacts(const OimoContactManager* cm) {
    return cm->_numContacts;
}

static inline OimoContact* oimo_contact_manager_get_contact_list(const OimoContactManager* cm) {
    return cm->_contactList;
}

#endif // OIMO_DYNAMICS_CONTACT_MANAGER_H
