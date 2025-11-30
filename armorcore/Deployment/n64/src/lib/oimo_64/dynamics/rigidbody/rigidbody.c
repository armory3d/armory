#include "rigidbody.h"
#include <stdlib.h>
#include <string.h>
#include <math.h>

// =============================================================================
// Constants
// =============================================================================

#define SLEEP_LINEAR_THRESHOLD  0.01f   // Linear velocity threshold for sleeping
#define SLEEP_ANGULAR_THRESHOLD 0.01f   // Angular velocity threshold for sleeping
#define SLEEP_TIME_THRESHOLD    0.5f    // Time below threshold before sleeping
#define PI 3.14159265358979323846f

// =============================================================================
// Shape Implementation
// =============================================================================

static Shape* shape_create(ShapeType type) {
    Shape* shape = (Shape*)malloc(sizeof(Shape));
    if (!shape) return NULL;

    memset(shape, 0, sizeof(Shape));
    shape->type = type;
    shape->localPosition = vec3_zero();
    shape->localRotation = mat3_identity();
    shape->collisionGroup = 1;
    shape->collisionMask = 0xFFFF;  // Collide with everything by default

    return shape;
}

Shape* shape_create_sphere(float radius) {
    Shape* shape = shape_create(SHAPE_SPHERE);
    if (shape) {
        shape->geom.sphere.radius = radius;
    }
    return shape;
}

Shape* shape_create_box(float halfX, float halfY, float halfZ) {
    Shape* shape = shape_create(SHAPE_BOX);
    if (shape) {
        shape->geom.box.halfExtents = vec3_new(halfX, halfY, halfZ);
    }
    return shape;
}

Shape* shape_create_box_vec(const Vec3* halfExtents) {
    return shape_create_box(halfExtents->x, halfExtents->y, halfExtents->z);
}

void shape_destroy(Shape* shape) {
    if (shape) {
        free(shape);
    }
}

void shape_set_collision_group(Shape* shape, uint16_t group) {
    shape->collisionGroup = group;
}

void shape_set_collision_mask(Shape* shape, uint16_t mask) {
    shape->collisionMask = mask;
}

void shape_set_local_position(Shape* shape, const Vec3* pos) {
    vec3_copy_from(&shape->localPosition, pos);
}

void shape_set_local_rotation(Shape* shape, const Mat3* rot) {
    mat3_copy_from(&shape->localRotation, rot);
}

void shape_update_aabb(Shape* shape) {
    if (!shape->body) return;

    // Get world position of shape center
    Vec3 worldPos = shape->localPosition;
    vec3_mul_transform(&worldPos, &shape->body->transform);

    switch (shape->type) {
        case SHAPE_SPHERE: {
            float r = shape->geom.sphere.radius;
            shape->aabbMin = vec3_new(worldPos.x - r, worldPos.y - r, worldPos.z - r);
            shape->aabbMax = vec3_new(worldPos.x + r, worldPos.y + r, worldPos.z + r);
            break;
        }
        case SHAPE_BOX: {
            // For rotated box, compute AABB from rotated corners
            // This is a simplified version - compute the max extent along each axis
            Vec3 half = shape->geom.box.halfExtents;

            // Get world rotation (body rotation * local rotation)
            Mat3 worldRot;
            mat3_copy_from(&worldRot, &shape->body->transform.rotation);
            mat3_mul(&worldRot, &shape->localRotation);

            // Compute AABB half-extents from rotated box
            // For each axis, the extent is the sum of absolute projections
            float ex = fabsf(worldRot.m[0][0]) * half.x + fabsf(worldRot.m[0][1]) * half.y + fabsf(worldRot.m[0][2]) * half.z;
            float ey = fabsf(worldRot.m[1][0]) * half.x + fabsf(worldRot.m[1][1]) * half.y + fabsf(worldRot.m[1][2]) * half.z;
            float ez = fabsf(worldRot.m[2][0]) * half.x + fabsf(worldRot.m[2][1]) * half.y + fabsf(worldRot.m[2][2]) * half.z;

            shape->aabbMin = vec3_new(worldPos.x - ex, worldPos.y - ey, worldPos.z - ez);
            shape->aabbMax = vec3_new(worldPos.x + ex, worldPos.y + ey, worldPos.z + ez);
            break;
        }
    }
}

void shape_compute_mass(const Shape* shape, float density, MassData* out) {
    out->localCenterOfMass = shape->localPosition;

    switch (shape->type) {
        case SHAPE_SPHERE: {
            float r = shape->geom.sphere.radius;
            float volume = (4.0f / 3.0f) * PI * r * r * r;
            out->mass = density * volume;

            // Inertia tensor for solid sphere: (2/5) * m * r^2
            float I = (2.0f / 5.0f) * out->mass * r * r;
            out->localInertia = mat3_new(I, 0, 0, 0, I, 0, 0, 0, I);
            break;
        }
        case SHAPE_BOX: {
            Vec3 h = shape->geom.box.halfExtents;
            float volume = 8.0f * h.x * h.y * h.z;  // (2h)^3
            out->mass = density * volume;

            // Inertia tensor for solid box: (1/12) * m * (h^2 + d^2) for each axis
            float m = out->mass;
            float w2 = 4.0f * h.x * h.x;  // Full width squared
            float h2 = 4.0f * h.y * h.y;
            float d2 = 4.0f * h.z * h.z;

            float Ixx = (1.0f / 12.0f) * m * (h2 + d2);
            float Iyy = (1.0f / 12.0f) * m * (w2 + d2);
            float Izz = (1.0f / 12.0f) * m * (w2 + h2);

            out->localInertia = mat3_new(Ixx, 0, 0, 0, Iyy, 0, 0, 0, Izz);
            break;
        }
    }
}

// =============================================================================
// RigidBody Implementation
// =============================================================================

RigidBody* rigidbody_create(void) {
    RigidBody* body = (RigidBody*)malloc(sizeof(RigidBody));
    if (!body) return NULL;

    memset(body, 0, sizeof(RigidBody));

    body->transform = transform_identity();
    body->linearVel = vec3_zero();
    body->angularVel = vec3_zero();
    body->force = vec3_zero();
    body->torque = vec3_zero();

    body->mass = 1.0f;
    body->invMass = 1.0f;
    body->localInertia = mat3_identity();
    body->invLocalInertia = mat3_identity();
    body->invWorldInertia = mat3_identity();

    body->linearDamping = 0.0f;
    body->angularDamping = 0.0f;
    body->gravityScale = 1.0f;
    body->rotationFactor = vec3_new(1.0f, 1.0f, 1.0f);

    body->type = RIGIDBODY_DYNAMIC;
    body->autoSleep = true;
    body->sleeping = false;
    body->sleepTime = 0.0f;

    return body;
}

void rigidbody_destroy(RigidBody* body) {
    if (!body) return;

    // Destroy all shapes
    Shape* shape = body->shapeList;
    while (shape) {
        Shape* next = shape->next;
        shape_destroy(shape);
        shape = next;
    }

    free(body);
}

void rigidbody_set_type(RigidBody* body, RigidBodyType type) {
    if (body->type == type) return;

    body->type = type;

    if (type == RIGIDBODY_STATIC || type == RIGIDBODY_KINEMATIC) {
        body->invMass = 0.0f;
        body->invLocalInertia = mat3_new(0,0,0, 0,0,0, 0,0,0);
        body->invWorldInertia = mat3_new(0,0,0, 0,0,0, 0,0,0);
        body->linearVel = vec3_zero();
        body->angularVel = vec3_zero();
    } else {
        // Recompute mass from shapes
        rigidbody_update_mass(body);
    }
}

RigidBodyType rigidbody_get_type(const RigidBody* body) {
    return body->type;
}

// Transform functions

void rigidbody_get_position(const RigidBody* body, Vec3* out) {
    *out = body->transform.position;
}

void rigidbody_set_position(RigidBody* body, const Vec3* pos) {
    body->transform.position = *pos;
    rigidbody_wake_up(body);
}

void rigidbody_translate(RigidBody* body, const Vec3* translation) {
    vec3_add(&body->transform.position, translation);
    rigidbody_wake_up(body);
}

void rigidbody_get_rotation(const RigidBody* body, Mat3* out) {
    *out = body->transform.rotation;
}

void rigidbody_set_rotation(RigidBody* body, const Mat3* rot) {
    body->transform.rotation = *rot;
    rigidbody_update_world_inertia(body);
    rigidbody_wake_up(body);
}

void rigidbody_set_rotation_xyz(RigidBody* body, const Vec3* euler) {
    body->transform.rotation = mat3_from_euler_xyz(euler);
    rigidbody_update_world_inertia(body);
    rigidbody_wake_up(body);
}

void rigidbody_rotate(RigidBody* body, const Mat3* rot) {
    mat3_mul(&body->transform.rotation, rot);
    rigidbody_update_world_inertia(body);
    rigidbody_wake_up(body);
}

void rigidbody_rotate_xyz(RigidBody* body, const Vec3* euler) {
    Mat3 rot = mat3_from_euler_xyz(euler);
    mat3_mul(&body->transform.rotation, &rot);
    rigidbody_update_world_inertia(body);
    rigidbody_wake_up(body);
}

void rigidbody_get_orientation(const RigidBody* body, Quat* out) {
    *out = mat3_to_quat(&body->transform.rotation);
}

void rigidbody_set_orientation(RigidBody* body, const Quat* q) {
    Quat qCopy = *q;
    body->transform.rotation = mat3_from_quat(&qCopy);
    rigidbody_update_world_inertia(body);
    rigidbody_wake_up(body);
}

void rigidbody_get_transform(const RigidBody* body, Transform* out) {
    *out = body->transform;
}

void rigidbody_set_transform(RigidBody* body, const Transform* t) {
    body->transform = *t;
    rigidbody_update_world_inertia(body);
    rigidbody_wake_up(body);
}

// Velocity functions

void rigidbody_get_linear_velocity(const RigidBody* body, Vec3* out) {
    *out = body->linearVel;
}

void rigidbody_set_linear_velocity(RigidBody* body, const Vec3* vel) {
    if (body->type == RIGIDBODY_STATIC) return;
    body->linearVel = *vel;
    rigidbody_wake_up(body);
}

void rigidbody_add_linear_velocity(RigidBody* body, const Vec3* vel) {
    if (body->type == RIGIDBODY_STATIC) return;
    vec3_add(&body->linearVel, vel);
    rigidbody_wake_up(body);
}

void rigidbody_get_angular_velocity(const RigidBody* body, Vec3* out) {
    *out = body->angularVel;
}

void rigidbody_set_angular_velocity(RigidBody* body, const Vec3* vel) {
    if (body->type == RIGIDBODY_STATIC) return;
    body->angularVel = *vel;
    rigidbody_wake_up(body);
}

void rigidbody_add_angular_velocity(RigidBody* body, const Vec3* vel) {
    if (body->type == RIGIDBODY_STATIC) return;
    vec3_add(&body->angularVel, vel);
    rigidbody_wake_up(body);
}

// Force and impulse functions

void rigidbody_apply_force(RigidBody* body, const Vec3* force, const Vec3* worldPoint) {
    if (body->type != RIGIDBODY_DYNAMIC) return;

    // Force at center
    vec3_add(&body->force, force);

    // Torque = r x F where r is from center of mass to world point
    Vec3 r = *worldPoint;
    vec3_sub(&r, &body->transform.position);
    Vec3 t = vec3_cross(&r, force);
    vec3_add(&body->torque, &t);

    rigidbody_wake_up(body);
}

void rigidbody_apply_force_to_center(RigidBody* body, const Vec3* force) {
    if (body->type != RIGIDBODY_DYNAMIC) return;
    vec3_add(&body->force, force);
    rigidbody_wake_up(body);
}

void rigidbody_apply_torque(RigidBody* body, const Vec3* torque) {
    if (body->type != RIGIDBODY_DYNAMIC) return;
    vec3_add(&body->torque, torque);
    rigidbody_wake_up(body);
}

void rigidbody_apply_impulse(RigidBody* body, const Vec3* impulse, const Vec3* worldPoint) {
    if (body->type != RIGIDBODY_DYNAMIC) return;

    // Linear impulse
    Vec3 dv = *impulse;
    vec3_scale(&dv, body->invMass);
    vec3_add(&body->linearVel, &dv);

    // Angular impulse = I^-1 * (r x impulse)
    Vec3 r = *worldPoint;
    vec3_sub(&r, &body->transform.position);
    Vec3 angImpulse = vec3_cross(&r, impulse);
    vec3_mul_mat3(&angImpulse, &body->invWorldInertia);
    vec3_add(&body->angularVel, &angImpulse);

    rigidbody_wake_up(body);
}

void rigidbody_apply_linear_impulse(RigidBody* body, const Vec3* impulse) {
    if (body->type != RIGIDBODY_DYNAMIC) return;

    Vec3 dv = *impulse;
    vec3_scale(&dv, body->invMass);
    vec3_add(&body->linearVel, &dv);

    rigidbody_wake_up(body);
}

void rigidbody_apply_angular_impulse(RigidBody* body, const Vec3* impulse) {
    if (body->type != RIGIDBODY_DYNAMIC) return;

    Vec3 angImpulse = *impulse;
    vec3_mul_mat3(&angImpulse, &body->invWorldInertia);
    vec3_add(&body->angularVel, &angImpulse);

    rigidbody_wake_up(body);
}

// Mass functions

float rigidbody_get_mass(const RigidBody* body) {
    return (body->invMass > 0.0f) ? body->mass : 0.0f;
}

void rigidbody_set_mass_data(RigidBody* body, const MassData* data) {
    if (body->type != RIGIDBODY_DYNAMIC) return;

    body->mass = data->mass;
    body->invMass = (data->mass > 0.0f) ? 1.0f / data->mass : 0.0f;
    body->localInertia = data->localInertia;

    // Compute inverse inertia
    body->invLocalInertia = data->localInertia;
    mat3_inverse(&body->invLocalInertia);

    rigidbody_update_world_inertia(body);
}

void rigidbody_get_mass_data(const RigidBody* body, MassData* out) {
    out->mass = body->mass;
    out->localCenterOfMass = vec3_zero();  // Simplified - assume center
    out->localInertia = body->localInertia;
}

void rigidbody_get_local_inertia(const RigidBody* body, Mat3* out) {
    *out = body->localInertia;
}

// Shape functions

void rigidbody_add_shape(RigidBody* body, Shape* shape) {
    if (!shape || shape->body) return;

    shape->body = body;
    shape->next = body->shapeList;
    body->shapeList = shape;
    body->numShapes++;

    // Recompute mass
    rigidbody_update_mass(body);

    // Update AABB
    shape_update_aabb(shape);
}

void rigidbody_remove_shape(RigidBody* body, Shape* shape) {
    if (!shape || shape->body != body) return;

    // Find and remove from list
    Shape** ptr = &body->shapeList;
    while (*ptr) {
        if (*ptr == shape) {
            *ptr = shape->next;
            shape->body = NULL;
            shape->next = NULL;
            body->numShapes--;
            break;
        }
        ptr = &(*ptr)->next;
    }

    // Recompute mass
    rigidbody_update_mass(body);
}

Shape* rigidbody_get_shape_list(const RigidBody* body) {
    return body->shapeList;
}

int rigidbody_get_num_shapes(const RigidBody* body) {
    return body->numShapes;
}

void rigidbody_update_mass(RigidBody* body) {
    if (body->type != RIGIDBODY_DYNAMIC) return;

    if (body->numShapes == 0) {
        body->mass = 1.0f;
        body->invMass = 1.0f;
        body->localInertia = mat3_identity();
        body->invLocalInertia = mat3_identity();
        rigidbody_update_world_inertia(body);
        return;
    }

    // Accumulate mass data from all shapes
    // Use density of 1.0 - shapes are assumed to have uniform density
    float totalMass = 0.0f;
    Mat3 totalInertia = mat3_new(0,0,0, 0,0,0, 0,0,0);

    for (Shape* s = body->shapeList; s; s = s->next) {
        MassData md;
        shape_compute_mass(s, 1.0f, &md);
        totalMass += md.mass;
        mat3_add(&totalInertia, &md.localInertia);
    }

    body->mass = totalMass;
    body->invMass = (totalMass > 0.0f) ? 1.0f / totalMass : 0.0f;
    body->localInertia = totalInertia;

    // Compute inverse
    body->invLocalInertia = totalInertia;
    mat3_inverse(&body->invLocalInertia);

    rigidbody_update_world_inertia(body);
}

// Damping functions

void rigidbody_set_linear_damping(RigidBody* body, float damping) {
    body->linearDamping = damping;
}

float rigidbody_get_linear_damping(const RigidBody* body) {
    return body->linearDamping;
}

void rigidbody_set_angular_damping(RigidBody* body, float damping) {
    body->angularDamping = damping;
}

float rigidbody_get_angular_damping(const RigidBody* body) {
    return body->angularDamping;
}

// Gravity functions

void rigidbody_set_gravity_scale(RigidBody* body, float scale) {
    body->gravityScale = scale;
}

float rigidbody_get_gravity_scale(const RigidBody* body) {
    return body->gravityScale;
}

// Rotation factor functions

void rigidbody_set_rotation_factor(RigidBody* body, const Vec3* factor) {
    body->rotationFactor = *factor;
}

void rigidbody_get_rotation_factor(const RigidBody* body, Vec3* out) {
    *out = body->rotationFactor;
}

// Sleep functions

void rigidbody_sleep(RigidBody* body) {
    if (body->type == RIGIDBODY_STATIC) return;
    body->sleeping = true;
    body->sleepTime = 0.0f;
    body->linearVel = vec3_zero();
    body->angularVel = vec3_zero();
}

void rigidbody_wake_up(RigidBody* body) {
    if (body->type == RIGIDBODY_STATIC) return;
    body->sleeping = false;
    body->sleepTime = 0.0f;
}

bool rigidbody_is_sleeping(const RigidBody* body) {
    return body->sleeping;
}

void rigidbody_set_auto_sleep(RigidBody* body, bool enabled) {
    body->autoSleep = enabled;
    if (!enabled) {
        rigidbody_wake_up(body);
    }
}

float rigidbody_get_sleep_time(const RigidBody* body) {
    return body->sleepTime;
}

// Coordinate conversion

void rigidbody_get_world_point(const RigidBody* body, const Vec3* localPoint, Vec3* worldPoint) {
    *worldPoint = *localPoint;
    vec3_mul_transform(worldPoint, &body->transform);
}

void rigidbody_get_local_point(const RigidBody* body, const Vec3* worldPoint, Vec3* localPoint) {
    *localPoint = *worldPoint;
    vec3_sub(localPoint, &body->transform.position);

    // Multiply by inverse rotation (transpose of rotation matrix)
    Mat3 invRot = body->transform.rotation;
    mat3_transpose(&invRot);
    vec3_mul_mat3(localPoint, &invRot);
}

void rigidbody_get_world_vector(const RigidBody* body, const Vec3* localVec, Vec3* worldVec) {
    *worldVec = *localVec;
    vec3_mul_mat3(worldVec, &body->transform.rotation);
}

void rigidbody_get_local_vector(const RigidBody* body, const Vec3* worldVec, Vec3* localVec) {
    Mat3 invRot = body->transform.rotation;
    mat3_transpose(&invRot);
    *localVec = *worldVec;
    vec3_mul_mat3(localVec, &invRot);
}

// Linked list navigation

RigidBody* rigidbody_get_next(const RigidBody* body) {
    return body->next;
}

RigidBody* rigidbody_get_prev(const RigidBody* body) {
    return body->prev;
}

// Internal functions

void rigidbody_update_world_inertia(RigidBody* body) {
    if (body->type != RIGIDBODY_DYNAMIC) {
        body->invWorldInertia = mat3_new(0,0,0, 0,0,0, 0,0,0);
        return;
    }

    // I_world^-1 = R * I_local^-1 * R^T
    Mat3 R = body->transform.rotation;
    Mat3 RT = body->transform.rotation;
    mat3_transpose(&RT);

    // invWorldInertia = R * invLocalInertia * RT
    body->invWorldInertia = body->invLocalInertia;

    // Premultiply by R
    Mat3 temp = R;
    mat3_mul(&temp, &body->invWorldInertia);

    // Postmultiply by RT
    mat3_mul(&temp, &RT);

    body->invWorldInertia = temp;

    // Apply rotation factor
    body->invWorldInertia.m[0][0] *= body->rotationFactor.x;
    body->invWorldInertia.m[1][1] *= body->rotationFactor.y;
    body->invWorldInertia.m[2][2] *= body->rotationFactor.z;
}

void rigidbody_integrate_velocity(RigidBody* body, float dt, const Vec3* gravity) {
    if (body->type != RIGIDBODY_DYNAMIC || body->sleeping) return;

    // Apply gravity
    Vec3 grav = *gravity;
    vec3_scale(&grav, body->gravityScale * dt);
    vec3_add(&body->linearVel, &grav);

    // Apply forces: a = F / m
    Vec3 acc = body->force;
    vec3_scale(&acc, body->invMass * dt);
    vec3_add(&body->linearVel, &acc);

    // Apply torques: alpha = I^-1 * torque
    Vec3 angAcc = body->torque;
    vec3_mul_mat3(&angAcc, &body->invWorldInertia);
    vec3_scale(&angAcc, dt);
    vec3_add(&body->angularVel, &angAcc);

    // Apply damping
    float linearDamp = 1.0f - body->linearDamping * dt;
    float angularDamp = 1.0f - body->angularDamping * dt;
    if (linearDamp < 0.0f) linearDamp = 0.0f;
    if (angularDamp < 0.0f) angularDamp = 0.0f;

    vec3_scale(&body->linearVel, linearDamp);
    vec3_scale(&body->angularVel, angularDamp);

    // Clear forces for next frame
    body->force = vec3_zero();
    body->torque = vec3_zero();
}

void rigidbody_integrate_position(RigidBody* body, float dt) {
    if (body->type == RIGIDBODY_STATIC || body->sleeping) return;

    // Update position: p += v * dt
    Vec3 dp = body->linearVel;
    vec3_scale(&dp, dt);
    vec3_add(&body->transform.position, &dp);

    // Update rotation: q += 0.5 * w * q * dt
    // Using small angle approximation for efficiency
    Vec3 dw = body->angularVel;
    vec3_scale(&dw, dt);

    float angle = vec3_length(&dw);
    if (angle > 0.0001f) {
        Vec3 axis = dw;
        vec3_scale(&axis, 1.0f / angle);

        // Create rotation quaternion
        float halfAngle = angle * 0.5f;
        float s = sinf(halfAngle);
        Quat dq = {{axis.x * s, axis.y * s, axis.z * s, cosf(halfAngle)}};

        // Get current orientation and multiply
        Quat q = transform_get_orientation(&body->transform);

        // q = dq * q (rotate in world space)
        Quat result;
        result.x = dq.w * q.x + dq.x * q.w + dq.y * q.z - dq.z * q.y;
        result.y = dq.w * q.y - dq.x * q.z + dq.y * q.w + dq.z * q.x;
        result.z = dq.w * q.z + dq.x * q.y - dq.y * q.x + dq.z * q.w;
        result.w = dq.w * q.w - dq.x * q.x - dq.y * q.y - dq.z * q.z;

        // Normalize
        float len = sqrtf(result.x*result.x + result.y*result.y + result.z*result.z + result.w*result.w);
        if (len > 0.0f) {
            result.x /= len;
            result.y /= len;
            result.z /= len;
            result.w /= len;
        }

        transform_set_orientation(&body->transform, &result);
    }

    // Update world inertia tensor
    rigidbody_update_world_inertia(body);

    // Check for sleeping
    if (body->autoSleep) {
        float linVelSq = vec3_length_sq(&body->linearVel);
        float angVelSq = vec3_length_sq(&body->angularVel);

        if (linVelSq < SLEEP_LINEAR_THRESHOLD * SLEEP_LINEAR_THRESHOLD &&
            angVelSq < SLEEP_ANGULAR_THRESHOLD * SLEEP_ANGULAR_THRESHOLD) {
            body->sleepTime += dt;
            if (body->sleepTime > SLEEP_TIME_THRESHOLD) {
                rigidbody_sleep(body);
            }
        } else {
            body->sleepTime = 0.0f;
        }
    }
}

void rigidbody_update_shapes(RigidBody* body) {
    for (Shape* s = body->shapeList; s; s = s->next) {
        shape_update_aabb(s);
    }
}
