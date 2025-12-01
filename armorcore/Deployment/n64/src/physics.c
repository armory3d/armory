// physics.c - Mini-engine physics implementation
#include "physics.h"
#include <string.h>

// Static pools
static OimoWorld g_world;
static bool g_paused = false;
static bool g_initialized = false;

#define MAX_PHYSICS_BODIES 32
static OimoRigidBody g_bodies[MAX_PHYSICS_BODIES];
static bool g_body_used[MAX_PHYSICS_BODIES];
static OimoShape g_shapes[MAX_PHYSICS_BODIES];

typedef union {
    OimoSphereGeometry sphere;
    OimoBoxGeometry box;
} GeometryUnion;
static GeometryUnion g_geometries[MAX_PHYSICS_BODIES];

// Pool helpers
static OimoRigidBody* alloc_body(void) {
    for (int i = 0; i < MAX_PHYSICS_BODIES; i++) {
        if (!g_body_used[i]) {
            g_body_used[i] = true;
            return &g_bodies[i];
        }
    }
    return NULL;
}

static void free_body(OimoRigidBody* rb) {
    for (int i = 0; i < MAX_PHYSICS_BODIES; i++) {
        if (&g_bodies[i] == rb) {
            g_body_used[i] = false;
            return;
        }
    }
}

static int get_body_index(OimoRigidBody* rb) {
    for (int i = 0; i < MAX_PHYSICS_BODIES; i++) {
        if (&g_bodies[i] == rb) return i;
    }
    return -1;
}

// World management
void physics_init(void) {
    if (g_initialized) return;

    memset(g_bodies, 0, sizeof(g_bodies));
    memset(g_body_used, 0, sizeof(g_body_used));
    memset(g_shapes, 0, sizeof(g_shapes));
    memset(g_geometries, 0, sizeof(g_geometries));

    OimoVec3 gravity = oimo_vec3(0.0f, -9.80665f, 0.0f);
    oimo_world_init(&g_world, &gravity);

    g_paused = false;
    g_initialized = true;
}

void physics_shutdown(void) {
    if (!g_initialized) return;
    physics_reset();
    g_initialized = false;
}

void physics_reset(void) {
    if (!g_initialized) return;

    for (int i = 0; i < MAX_PHYSICS_BODIES; i++) {
        if (g_body_used[i]) {
            oimo_world_remove_rigid_body(&g_world, &g_bodies[i]);
            g_body_used[i] = false;
        }
    }

    OimoVec3 gravity = g_world._gravity;
    oimo_world_init(&g_world, &gravity);
}

void physics_step(float dt) {
    if (!g_initialized || g_paused) return;
    oimo_world_step(&g_world, dt);
}

void physics_pause(void) { g_paused = true; }
void physics_resume(void) { g_paused = false; }
OimoWorld* physics_get_world(void) { return &g_world; }

// Gravity
void physics_set_gravity(float x, float y, float z) {
    if (!g_initialized) return;
    oimo_world_set_gravity(&g_world, oimo_vec3(x, y, z));
}

OimoVec3 physics_get_gravity(void) {
    return g_initialized ? oimo_world_get_gravity(&g_world) : oimo_vec3_zero();
}

// Body creation
void physics_create_box(ArmObject* obj, int type, float hx, float hy, float hz,
                        float mass, float friction, float restitution) {
    if (!g_initialized || !obj) return;

    OimoRigidBody* rb = alloc_body();
    if (!rb) return;

    int idx = get_body_index(rb);

    // Body config
    OimoRigidBodyConfig config = oimo_rigid_body_config();
    config.type = type;
    config.position = oimo_vec3(obj->transform.loc[0], obj->transform.loc[1], obj->transform.loc[2]);
    OimoQuat q = oimo_quat(obj->transform.rot[0], obj->transform.rot[1],
                           obj->transform.rot[2], obj->transform.rot[3]);
    config.rotation = oimo_quat_to_mat3(&q);
    config.autoSleep = (type == OIMO_RIGID_BODY_DYNAMIC);
    oimo_rigid_body_init(rb, &config);

    // Geometry & shape
    oimo_box_geometry_init3(&g_geometries[idx].box, hx, hy, hz);

    OimoShapeConfig shapeConfig = oimo_shape_config();
    shapeConfig.geometry = &g_geometries[idx].box.base;
    shapeConfig.friction = friction;
    shapeConfig.restitution = restitution;
    shapeConfig.density = (type == OIMO_RIGID_BODY_STATIC) ? 0.0f : (mass / (8.0f * hx * hy * hz));

    oimo_shape_init(&g_shapes[idx], &shapeConfig);
    oimo_rigid_body_add_shape(rb, &g_shapes[idx]);

    oimo_world_add_rigid_body(&g_world, rb);
    obj->rigid_body = rb;
}

void physics_create_sphere(ArmObject* obj, int type, float radius,
                           float mass, float friction, float restitution) {
    if (!g_initialized || !obj) return;

    OimoRigidBody* rb = alloc_body();
    if (!rb) return;

    int idx = get_body_index(rb);

    // Body config
    OimoRigidBodyConfig config = oimo_rigid_body_config();
    config.type = type;
    config.position = oimo_vec3(obj->transform.loc[0], obj->transform.loc[1], obj->transform.loc[2]);
    OimoQuat q = oimo_quat(obj->transform.rot[0], obj->transform.rot[1],
                           obj->transform.rot[2], obj->transform.rot[3]);
    config.rotation = oimo_quat_to_mat3(&q);
    config.autoSleep = (type == OIMO_RIGID_BODY_DYNAMIC);
    oimo_rigid_body_init(rb, &config);

    // Geometry & shape
    oimo_sphere_geometry_init(&g_geometries[idx].sphere, radius);

    OimoShapeConfig shapeConfig = oimo_shape_config();
    shapeConfig.geometry = &g_geometries[idx].sphere.base;
    shapeConfig.friction = friction;
    shapeConfig.restitution = restitution;
    float volume = (4.0f / 3.0f) * 3.14159265f * radius * radius * radius;
    shapeConfig.density = (type == OIMO_RIGID_BODY_STATIC) ? 0.0f : (mass / volume);

    oimo_shape_init(&g_shapes[idx], &shapeConfig);
    oimo_rigid_body_add_shape(rb, &g_shapes[idx]);

    oimo_world_add_rigid_body(&g_world, rb);
    obj->rigid_body = rb;
}

void physics_remove_body(ArmObject* obj) {
    if (!g_initialized || !obj || !obj->rigid_body) return;

    oimo_world_remove_rigid_body(&g_world, obj->rigid_body);
    free_body(obj->rigid_body);
    obj->rigid_body = NULL;
}

// Transform sync
void physics_sync_object(ArmObject* obj) {
    if (!obj || !obj->rigid_body) return;

    OimoRigidBody* rb = obj->rigid_body;
    if (rb->_type == OIMO_RIGID_BODY_STATIC || rb->_sleeping) return;

    OimoVec3 pos = oimo_rigid_body_get_position(rb);
    obj->transform.loc[0] = pos.x;
    obj->transform.loc[1] = pos.y;
    obj->transform.loc[2] = pos.z;

    OimoQuat rot = oimo_rigid_body_get_orientation(rb);
    obj->transform.rot[0] = rot.x;
    obj->transform.rot[1] = rot.y;
    obj->transform.rot[2] = rot.z;
    obj->transform.rot[3] = rot.w;

    obj->transform.dirty = 3;
}

