// physics.h - Mini-engine physics wrapper
#ifndef PHYSICS_H
#define PHYSICS_H

#include "types.h"
#include "oimo/oimo.h"

#ifdef __cplusplus
extern "C" {
#endif

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
void physics_create_box(ArmObject* obj, int type, float hx, float hy, float hz,
                        float mass, float friction, float restitution);
void physics_create_sphere(ArmObject* obj, int type, float radius,
                           float mass, float friction, float restitution);
void physics_remove_body(ArmObject* obj);

// Transform sync (call after physics_step)
void physics_sync_object(ArmObject* obj);

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
