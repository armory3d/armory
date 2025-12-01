#pragma once

#include <libdragon.h>
#include <stdbool.h>
#include "oimo_64/oimo_64.h"

#ifdef __cplusplus
extern "C" {
#endif

#define PHYSICS_DEFAULT_GRAVITY_Y (-9.81f)

void physics_init(void);
void physics_shutdown(void);
void physics_reset(void);

OimoWorld* physics_get_world(void);

void physics_set_gravity(float x, float y, float z);
void physics_set_paused(bool paused);
bool physics_is_paused(void);

void physics_step(float dt);

// Sync a single object's transform from its rigid body
void physics_sync_object(void* obj);

typedef struct {
    bool hit;
    OimoVec3 point;
    OimoVec3 normal;
    float distance;
    OimoRigidBody* body;
} PhysicsRayHit;

bool physics_raycast(const OimoVec3* from, const OimoVec3* direction, float max_distance, PhysicsRayHit* out_hit);

#ifdef __cplusplus
}
#endif
