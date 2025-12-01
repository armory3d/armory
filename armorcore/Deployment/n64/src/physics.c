#include "physics.h"
#include <stdlib.h>
#include <string.h>

static OimoWorld* g_world = NULL;
static bool g_paused = false;

void physics_init(void) {
    g_world = (OimoWorld*)malloc(sizeof(OimoWorld));
    if (g_world) {
        oimo_world_init(g_world);
        oimo_world_set_gravity(g_world, 0.0f, PHYSICS_DEFAULT_GRAVITY_Y, 0.0f);
    }
    g_paused = false;
}

void physics_shutdown(void) {
    if (g_world) {
        // TODO: Properly destroy all bodies and shapes
        free(g_world);
        g_world = NULL;
    }
}

void physics_reset(void) {
    // TODO: Clear all bodies from world
    if (g_world) {
        // For now, just reinitialize
        oimo_world_init(g_world);
    }
}

OimoWorld* physics_get_world(void) { return g_world; }

void physics_set_gravity(float x, float y, float z) {
    if (g_world) {
        oimo_world_set_gravity(g_world, x, y, z);
    }
}

void physics_set_paused(bool paused) { g_paused = paused; }
bool physics_is_paused(void) { return g_paused; }

void physics_step(float dt) {
    if (!g_world || g_paused) return;
    oimo_world_step(g_world, dt);
}

#include "types.h"
#include <math.h>

// N64 fixed-point safe range (avoid overflow in t3d_mat4_to_fixed)
#define PHYSICS_MAX_POS 1000.0f

static inline float clamp_position(float v) {
    if (isnan(v) || isinf(v)) return 0.0f;
    if (v > PHYSICS_MAX_POS) return PHYSICS_MAX_POS;
    if (v < -PHYSICS_MAX_POS) return -PHYSICS_MAX_POS;
    return v;
}

static inline float sanitize_quat(float v) {
    if (isnan(v) || isinf(v)) return 0.0f;
    return v;
}

void physics_sync_object(void* obj_ptr) {
    ArmObject* obj = (ArmObject*)obj_ptr;
    if (!obj || !obj->rigid_body) return;

    OimoRigidBody* rb = obj->rigid_body;

    // Get position from physics (with bounds checking for N64 fixed-point)
    OimoVec3 pos = oimo_rigidbody_get_position(rb);
    obj->transform.loc[0] = clamp_position(pos.v[0]);
    obj->transform.loc[1] = clamp_position(pos.v[1]);
    obj->transform.loc[2] = clamp_position(pos.v[2]);

    // Get rotation matrix from physics and convert to quaternion
    OimoMat3 rot_mat = oimo_rigidbody_get_rotation(rb);
    // Convert rotation matrix to quaternion
    // Using standard matrix-to-quaternion conversion
    float trace = rot_mat.e00 + rot_mat.e11 + rot_mat.e22;
    float qw, qx, qy, qz;

    if (trace > 0) {
        float s = 0.5f / sqrtf(trace + 1.0f);
        qw = 0.25f / s;
        qx = (rot_mat.e21 - rot_mat.e12) * s;
        qy = (rot_mat.e02 - rot_mat.e20) * s;
        qz = (rot_mat.e10 - rot_mat.e01) * s;
    } else if (rot_mat.e00 > rot_mat.e11 && rot_mat.e00 > rot_mat.e22) {
        float s = 2.0f * sqrtf(1.0f + rot_mat.e00 - rot_mat.e11 - rot_mat.e22);
        qw = (rot_mat.e21 - rot_mat.e12) / s;
        qx = 0.25f * s;
        qy = (rot_mat.e01 + rot_mat.e10) / s;
        qz = (rot_mat.e02 + rot_mat.e20) / s;
    } else if (rot_mat.e11 > rot_mat.e22) {
        float s = 2.0f * sqrtf(1.0f + rot_mat.e11 - rot_mat.e00 - rot_mat.e22);
        qw = (rot_mat.e02 - rot_mat.e20) / s;
        qx = (rot_mat.e01 + rot_mat.e10) / s;
        qy = 0.25f * s;
        qz = (rot_mat.e12 + rot_mat.e21) / s;
    } else {
        float s = 2.0f * sqrtf(1.0f + rot_mat.e22 - rot_mat.e00 - rot_mat.e11);
        qw = (rot_mat.e10 - rot_mat.e01) / s;
        qx = (rot_mat.e02 + rot_mat.e20) / s;
        qy = (rot_mat.e12 + rot_mat.e21) / s;
        qz = 0.25f * s;
    }

    obj->transform.rot[0] = sanitize_quat(qx);
    obj->transform.rot[1] = sanitize_quat(qy);
    obj->transform.rot[2] = sanitize_quat(qz);
    obj->transform.rot[3] = sanitize_quat(qw);

    // Ensure quaternion is valid (default to identity if all zero)
    if (obj->transform.rot[0] == 0.0f && obj->transform.rot[1] == 0.0f &&
        obj->transform.rot[2] == 0.0f && obj->transform.rot[3] == 0.0f) {
        obj->transform.rot[3] = 1.0f;
    }

    // Mark transform as dirty for rendering
    obj->transform.dirty = 3;
}

bool physics_raycast(const OimoVec3* from, const OimoVec3* direction, float max_distance, PhysicsRayHit* out_hit) {
    if (!g_world || !out_hit) return false;

    // TODO: Implement raycast using oimo_64
    // For now, return no hit
    out_hit->hit = false;
    return false;
}

