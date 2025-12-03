#ifndef OIMO_DYNAMICS_WORLD_H
#define OIMO_DYNAMICS_WORLD_H

#include "../common/vec3.h"
#include "../common/setting.h"
#include "../collision/broadphase/broadphase.h"
#include "../collision/broadphase/bruteforce_broadphase.h"
#include "time_step.h"
#include "rigidbody/rigid_body.h"
#include "rigidbody/rigid_body_type.h"
#include "rigidbody/shape.h"
#include "contact.h"
#include "contact_link.h"
#include "contact_manager.h"
#include "island.h"

// World limits for N64
#define OIMO_MAX_RIGID_BODIES 32
#define OIMO_MAX_SHAPES 64

typedef struct OimoWorld {
    OimoRigidBody* _rigidBodyList;
    OimoRigidBody* _rigidBodyListLast;

    OimoBroadPhase _broadPhaseStorage;
    OimoBroadPhase* _broadPhase;
    OimoContactManager _contactManager;

    int _numRigidBodies;
    int _numShapes;
    int _numIslands;

    int _numVelocityIterations;
    int _numPositionIterations;

    OimoVec3 _gravity;

    OimoTimeStep _timeStep;
    OimoIsland _island;

    // Stack for island building
    OimoRigidBody* _rigidBodyStack[OIMO_MAX_RIGID_BODIES];

    int _shapeIdCount;
} OimoWorld;

// Forward declarations for internal functions
static inline void oimo_world_update_contacts(OimoWorld* world);
static inline void oimo_world_solve_islands(OimoWorld* world);
static inline void oimo_world_build_island(OimoWorld* world, OimoRigidBody* base);

// Initialize world - 1:1 from World constructor
static inline void oimo_world_init(OimoWorld* world, OimoVec3* gravity) {
    // Initialize broadphase (brute-force O(n²) - reliable for N64's small object counts)
    oimo_bruteforce_broadphase_init(&world->_broadPhaseStorage);
    world->_broadPhase = &world->_broadPhaseStorage;

    // Initialize contact manager
    oimo_contact_manager_init(&world->_contactManager, world->_broadPhase);

    // Set gravity
    if (gravity != NULL) {
        world->_gravity = *gravity;
    } else {
        world->_gravity = oimo_vec3(0.0f, -9.80665f, 0.0f);
    }

    world->_rigidBodyList = NULL;
    world->_rigidBodyListLast = NULL;

    world->_numRigidBodies = 0;
    world->_numShapes = 0;
    world->_numIslands = 0;

    world->_numVelocityIterations = 10;
    world->_numPositionIterations = 5;

    world->_timeStep = oimo_time_step_create();
    oimo_island_init(&world->_island);

    world->_shapeIdCount = 0;
}

// Add shape to broadphase
static inline void oimo_world_add_shape(OimoWorld* world, OimoShape* shape) {
    shape->_proxy = oimo_broadphase_create_proxy(world->_broadPhase, shape, &shape->_aabb);
    shape->_id = world->_shapeIdCount++;
    world->_numShapes++;
}

// Remove shape from broadphase
static inline void oimo_world_remove_shape(OimoWorld* world, OimoShape* shape) {
    oimo_broadphase_destroy_proxy(world->_broadPhase, shape->_proxy);
    shape->_proxy = NULL;
    shape->_id = -1;

    // Destroy linked contacts
    OimoContactLink* cl = shape->_rigidBody->_contactLinkList;
    while (cl != NULL) {
        OimoContactLink* next = cl->_next;
        OimoContact* c = cl->_contact;
        if (c->_s1 == shape || c->_s2 == shape) {
            oimo_rigid_body_wake_up(cl->_other);
            oimo_contact_manager_destroy_contact(&world->_contactManager, c);
        }
        cl = next;
    }

    world->_numShapes--;
}

// Add rigid body to world - 1:1 from World.addRigidBody
static inline void oimo_world_add_rigid_body(OimoWorld* world, OimoRigidBody* rigidBody) {
    if (rigidBody->_world != NULL) {
        return; // Already in a world
    }

    // Add to list
    rigidBody->_prev = world->_rigidBodyListLast;
    rigidBody->_next = NULL;
    if (world->_rigidBodyListLast != NULL) {
        world->_rigidBodyListLast->_next = rigidBody;
    } else {
        world->_rigidBodyList = rigidBody;
    }
    world->_rigidBodyListLast = rigidBody;
    rigidBody->_world = world;

    // Add shapes to broadphase
    OimoShape* s = rigidBody->_shapeList;
    while (s != NULL) {
        oimo_world_add_shape(world, s);
        s = s->_next;
    }

    world->_numRigidBodies++;
}

// Remove rigid body from world - 1:1 from World.removeRigidBody
static inline void oimo_world_remove_rigid_body(OimoWorld* world, OimoRigidBody* rigidBody) {
    if (rigidBody->_world != world) {
        return; // Not in this world
    }

    // Remove from list
    if (rigidBody->_prev != NULL) {
        rigidBody->_prev->_next = rigidBody->_next;
    } else {
        world->_rigidBodyList = rigidBody->_next;
    }
    if (rigidBody->_next != NULL) {
        rigidBody->_next->_prev = rigidBody->_prev;
    } else {
        world->_rigidBodyListLast = rigidBody->_prev;
    }
    rigidBody->_world = NULL;

    // Remove shapes from broadphase
    OimoShape* s = rigidBody->_shapeList;
    while (s != NULL) {
        oimo_world_remove_shape(world, s);
        s = s->_next;
    }

    world->_numRigidBodies--;
}

// Update contacts - 1:1 from World._updateContacts
static inline void oimo_world_update_contacts(OimoWorld* world) {
    oimo_contact_manager_update_contacts(&world->_contactManager);
    oimo_contact_manager_update_manifolds(&world->_contactManager);
}

// Build island using DFS - 1:1 from World.buildIsland
static inline void oimo_world_build_island(OimoWorld* world, OimoRigidBody* base) {
    int stackCount = 1;
    oimo_island_add_rigid_body(&world->_island, base);
    world->_rigidBodyStack[0] = base;

    while (stackCount > 0) {
        OimoRigidBody* rb = world->_rigidBodyStack[--stackCount];
        world->_rigidBodyStack[stackCount] = NULL;

        // Stop searching at static bodies
        if (rb->_type == OIMO_RIGID_BODY_STATIC) {
            continue;
        }

        // Search contacts
        OimoContactLink* cl = rb->_contactLinkList;
        while (cl != NULL) {
            OimoContact* contact = cl->_contact;
            OimoContactConstraint* cc = &contact->_contactConstraint;
            OimoPgsContactConstraintSolver* solver = &contact->_solver;

            if (oimo_contact_constraint_is_touching(cc) && !solver->_addedToIsland) {
                oimo_island_add_solver(&world->_island, solver, cc->_positionCorrectionAlgorithm);

                OimoRigidBody* other = cl->_other;
                if (!other->_addedToIsland && stackCount < OIMO_MAX_RIGID_BODIES) {
                    oimo_island_add_rigid_body(&world->_island, other);
                    world->_rigidBodyStack[stackCount++] = other;
                }
            }
            cl = cl->_next;
        }
    }
}

// Solve islands - 1:1 from World._solveIslands
static inline void oimo_world_solve_islands(OimoWorld* world) {
    // Wake up all bodies if sleeping disabled
    if (OIMO_DISABLE_SLEEPING) {
        OimoRigidBody* b = world->_rigidBodyList;
        while (b != NULL) {
            b->_sleeping = 0;
            b->_sleepTime = 0.0f;
            b = b->_next;
        }
    }

    // Build and solve islands
    world->_numIslands = 0;
    oimo_island_set_gravity(&world->_island, world->_gravity);

    OimoRigidBody* b = world->_rigidBodyList;
    while (b != NULL) {
        if (!b->_addedToIsland && !b->_sleeping && b->_type != OIMO_RIGID_BODY_STATIC) {
            // Check if alone (no contacts)
            if (b->_numContactLinks == 0) {
                oimo_island_step_single_rigid_body(&world->_island, &world->_timeStep, b);
                world->_numIslands++;
            } else {
                oimo_world_build_island(world, b);
                oimo_island_step(&world->_island, &world->_timeStep,
                                world->_numVelocityIterations, world->_numPositionIterations);
                oimo_island_clear(&world->_island);
                world->_numIslands++;
            }
        }
        b = b->_next;
    }

    oimo_contact_manager_post_solve(&world->_contactManager);

    // Clear island flags
    b = world->_rigidBodyList;
    while (b != NULL) {
        b->_addedToIsland = 0;
        b = b->_next;
    }

    // Clear forces and torques
    b = world->_rigidBodyList;
    while (b != NULL) {
        b->_force = oimo_vec3_zero();
        b->_torque = oimo_vec3_zero();
        b = b->_next;
    }

    // Clear solver island flags
    OimoContact* c = world->_contactManager._contactList;
    while (c != NULL) {
        c->_solver._addedToIsland = false;
        c = c->_next;
    }
}

// Step the simulation - 1:1 from World.step
static inline void oimo_world_step(OimoWorld* world, OimoScalar timeStep) {
    // Guard against zero or negative timestep
    if (timeStep <= OIMO_EPSILON) {
        return;
    }

    if (world->_timeStep.dt > 0.0f) {
        world->_timeStep.dtRatio = timeStep / world->_timeStep.dt;
    }
    world->_timeStep.dt = timeStep;
    world->_timeStep.invDt = 1.0f / timeStep;

    oimo_world_update_contacts(world);
    oimo_world_solve_islands(world);
}

// Getters
static inline OimoRigidBody* oimo_world_get_rigid_body_list(const OimoWorld* world) {
    return world->_rigidBodyList;
}

static inline OimoBroadPhase* oimo_world_get_broadphase(const OimoWorld* world) {
    return world->_broadPhase;
}

static inline OimoContactManager* oimo_world_get_contact_manager(OimoWorld* world) {
    return &world->_contactManager;
}

static inline int oimo_world_get_num_rigid_bodies(const OimoWorld* world) {
    return world->_numRigidBodies;
}

static inline int oimo_world_get_num_shapes(const OimoWorld* world) {
    return world->_numShapes;
}

static inline int oimo_world_get_num_contacts(const OimoWorld* world) {
    return world->_contactManager._numContacts;
}

static inline int oimo_world_get_num_islands(const OimoWorld* world) {
    return world->_numIslands;
}

static inline void oimo_world_set_gravity(OimoWorld* world, OimoVec3 gravity) {
    world->_gravity = gravity;
}

static inline OimoVec3 oimo_world_get_gravity(const OimoWorld* world) {
    return world->_gravity;
}

static inline void oimo_world_set_num_velocity_iterations(OimoWorld* world, int iterations) {
    world->_numVelocityIterations = iterations;
}

static inline void oimo_world_set_num_position_iterations(OimoWorld* world, int iterations) {
    world->_numPositionIterations = iterations;
}

#endif // OIMO_DYNAMICS_WORLD_H
