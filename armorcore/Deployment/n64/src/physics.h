// physics.h - Mini-engine physics wrapper
#ifndef PHYSICS_H
#define PHYSICS_H

#include "types.h"
#include "oimo/oimo.h"

#ifdef __cplusplus
extern "C" {
#endif

// Maximum static mesh colliders (separate from body pool due to different memory management)
#define MAX_MESH_COLLIDERS 8

// World management
void physics_init(void);
void physics_shutdown(void);
void physics_reset(void);
void physics_step(float dt);
void physics_pause(void);
void physics_resume(void);
OimoWorld* physics_get_world(void);

// Gravity
void physics_set_gravity(float x, float y, float z);
OimoVec3 physics_get_gravity(void);

// Body creation (type: OIMO_RIGID_BODY_STATIC, DYNAMIC, KINEMATIC)
// Full versions with collision group/mask
// Returns true on success, false if pool exhausted
bool physics_create_box_ex(ArmObject* obj, int type, float hx, float hy, float hz,
                           float mass, float friction, float restitution,
                           int collision_group, int collision_mask);
bool physics_create_sphere_ex(ArmObject* obj, int type, float radius,
                              float mass, float friction, float restitution,
                              int collision_group, int collision_mask);
bool physics_create_capsule_ex(ArmObject* obj, int type, float radius, float half_height,
                               float mass, float friction, float restitution,
                               int collision_group, int collision_mask);

// Static mesh collider (always static body type)
// vertices: array of Vec3 positions
// indices: array of triangle indices (3 per triangle)
// vertex_count: number of vertices
// index_count: number of indices (must be multiple of 3)
bool physics_create_mesh(ArmObject* obj,
                         const OimoVec3* vertices, const int16_t* indices,
                         int vertex_count, int index_count,
                         float friction, float restitution,
                         int collision_group, int collision_mask);

// Convenience wrappers with default collision group=1, mask=1
static inline bool physics_create_box(ArmObject* obj, int type, float hx, float hy, float hz,
                                      float mass, float friction, float restitution) {
    return physics_create_box_ex(obj, type, hx, hy, hz, mass, friction, restitution, 1, 1);
}
static inline bool physics_create_sphere(ArmObject* obj, int type, float radius,
                                         float mass, float friction, float restitution) {
    return physics_create_sphere_ex(obj, type, radius, mass, friction, restitution, 1, 1);
}
static inline bool physics_create_capsule(ArmObject* obj, int type, float radius, float half_height,
                                          float mass, float friction, float restitution) {
    return physics_create_capsule_ex(obj, type, radius, half_height, mass, friction, restitution, 1, 1);
}

void physics_remove_body(ArmObject* obj);

// Transform sync (call after physics_step)
void physics_sync_object(ArmObject* obj);

// Contact/collision info
typedef struct PhysicsContactPair {
    ArmObject* obj_a;
    ArmObject* obj_b;
    OimoVec3 pos_a;
    OimoVec3 pos_b;
    OimoVec3 normal;
    float impulse;
} PhysicsContactPair;

// Callback for contact events
typedef void (*PhysicsContactCallback)(const PhysicsContactPair* contact, void* user_data);

// Set contact callback (called for each active contact after physics_step)
void physics_set_contact_callback(PhysicsContactCallback callback, void* user_data);

// Get contacts for a specific rigid body (returns count, fills contacts array up to max_contacts)
int physics_get_contacts(OimoRigidBody* rb, PhysicsContactPair* contacts, int max_contacts);

// Rigid body helpers
static inline void physics_apply_force(OimoRigidBody* rb, const OimoVec3* force) {
    if (rb) oimo_rigid_body_apply_force_to_center(rb, force);
}

static inline void physics_apply_impulse(OimoRigidBody* rb, const OimoVec3* impulse) {
    if (rb) {
        OimoVec3 pos = oimo_rigid_body_get_position(rb);
        oimo_rigid_body_apply_impulse(rb, impulse, &pos);
    }
}

static inline void physics_set_linear_velocity(OimoRigidBody* rb, const OimoVec3* vel) {
    if (rb) oimo_rigid_body_set_linear_velocity(rb, vel);
}

static inline OimoVec3 physics_get_linear_velocity(const OimoRigidBody* rb) {
    return rb ? oimo_rigid_body_get_linear_velocity(rb) : oimo_vec3_zero();
}

static inline void physics_set_angular_velocity(OimoRigidBody* rb, const OimoVec3* vel) {
    if (rb) oimo_rigid_body_set_angular_velocity(rb, vel);
}

static inline OimoVec3 physics_get_angular_velocity(const OimoRigidBody* rb) {
    return rb ? oimo_rigid_body_get_angular_velocity(rb) : oimo_vec3_zero();
}

static inline void physics_wake_up(OimoRigidBody* rb) {
    if (rb) oimo_rigid_body_wake_up(rb);
}

static inline void physics_disable_sleep(OimoRigidBody* rb) {
    if (rb) rb->_autoSleep = 0;
}

static inline void physics_set_mass(OimoRigidBody* rb, float mass) {
    if (rb) {
        rb->_mass = mass;
        oimo_rigid_body_update_mass(rb);
    }
}

#ifdef __cplusplus
}
#endif

#endif // PHYSICS_H
