#include "world.h"
#include <stdlib.h>
#include <string.h>
#include <math.h>

// =============================================================================
// Constants
// =============================================================================

#define MAX_CONTACTS_PER_PAIR 4
#define CONTACT_POOL_INITIAL_SIZE 64
#define COLLISION_EPSILON 0.0001f

// =============================================================================
// Helper Functions
// =============================================================================

static float clampf(float v, float lo, float hi) {
    if (v < lo) return lo;
    if (v > hi) return hi;
    return v;
}

static float minf(float a, float b) { return a < b ? a : b; }
static float maxf(float a, float b) { return a > b ? a : b; }
static float absf(float a) { return a < 0 ? -a : a; }

// =============================================================================
// Contact Pool Management
// =============================================================================

static Contact* contact_alloc(World* world) {
    Contact* c;

    if (world->contactPool) {
        // Reuse from pool
        c = world->contactPool;
        world->contactPool = c->next;
        world->contactPoolSize--;
    } else {
        // Allocate new
        c = (Contact*)malloc(sizeof(Contact));
    }

    if (c) {
        memset(c, 0, sizeof(Contact));
    }
    return c;
}

static void contact_free(World* world, Contact* c) {
    // Return to pool
    c->next = world->contactPool;
    c->prev = NULL;
    world->contactPool = c;
    world->contactPoolSize++;
}

// =============================================================================
// World Implementation
// =============================================================================

World* world_create(const WorldConfig* config) {
    World* world = (World*)malloc(sizeof(World));
    if (!world) return NULL;

    memset(world, 0, sizeof(World));

    if (config) {
        world->gravity = config->gravity;
        world->velocityIterations = config->velocityIterations;
        world->positionIterations = config->positionIterations;
        world->allowSleep = config->allowSleep;
    } else {
        world->gravity = vec3_new(0.0f, -9.81f, 0.0f);
        world->velocityIterations = 8;
        world->positionIterations = 3;
        world->allowSleep = true;
    }

    return world;
}

World* world_create_default(void) {
    return world_create(NULL);
}

void world_destroy(World* world) {
    if (!world) return;

    world_clear(world);

    // Free contact pool
    while (world->contactPool) {
        Contact* next = world->contactPool->next;
        free(world->contactPool);
        world->contactPool = next;
    }

    free(world);
}

void world_set_gravity(World* world, const Vec3* gravity) {
    world->gravity = *gravity;
}

void world_get_gravity(const World* world, Vec3* out) {
    *out = world->gravity;
}

void world_add_body(World* world, RigidBody* body) {
    if (!body || body->world) return;

    body->world = world;
    body->prev = NULL;
    body->next = world->bodyList;

    if (world->bodyList) {
        world->bodyList->prev = body;
    }
    world->bodyList = body;
    world->numBodies++;

    // Update shape AABBs
    rigidbody_update_shapes(body);
}

void world_remove_body(World* world, RigidBody* body) {
    if (!body || body->world != world) return;

    // Remove any contacts involving this body
    Contact* c = world->contactList;
    while (c) {
        Contact* next = c->next;
        if (c->body1 == body || c->body2 == body) {
            // Remove from list
            if (c->prev) c->prev->next = c->next;
            else world->contactList = c->next;
            if (c->next) c->next->prev = c->prev;
            world->numContacts--;

            // Fire callback
            if (c->isTouching && world->onContactEnd) {
                world->onContactEnd(c, world->callbackUserData);
            }

            contact_free(world, c);
        }
        c = next;
    }

    // Remove from body list
    if (body->prev) body->prev->next = body->next;
    else world->bodyList = body->next;
    if (body->next) body->next->prev = body->prev;

    body->world = NULL;
    body->prev = NULL;
    body->next = NULL;
    world->numBodies--;
}

RigidBody* world_get_body_list(const World* world) {
    return world->bodyList;
}

int world_get_num_bodies(const World* world) {
    return world->numBodies;
}

// =============================================================================
// Collision Detection
// =============================================================================

bool collision_should_collide(const Shape* a, const Shape* b) {
    return (a->collisionGroup & b->collisionMask) &&
           (b->collisionGroup & a->collisionMask);
}

bool collision_test_aabb(const Shape* a, const Shape* b) {
    return !(a->aabbMax.x < b->aabbMin.x || a->aabbMin.x > b->aabbMax.x ||
             a->aabbMax.y < b->aabbMin.y || a->aabbMin.y > b->aabbMax.y ||
             a->aabbMax.z < b->aabbMin.z || a->aabbMin.z > b->aabbMax.z);
}

bool collision_sphere_sphere(const Shape* a, const Shape* b, ContactPoint* out) {
    // Get world positions
    Vec3 posA = a->localPosition;
    vec3_mul_transform(&posA, &a->body->transform);

    Vec3 posB = b->localPosition;
    vec3_mul_transform(&posB, &b->body->transform);

    float rA = a->geom.sphere.radius;
    float rB = b->geom.sphere.radius;

    // Vector from A to B
    Vec3 d = posB;
    vec3_sub(&d, &posA);

    float distSq = vec3_length_sq(&d);
    float radiusSum = rA + rB;

    if (distSq > radiusSum * radiusSum) {
        return false;  // No collision
    }

    float dist = sqrtf(distSq);

    if (dist > COLLISION_EPSILON) {
        // Normal from A to B
        out->normal = d;
        vec3_scale(&out->normal, 1.0f / dist);
    } else {
        // Spheres at same position, use arbitrary normal
        out->normal = vec3_new(0.0f, 1.0f, 0.0f);
        dist = 0.0f;
    }

    out->penetration = radiusSum - dist;

    // Contact point at midpoint of overlapping region
    out->position = posA;
    vec3_add_scaled(&out->position, &out->normal, rA - out->penetration * 0.5f);

    return true;
}

bool collision_sphere_box(const Shape* sphere, const Shape* box, ContactPoint* out) {
    // Get sphere center in box's local space
    Vec3 sphereWorld = sphere->localPosition;
    vec3_mul_transform(&sphereWorld, &sphere->body->transform);

    Vec3 boxWorld = box->localPosition;
    vec3_mul_transform(&boxWorld, &box->body->transform);

    // Transform sphere center to box local space
    Vec3 localSphere = sphereWorld;
    vec3_sub(&localSphere, &boxWorld);

    // Get box rotation (world rotation * local rotation)
    Mat3 boxRot;
    mat3_copy_from(&boxRot, &box->body->transform.rotation);
    mat3_mul(&boxRot, &box->localRotation);

    // Inverse rotation
    Mat3 invBoxRot = boxRot;
    mat3_transpose(&invBoxRot);

    // Sphere center in box local space
    vec3_mul_mat3(&localSphere, &invBoxRot);

    Vec3 half = box->geom.box.halfExtents;
    float radius = sphere->geom.sphere.radius;

    // Find closest point on box to sphere center
    Vec3 closest;
    closest.x = clampf(localSphere.x, -half.x, half.x);
    closest.y = clampf(localSphere.y, -half.y, half.y);
    closest.z = clampf(localSphere.z, -half.z, half.z);

    // Vector from closest point to sphere center
    Vec3 diff = localSphere;
    vec3_sub(&diff, &closest);

    float distSq = vec3_length_sq(&diff);

    if (distSq > radius * radius) {
        return false;  // No collision
    }

    float dist = sqrtf(distSq);

    // Normal in local space
    Vec3 localNormal;
    if (dist > COLLISION_EPSILON) {
        localNormal = diff;
        vec3_scale(&localNormal, 1.0f / dist);
    } else {
        // Sphere center is inside box - find closest face
        float dx = half.x - absf(localSphere.x);
        float dy = half.y - absf(localSphere.y);
        float dz = half.z - absf(localSphere.z);

        if (dx < dy && dx < dz) {
            localNormal = vec3_new(localSphere.x > 0 ? 1.0f : -1.0f, 0.0f, 0.0f);
            dist = -dx;
        } else if (dy < dz) {
            localNormal = vec3_new(0.0f, localSphere.y > 0 ? 1.0f : -1.0f, 0.0f);
            dist = -dy;
        } else {
            localNormal = vec3_new(0.0f, 0.0f, localSphere.z > 0 ? 1.0f : -1.0f);
            dist = -dz;
        }
    }

    // Transform normal back to world space
    out->normal = localNormal;
    vec3_mul_mat3(&out->normal, &boxRot);

    out->penetration = radius - dist;

    // Contact point in world space
    Vec3 closestWorld = closest;
    vec3_mul_mat3(&closestWorld, &boxRot);
    vec3_add(&closestWorld, &boxWorld);
    out->position = closestWorld;

    return true;
}

// Separating Axis Test helper
static float project_box_on_axis(const Vec3* half, const Mat3* rot, const Vec3* axis) {
    // Project each box axis onto the test axis and sum absolute values
    Vec3 ax = mat3_get_col(rot, 0);
    Vec3 ay = mat3_get_col(rot, 1);
    Vec3 az = mat3_get_col(rot, 2);

    return half->x * absf(vec3_dot(&ax, axis)) +
           half->y * absf(vec3_dot(&ay, axis)) +
           half->z * absf(vec3_dot(&az, axis));
}

bool collision_box_box(const Shape* a, const Shape* b, ContactPoint* outPoints, int* outNumPoints) {
    // Get world transforms
    Vec3 posA = a->localPosition;
    vec3_mul_transform(&posA, &a->body->transform);

    Vec3 posB = b->localPosition;
    vec3_mul_transform(&posB, &b->body->transform);

    // Get world rotations
    Mat3 rotA;
    mat3_copy_from(&rotA, &a->body->transform.rotation);
    mat3_mul(&rotA, &a->localRotation);

    Mat3 rotB;
    mat3_copy_from(&rotB, &b->body->transform.rotation);
    mat3_mul(&rotB, &b->localRotation);

    Vec3 halfA = a->geom.box.halfExtents;
    Vec3 halfB = b->geom.box.halfExtents;

    // Vector from A to B
    Vec3 d = posB;
    vec3_sub(&d, &posA);

    // Get axes
    Vec3 axA[3], axB[3];
    mat3_get_col_to(&rotA, 0, &axA[0]);
    mat3_get_col_to(&rotA, 1, &axA[1]);
    mat3_get_col_to(&rotA, 2, &axA[2]);
    mat3_get_col_to(&rotB, 0, &axB[0]);
    mat3_get_col_to(&rotB, 1, &axB[1]);
    mat3_get_col_to(&rotB, 2, &axB[2]);

    float minPen = 1e30f;
    Vec3 minAxis = vec3_new(1, 0, 0);
    int minAxisType = 0;  // 0-2: face A, 3-5: face B, 6-14: edge-edge
    (void)minAxisType;  // Suppress unused warning - used for contact type identification

    // Test 15 separating axes
    // 3 face normals of A
    for (int i = 0; i < 3; i++) {
        Vec3* axis = &axA[i];
        float projA = (i == 0 ? halfA.x : (i == 1 ? halfA.y : halfA.z));
        float projB = project_box_on_axis(&halfB, &rotB, axis);
        float dist = absf(vec3_dot(&d, axis));
        float pen = projA + projB - dist;

        if (pen < 0) return false;  // Separating axis found
        if (pen < minPen) {
            minPen = pen;
            minAxis = *axis;
            if (vec3_dot(&d, axis) < 0) vec3_negate(&minAxis);
            minAxisType = i;
        }
    }

    // 3 face normals of B
    for (int i = 0; i < 3; i++) {
        Vec3* axis = &axB[i];
        float projA = project_box_on_axis(&halfA, &rotA, axis);
        float projB = (i == 0 ? halfB.x : (i == 1 ? halfB.y : halfB.z));
        float dist = absf(vec3_dot(&d, axis));
        float pen = projA + projB - dist;

        if (pen < 0) return false;
        if (pen < minPen) {
            minPen = pen;
            minAxis = *axis;
            if (vec3_dot(&d, axis) < 0) vec3_negate(&minAxis);
            minAxisType = 3 + i;
        }
    }

    // 9 edge-edge axes (cross products)
    for (int i = 0; i < 3; i++) {
        for (int j = 0; j < 3; j++) {
            Vec3 axis = vec3_cross(&axA[i], &axB[j]);
            float len = vec3_length(&axis);
            if (len < COLLISION_EPSILON) continue;  // Parallel edges

            vec3_scale(&axis, 1.0f / len);

            float projA = project_box_on_axis(&halfA, &rotA, &axis);
            float projB = project_box_on_axis(&halfB, &rotB, &axis);
            float dist = absf(vec3_dot(&d, &axis));
            float pen = projA + projB - dist;

            if (pen < 0) return false;
            if (pen < minPen) {
                minPen = pen;
                minAxis = axis;
                if (vec3_dot(&d, &axis) < 0) vec3_negate(&minAxis);
                minAxisType = 6 + i * 3 + j;
            }
        }
    }

    // Generate contact point(s)
    // For simplicity, generate single contact at center of overlap
    // A full implementation would clip polygons for face-face contacts

    *outNumPoints = 1;
    outPoints[0].normal = minAxis;
    outPoints[0].penetration = minPen;

    // Contact point approximation: midpoint between box centers, projected to surface
    Vec3 midpoint = posA;
    vec3_add(&midpoint, &posB);
    vec3_scale(&midpoint, 0.5f);

    // Project to contact plane
    Vec3 toMid = midpoint;
    vec3_sub(&toMid, &posA);
    float offset = vec3_dot(&toMid, &minAxis);

    outPoints[0].position = posA;
    vec3_add_scaled(&outPoints[0].position, &minAxis, offset);

    return true;
}

bool collision_test_shapes(Shape* a, Shape* b, ContactPoint* outPoints, int* outNumPoints) {
    *outNumPoints = 0;

    if (a->type == SHAPE_SPHERE && b->type == SHAPE_SPHERE) {
        if (collision_sphere_sphere(a, b, &outPoints[0])) {
            *outNumPoints = 1;
            return true;
        }
    } else if (a->type == SHAPE_SPHERE && b->type == SHAPE_BOX) {
        if (collision_sphere_box(a, b, &outPoints[0])) {
            *outNumPoints = 1;
            return true;
        }
    } else if (a->type == SHAPE_BOX && b->type == SHAPE_SPHERE) {
        if (collision_sphere_box(b, a, &outPoints[0])) {
            // Flip normal
            vec3_negate(&outPoints[0].normal);
            *outNumPoints = 1;
            return true;
        }
    } else if (a->type == SHAPE_BOX && b->type == SHAPE_BOX) {
        return collision_box_box(a, b, outPoints, outNumPoints);
    }

    return false;
}

// =============================================================================
// Contact Constraint Solver
// =============================================================================

static void solve_contact_velocity(Contact* c, float dt) {
    if (!c->isTouching || c->numPoints == 0) return;

    RigidBody* bodyA = c->body1;
    RigidBody* bodyB = c->body2;

    // Skip if both are static/kinematic
    if (bodyA->type != RIGIDBODY_DYNAMIC && bodyB->type != RIGIDBODY_DYNAMIC) return;

    for (int i = 0; i < c->numPoints; i++) {
        ContactPoint* cp = &c->points[i];

        // Vectors from centers to contact point
        Vec3 rA = cp->position;
        vec3_sub(&rA, &bodyA->transform.position);
        Vec3 rB = cp->position;
        vec3_sub(&rB, &bodyB->transform.position);

        // Relative velocity at contact
        Vec3 velA = bodyA->linearVel;
        Vec3 angCrossA = vec3_cross(&bodyA->angularVel, &rA);
        vec3_add(&velA, &angCrossA);

        Vec3 velB = bodyB->linearVel;
        Vec3 angCrossB = vec3_cross(&bodyB->angularVel, &rB);
        vec3_add(&velB, &angCrossB);

        Vec3 relVel = velA;
        vec3_sub(&relVel, &velB);

        // Normal velocity
        float normalVel = vec3_dot(&relVel, &cp->normal);

        // Only apply impulse if bodies are approaching
        if (normalVel > 0) continue;

        // Compute effective mass
        Vec3 rnA = vec3_cross(&rA, &cp->normal);
        Vec3 rnB = vec3_cross(&rB, &cp->normal);

        vec3_mul_mat3(&rnA, &bodyA->invWorldInertia);
        vec3_mul_mat3(&rnB, &bodyB->invWorldInertia);

        Vec3 rnAxN = vec3_cross(&rnA, &rA);
        Vec3 rnBxN = vec3_cross(&rnB, &rB);

        float kNormal = bodyA->invMass + bodyB->invMass +
                        vec3_dot(&rnAxN, &cp->normal) +
                        vec3_dot(&rnBxN, &cp->normal);

        if (kNormal < COLLISION_EPSILON) continue;

        // Restitution (bounciness) - use average of both bodies
        // For simplicity, use 0.2 (slight bounce)
        float restitution = 0.2f;

        // Normal impulse magnitude
        float jN = -(1.0f + restitution) * normalVel / kNormal;
        if (jN < 0) jN = 0;  // No pulling

        // Apply normal impulse
        Vec3 impulse = cp->normal;
        vec3_scale(&impulse, jN);

        if (bodyA->type == RIGIDBODY_DYNAMIC) {
            vec3_add_scaled(&bodyA->linearVel, &impulse, bodyA->invMass);
            Vec3 angImpA = vec3_cross(&rA, &impulse);
            vec3_mul_mat3(&angImpA, &bodyA->invWorldInertia);
            vec3_add(&bodyA->angularVel, &angImpA);
        }

        if (bodyB->type == RIGIDBODY_DYNAMIC) {
            vec3_add_scaled(&bodyB->linearVel, &impulse, -bodyB->invMass);
            Vec3 angImpB = vec3_cross(&rB, &impulse);
            vec3_mul_mat3(&angImpB, &bodyB->invWorldInertia);
            vec3_sub(&bodyB->angularVel, &angImpB);
        }

        // Friction (simplified)
        // Recompute relative velocity after normal impulse
        velA = bodyA->linearVel;
        angCrossA = vec3_cross(&bodyA->angularVel, &rA);
        vec3_add(&velA, &angCrossA);

        velB = bodyB->linearVel;
        angCrossB = vec3_cross(&bodyB->angularVel, &rB);
        vec3_add(&velB, &angCrossB);

        relVel = velA;
        vec3_sub(&relVel, &velB);

        // Tangent velocity
        Vec3 tangentVel = relVel;
        vec3_add_scaled(&tangentVel, &cp->normal, -vec3_dot(&relVel, &cp->normal));

        float tangentSpeed = vec3_length(&tangentVel);
        if (tangentSpeed > COLLISION_EPSILON) {
            Vec3 tangent = tangentVel;
            vec3_scale(&tangent, 1.0f / tangentSpeed);

            // Friction coefficient
            float friction = 0.5f;
            float maxFriction = friction * jN;

            // Friction impulse
            float jT = -tangentSpeed / kNormal;  // Simplified
            if (jT > maxFriction) jT = maxFriction;
            if (jT < -maxFriction) jT = -maxFriction;

            Vec3 frictionImpulse = tangent;
            vec3_scale(&frictionImpulse, jT);

            if (bodyA->type == RIGIDBODY_DYNAMIC) {
                vec3_add_scaled(&bodyA->linearVel, &frictionImpulse, bodyA->invMass);
                Vec3 angFricA = vec3_cross(&rA, &frictionImpulse);
                vec3_mul_mat3(&angFricA, &bodyA->invWorldInertia);
                vec3_add(&bodyA->angularVel, &angFricA);
            }

            if (bodyB->type == RIGIDBODY_DYNAMIC) {
                vec3_add_scaled(&bodyB->linearVel, &frictionImpulse, -bodyB->invMass);
                Vec3 angFricB = vec3_cross(&rB, &frictionImpulse);
                vec3_mul_mat3(&angFricB, &bodyB->invWorldInertia);
                vec3_sub(&bodyB->angularVel, &angFricB);
            }
        }
    }
}

static void solve_contact_position(Contact* c) {
    if (!c->isTouching || c->numPoints == 0) return;

    RigidBody* bodyA = c->body1;
    RigidBody* bodyB = c->body2;

    if (bodyA->type != RIGIDBODY_DYNAMIC && bodyB->type != RIGIDBODY_DYNAMIC) return;

    for (int i = 0; i < c->numPoints; i++) {
        ContactPoint* cp = &c->points[i];

        if (cp->penetration < 0.01f) continue;  // Allow small overlap

        // Position correction (Baumgarte stabilization)
        float correction = maxf(cp->penetration - 0.01f, 0.0f) * 0.2f;

        float totalInvMass = bodyA->invMass + bodyB->invMass;
        if (totalInvMass < COLLISION_EPSILON) continue;

        Vec3 corr = cp->normal;
        vec3_scale(&corr, correction / totalInvMass);

        if (bodyA->type == RIGIDBODY_DYNAMIC) {
            vec3_add_scaled(&bodyA->transform.position, &corr, bodyA->invMass);
        }
        if (bodyB->type == RIGIDBODY_DYNAMIC) {
            vec3_add_scaled(&bodyB->transform.position, &corr, -bodyB->invMass);
        }
    }
}

// =============================================================================
// Simulation Step
// =============================================================================

void world_step(World* world, float dt) {
    if (dt <= 0.0f) return;

    // 1. Integrate velocities (apply forces and gravity)
    for (RigidBody* body = world->bodyList; body; body = body->next) {
        rigidbody_integrate_velocity(body, dt, &world->gravity);
    }

    // 2. Update shape AABBs
    for (RigidBody* body = world->bodyList; body; body = body->next) {
        rigidbody_update_shapes(body);
    }

    // 3. Broad phase - find potential collisions
    //    Mark previous contacts
    for (Contact* c = world->contactList; c; c = c->next) {
        c->wasTouching = c->isTouching;
        c->isTouching = false;
    }

    // 4. Narrow phase - test collisions between all shape pairs
    //    O(n²) for simplicity - sufficient for N64 with <50 bodies
    for (RigidBody* bodyA = world->bodyList; bodyA; bodyA = bodyA->next) {
        for (RigidBody* bodyB = bodyA->next; bodyB; bodyB = bodyB->next) {
            // Skip if both are static
            if (bodyA->type != RIGIDBODY_DYNAMIC && bodyB->type != RIGIDBODY_DYNAMIC) {
                continue;
            }

            // Skip sleeping pairs
            if (bodyA->sleeping && bodyB->sleeping) {
                continue;
            }

            // Test all shape pairs
            for (Shape* shapeA = bodyA->shapeList; shapeA; shapeA = shapeA->next) {
                for (Shape* shapeB = bodyB->shapeList; shapeB; shapeB = shapeB->next) {
                    // Collision mask check
                    if (!collision_should_collide(shapeA, shapeB)) continue;

                    // AABB test
                    if (!collision_test_aabb(shapeA, shapeB)) continue;

                    // Narrow phase
                    ContactPoint points[MAX_CONTACTS_PER_PAIR];
                    int numPoints = 0;

                    if (collision_test_shapes(shapeA, shapeB, points, &numPoints)) {
                        // Find or create contact
                        Contact* contact = NULL;
                        for (Contact* c = world->contactList; c; c = c->next) {
                            if ((c->shape1 == shapeA && c->shape2 == shapeB) ||
                                (c->shape1 == shapeB && c->shape2 == shapeA)) {
                                contact = c;
                                break;
                            }
                        }

                        if (!contact) {
                            contact = contact_alloc(world);
                            if (!contact) continue;

                            contact->body1 = bodyA;
                            contact->body2 = bodyB;
                            contact->shape1 = shapeA;
                            contact->shape2 = shapeB;
                            contact->wasTouching = false;

                            // Add to world list
                            contact->prev = NULL;
                            contact->next = world->contactList;
                            if (world->contactList) world->contactList->prev = contact;
                            world->contactList = contact;
                            world->numContacts++;
                        }

                        // Update contact
                        contact->isTouching = true;
                        contact->numPoints = numPoints;
                        for (int i = 0; i < numPoints; i++) {
                            contact->points[i] = points[i];
                        }

                        // Wake up bodies
                        rigidbody_wake_up(bodyA);
                        rigidbody_wake_up(bodyB);

                        // Begin callback
                        if (!contact->wasTouching && world->onContactBegin) {
                            world->onContactBegin(contact, world->callbackUserData);
                        }

                        // Pre-solve callback
                        if (world->onContactPreSolve) {
                            world->onContactPreSolve(contact, world->callbackUserData);
                        }
                    }
                }
            }
        }
    }

    // 5. Solve velocity constraints
    for (int iter = 0; iter < world->velocityIterations; iter++) {
        for (Contact* c = world->contactList; c; c = c->next) {
            solve_contact_velocity(c, dt);
        }
    }

    // 6. Integrate positions
    for (RigidBody* body = world->bodyList; body; body = body->next) {
        rigidbody_integrate_position(body, dt);
    }

    // 7. Solve position constraints
    for (int iter = 0; iter < world->positionIterations; iter++) {
        for (Contact* c = world->contactList; c; c = c->next) {
            solve_contact_position(c);
        }
    }

    // 8. Post-solve callbacks and clean up ended contacts
    Contact* c = world->contactList;
    while (c) {
        Contact* next = c->next;

        if (c->isTouching) {
            // Post-solve callback
            if (world->onContactPostSolve) {
                world->onContactPostSolve(c, world->callbackUserData);
            }
        } else if (c->wasTouching) {
            // End callback
            if (world->onContactEnd) {
                world->onContactEnd(c, world->callbackUserData);
            }

            // Remove contact
            if (c->prev) c->prev->next = c->next;
            else world->contactList = c->next;
            if (c->next) c->next->prev = c->prev;
            world->numContacts--;

            contact_free(world, c);
        }

        c = next;
    }

    // 9. Update shape AABBs again after position solve
    for (RigidBody* body = world->bodyList; body; body = body->next) {
        rigidbody_update_shapes(body);
    }
}

// =============================================================================
// Settings
// =============================================================================

void world_set_velocity_iterations(World* world, int iterations) {
    world->velocityIterations = iterations;
}

int world_get_velocity_iterations(const World* world) {
    return world->velocityIterations;
}

void world_set_position_iterations(World* world, int iterations) {
    world->positionIterations = iterations;
}

int world_get_position_iterations(const World* world) {
    return world->positionIterations;
}

void world_set_contact_callbacks(World* world,
                                 ContactBeginCallback onBegin,
                                 ContactEndCallback onEnd,
                                 ContactPreSolveCallback onPreSolve,
                                 ContactPostSolveCallback onPostSolve,
                                 void* userData) {
    world->onContactBegin = onBegin;
    world->onContactEnd = onEnd;
    world->onContactPreSolve = onPreSolve;
    world->onContactPostSolve = onPostSolve;
    world->callbackUserData = userData;
}

Contact* world_get_contact_list(const World* world) {
    return world->contactList;
}

int world_get_num_contacts(const World* world) {
    return world->numContacts;
}

void world_set_allow_sleep(World* world, bool allow) {
    world->allowSleep = allow;
}

bool world_get_allow_sleep(const World* world) {
    return world->allowSleep;
}

void world_clear(World* world) {
    // Remove all bodies
    while (world->bodyList) {
        world_remove_body(world, world->bodyList);
    }
}

// =============================================================================
// Raycasting
// =============================================================================

bool collision_ray_sphere(const Vec3* from, const Vec3* dir, float maxDist,
                          const Shape* sphere, float* outDist, Vec3* outNormal) {
    // Sphere center in world space
    Vec3 center = sphere->localPosition;
    vec3_mul_transform(&center, &sphere->body->transform);

    float radius = sphere->geom.sphere.radius;

    // Vector from ray origin to sphere center
    Vec3 oc = *from;
    vec3_sub(&oc, &center);

    // Quadratic equation: t² + 2bt + c = 0
    float b = vec3_dot(&oc, dir);
    float c = vec3_dot(&oc, &oc) - radius * radius;
    float discriminant = b * b - c;

    if (discriminant < 0) return false;

    float sqrtD = sqrtf(discriminant);
    float t = -b - sqrtD;

    if (t < 0) t = -b + sqrtD;
    if (t < 0 || t > maxDist) return false;

    *outDist = t;

    // Hit point
    Vec3 hitPoint = *from;
    vec3_add_scaled(&hitPoint, dir, t);

    // Normal at hit point
    *outNormal = hitPoint;
    vec3_sub(outNormal, &center);
    vec3_normalize(outNormal);

    return true;
}

bool collision_ray_box(const Vec3* from, const Vec3* dir, float maxDist,
                       const Shape* box, float* outDist, Vec3* outNormal) {
    // Transform ray to box local space
    Vec3 boxWorld = box->localPosition;
    vec3_mul_transform(&boxWorld, &box->body->transform);

    Mat3 boxRot;
    mat3_copy_from(&boxRot, &box->body->transform.rotation);
    mat3_mul(&boxRot, &box->localRotation);

    Mat3 invBoxRot = boxRot;
    mat3_transpose(&invBoxRot);

    // Ray origin in box local space
    Vec3 localFrom = *from;
    vec3_sub(&localFrom, &boxWorld);
    vec3_mul_mat3(&localFrom, &invBoxRot);

    // Ray direction in box local space
    Vec3 localDir = *dir;
    vec3_mul_mat3(&localDir, &invBoxRot);

    Vec3 half = box->geom.box.halfExtents;

    // Slab test
    float tMin = 0.0f;
    float tMax = maxDist;
    int hitAxis = -1;
    float hitSign = 1.0f;

    float* halfArr = &half.x;
    float* fromArr = &localFrom.x;
    float* dirArr = &localDir.x;

    for (int i = 0; i < 3; i++) {
        if (absf(dirArr[i]) < COLLISION_EPSILON) {
            // Ray parallel to slab
            if (fromArr[i] < -halfArr[i] || fromArr[i] > halfArr[i]) {
                return false;
            }
        } else {
            float invD = 1.0f / dirArr[i];
            float t1 = (-halfArr[i] - fromArr[i]) * invD;
            float t2 = (halfArr[i] - fromArr[i]) * invD;

            float tNear = minf(t1, t2);
            float tFar = maxf(t1, t2);

            if (tNear > tMin) {
                tMin = tNear;
                hitAxis = i;
                hitSign = (dirArr[i] > 0) ? -1.0f : 1.0f;
            }
            tMax = minf(tMax, tFar);

            if (tMin > tMax) return false;
        }
    }

    if (tMin < 0) return false;

    *outDist = tMin;

    // Normal in local space
    Vec3 localNormal = vec3_zero();
    if (hitAxis == 0) localNormal.x = hitSign;
    else if (hitAxis == 1) localNormal.y = hitSign;
    else localNormal.z = hitSign;

    // Transform normal to world space
    *outNormal = localNormal;
    vec3_mul_mat3(outNormal, &boxRot);

    return true;
}

void world_raycast(World* world, const Vec3* from, const Vec3* to,
                   RaycastCallback callback, void* userData) {
    Vec3 dir = *to;
    vec3_sub(&dir, from);
    float maxDist = vec3_length(&dir);

    if (maxDist < COLLISION_EPSILON) return;
    vec3_scale(&dir, 1.0f / maxDist);

    for (RigidBody* body = world->bodyList; body; body = body->next) {
        for (Shape* shape = body->shapeList; shape; shape = shape->next) {
            float dist;
            Vec3 normal;
            bool hit = false;

            if (shape->type == SHAPE_SPHERE) {
                hit = collision_ray_sphere(from, &dir, maxDist, shape, &dist, &normal);
            } else if (shape->type == SHAPE_BOX) {
                hit = collision_ray_box(from, &dir, maxDist, shape, &dist, &normal);
            }

            if (hit) {
                RaycastHit hitInfo;
                hitInfo.body = body;
                hitInfo.shape = shape;
                hitInfo.position = *from;
                vec3_add_scaled(&hitInfo.position, &dir, dist);
                hitInfo.normal = normal;
                hitInfo.fraction = dist / maxDist;

                if (!callback(&hitInfo, userData)) {
                    return;  // Callback requested stop
                }
            }
        }
    }
}

bool world_raycast_closest(World* world, const Vec3* from, const Vec3* to,
                           RaycastHit* outHit) {
    Vec3 dir = *to;
    vec3_sub(&dir, from);
    float maxDist = vec3_length(&dir);

    if (maxDist < COLLISION_EPSILON) return false;
    vec3_scale(&dir, 1.0f / maxDist);

    bool foundHit = false;
    float closestDist = maxDist;

    for (RigidBody* body = world->bodyList; body; body = body->next) {
        for (Shape* shape = body->shapeList; shape; shape = shape->next) {
            float dist;
            Vec3 normal;
            bool hit = false;

            if (shape->type == SHAPE_SPHERE) {
                hit = collision_ray_sphere(from, &dir, closestDist, shape, &dist, &normal);
            } else if (shape->type == SHAPE_BOX) {
                hit = collision_ray_box(from, &dir, closestDist, shape, &dist, &normal);
            }

            if (hit && dist < closestDist) {
                closestDist = dist;
                foundHit = true;

                outHit->body = body;
                outHit->shape = shape;
                outHit->position = *from;
                vec3_add_scaled(&outHit->position, &dir, dist);
                outHit->normal = normal;
                outHit->fraction = dist / maxDist;
            }
        }
    }

    return foundHit;
}
