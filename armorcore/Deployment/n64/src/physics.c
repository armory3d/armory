#include "physics.h"
#include <stdlib.h>
#include <string.h>

static World* g_world = NULL;
static bool g_paused = false;

void physics_init(void) {
    g_world = world_create_default();
    if (g_world) {
        physics_set_gravity(0.0f, PHYSICS_DEFAULT_GRAVITY_Y, 0.0f);
    }
    g_paused = false;
}

void physics_shutdown(void) {
    if (g_world) {
        world_destroy(g_world);
        g_world = NULL;
    }
}

void physics_reset(void) {
    if (g_world) world_clear(g_world);
}

World* physics_get_world(void) { return g_world; }

void physics_set_gravity(float x, float y, float z) {
    if (g_world) {
        Vec3 grav = vec3_new(x, y, z);
        world_set_gravity(g_world, &grav);
    }
}

void physics_set_paused(bool paused) { g_paused = paused; }
bool physics_is_paused(void) { return g_paused; }

void physics_step(float dt) {
    if (!g_world || g_paused) return;
    world_step(g_world, dt);
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

    RigidBody* rb = obj->rigid_body;

    // Get position from physics (with bounds checking for N64 fixed-point)
    Vec3 pos;
    rigidbody_get_position(rb, &pos);
    obj->transform.loc[0] = clamp_position(pos.x);
    obj->transform.loc[1] = clamp_position(pos.y);
    obj->transform.loc[2] = clamp_position(pos.z);

    // Get orientation from physics (sanitize for NaN)
    Quat rot;
    rigidbody_get_orientation(rb, &rot);
    obj->transform.rot[0] = sanitize_quat(rot.x);
    obj->transform.rot[1] = sanitize_quat(rot.y);
    obj->transform.rot[2] = sanitize_quat(rot.z);
    obj->transform.rot[3] = sanitize_quat(rot.w);

    // Ensure quaternion is valid (default to identity if all zero)
    if (obj->transform.rot[0] == 0.0f && obj->transform.rot[1] == 0.0f &&
        obj->transform.rot[2] == 0.0f && obj->transform.rot[3] == 0.0f) {
        obj->transform.rot[3] = 1.0f;
    }

    // Mark transform as dirty for rendering
    obj->transform.dirty = 3;
}

bool physics_raycast(const Vec3* from, const Vec3* direction, float max_distance, PhysicsRayHit* out_hit) {
    if (!g_world || !out_hit) return false;

    Vec3 to = *from;
    vec3_add_scaled(&to, direction, max_distance);

    RaycastHit hit;
    if (!world_raycast_closest(g_world, from, &to, &hit)) {
        out_hit->hit = false;
        return false;
    }

    out_hit->hit = true;
    out_hit->point = hit.position;
    out_hit->normal = hit.normal;
    out_hit->distance = hit.fraction * max_distance;
    out_hit->body = hit.body;
    return true;
}
