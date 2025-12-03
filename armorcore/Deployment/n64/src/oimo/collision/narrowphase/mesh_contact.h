// mesh_contact.h - Shared contact storage for mesh collision detectors
#ifndef OIMO_COLLISION_NARROWPHASE_MESH_CONTACT_H
#define OIMO_COLLISION_NARROWPHASE_MESH_CONTACT_H

#include "../../common/vec3.h"

#ifdef __cplusplus
extern "C" {
#endif

// Maximum contacts for mesh collision (balance stability vs performance)
#define OIMO_MESH_MAX_CONTACTS 4

// Temporary contact storage for single-pass mesh collision
typedef struct OimoMeshContact {
    OimoVec3 closest;       // Closest point on triangle (mesh local space)
    OimoVec3 normal_dir;    // Contact normal direction
    float depth;            // Penetration depth
    int tri_idx;            // Triangle index
} OimoMeshContact;

// Storage for multiple contacts during detection
typedef struct OimoMeshContactStorage {
    OimoMeshContact contacts[OIMO_MESH_MAX_CONTACTS];
    int count;
    float max_depth;
    OimoVec3 primary_normal;
    bool has_contact;
} OimoMeshContactStorage;

// Initialize contact storage
static inline void oimo_mesh_contact_storage_init(OimoMeshContactStorage* storage) {
    storage->count = 0;
    storage->max_depth = 0.0f;
    storage->primary_normal = oimo_vec3(0, 1, 0);
    storage->has_contact = false;
}

// Add a contact, replacing shallowest if full
static inline void oimo_mesh_contact_storage_add(
    OimoMeshContactStorage* storage,
    const OimoVec3* closest,
    const OimoVec3* normal_dir,
    float depth,
    int tri_idx
) {
    // Track primary normal (deepest penetration)
    if (depth > storage->max_depth) {
        storage->max_depth = depth;
        storage->primary_normal = *normal_dir;
        storage->has_contact = true;
    }

    // Add contact
    if (storage->count < OIMO_MESH_MAX_CONTACTS) {
        OimoMeshContact* c = &storage->contacts[storage->count++];
        c->closest = *closest;
        c->normal_dir = *normal_dir;
        c->depth = depth;
        c->tri_idx = tri_idx;
    } else {
        // Replace shallowest contact if this one is deeper
        int shallowest = 0;
        for (int i = 1; i < OIMO_MESH_MAX_CONTACTS; i++) {
            if (storage->contacts[i].depth < storage->contacts[shallowest].depth) {
                shallowest = i;
            }
        }
        if (depth > storage->contacts[shallowest].depth) {
            OimoMeshContact* c = &storage->contacts[shallowest];
            c->closest = *closest;
            c->normal_dir = *normal_dir;
            c->depth = depth;
            c->tri_idx = tri_idx;
        }
    }
}

#ifdef __cplusplus
}
#endif

#endif // OIMO_COLLISION_NARROWPHASE_MESH_CONTACT_H
