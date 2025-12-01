// island.h
// 1:1 port from OimoPhysics Island.hx
#ifndef OIMO_DYNAMICS_ISLAND_H
#define OIMO_DYNAMICS_ISLAND_H

#include "../common/vec3.h"
#include "../common/mat3.h"
#include "../common/setting.h"
#include "time_step.h"
#include "rigidbody/rigid_body.h"
#include "rigidbody/rigid_body_type.h"
#include "constraint/position_correction_algorithm.h"
#include "constraint/solver/pgs/pgs_contact_constraint_solver.h"

// Island size limits for N64
#define OIMO_MAX_ISLAND_BODIES 32
#define OIMO_MAX_ISLAND_SOLVERS 64

typedef struct OimoIsland {
    OimoVec3 gravity;

    int numRigidBodies;
    OimoRigidBody* rigidBodies[OIMO_MAX_ISLAND_BODIES];

    // All constraint solvers
    int numSolvers;
    OimoPgsContactConstraintSolver* solvers[OIMO_MAX_ISLAND_SOLVERS];

    // Split impulse solvers
    int numSolversSi;
    OimoPgsContactConstraintSolver* solversSi[OIMO_MAX_ISLAND_SOLVERS];

    // NGS solvers
    int numSolversNgs;
    OimoPgsContactConstraintSolver* solversNgs[OIMO_MAX_ISLAND_SOLVERS];
} OimoIsland;

static inline void oimo_island_init(OimoIsland* island) {
    island->gravity = oimo_vec3(0.0f, -9.80665f, 0.0f);
    island->numRigidBodies = 0;
    island->numSolvers = 0;
    island->numSolversSi = 0;
    island->numSolversNgs = 0;
}

// Fast inverse exponential approximation - 1:1 from Island.fastInvExp
static inline OimoScalar oimo_island_fast_inv_exp(OimoScalar x) {
    OimoScalar x2 = x * x;
    return 1.0f / (1.0f + x + x2 * (0.5f + x * (1.0f/6.0f) + x2 * (1.0f/24.0f)));
}

static inline void oimo_island_clear(OimoIsland* island) {
    for (int i = 0; i < island->numRigidBodies; i++) {
        island->rigidBodies[i] = NULL;
    }
    for (int i = 0; i < island->numSolvers; i++) {
        island->solvers[i] = NULL;
    }
    for (int i = 0; i < island->numSolversSi; i++) {
        island->solversSi[i] = NULL;
    }
    for (int i = 0; i < island->numSolversNgs; i++) {
        island->solversNgs[i] = NULL;
    }
    island->numRigidBodies = 0;
    island->numSolvers = 0;
    island->numSolversSi = 0;
    island->numSolversNgs = 0;
}

static inline void oimo_island_set_gravity(OimoIsland* island, OimoVec3 gravity) {
    island->gravity = gravity;
}

static inline void oimo_island_add_rigid_body(OimoIsland* island, OimoRigidBody* rb) {
    if (island->numRigidBodies < OIMO_MAX_ISLAND_BODIES) {
        rb->_addedToIsland = 1;
        island->rigidBodies[island->numRigidBodies++] = rb;
    }
}

static inline void oimo_island_add_solver(OimoIsland* island, OimoPgsContactConstraintSolver* solver, int positionCorrection) {
    if (island->numSolvers < OIMO_MAX_ISLAND_SOLVERS) {
        solver->_addedToIsland = true;
        island->solvers[island->numSolvers++] = solver;

        if (positionCorrection == OIMO_POSITION_CORRECTION_SPLIT_IMPULSE) {
            if (island->numSolversSi < OIMO_MAX_ISLAND_SOLVERS) {
                island->solversSi[island->numSolversSi++] = solver;
            }
        }
        if (positionCorrection == OIMO_POSITION_CORRECTION_NGS) {
            if (island->numSolversNgs < OIMO_MAX_ISLAND_SOLVERS) {
                island->solversNgs[island->numSolversNgs++] = solver;
            }
        }
    }
}

// Step single rigid body - 1:1 from Island._stepSingleRigidBody
static inline void oimo_island_step_single_rigid_body(OimoIsland* island, OimoTimeStep* timeStep, OimoRigidBody* rb) {
    OimoScalar dt = timeStep->dt;

    // Store previous transform
    rb->_ptransform = rb->_transform;

    // Clear contact impulses
    rb->_linearContactImpulse = oimo_vec3_zero();
    rb->_angularContactImpulse = oimo_vec3_zero();

    // Update sleep time
    if (oimo_rigid_body_is_sleepy(rb)) {
        rb->_sleepTime += dt;
        if (rb->_sleepTime >= rb->_sleepingTimeThreshold) {
            oimo_rigid_body_sleep(rb);
        }
    } else {
        rb->_sleepTime = 0.0f;
    }

    if (!rb->_sleeping) {
        if (rb->_type == OIMO_RIGID_BODY_DYNAMIC) {
            // Damping
            OimoScalar linScale = oimo_island_fast_inv_exp(dt * rb->_linearDamping);
            OimoScalar angScale = oimo_island_fast_inv_exp(dt * rb->_angularDamping);

            // Compute accelerations
            OimoVec3 linAcc = oimo_vec3_scale(island->gravity, rb->_gravityScale);
            OimoVec3 forceAcc = oimo_vec3_scale(rb->_force, rb->_invMass);
            linAcc = oimo_vec3_add(linAcc, forceAcc);
            OimoVec3 angAcc = oimo_mat3_mul_vec3(&rb->_invInertia, rb->_torque);

            // Update velocity
            OimoVec3 linAccDt = oimo_vec3_scale(linAcc, dt);
            rb->_vel = oimo_vec3_add(rb->_vel, linAccDt);
            rb->_vel = oimo_vec3_scale(rb->_vel, linScale);
            OimoVec3 angAccDt = oimo_vec3_scale(angAcc, dt);
            rb->_angVel = oimo_vec3_add(rb->_angVel, angAccDt);
            rb->_angVel = oimo_vec3_scale(rb->_angVel, angScale);
        }
        oimo_rigid_body_integrate(rb, dt);
        oimo_rigid_body_sync_shapes(rb);
    }
}

// Step island with multiple bodies and constraints - 1:1 from Island._step
static inline void oimo_island_step(
    OimoIsland* island,
    OimoTimeStep* timeStep,
    int numVelocityIterations,
    int numPositionIterations
) {
    OimoScalar dt = timeStep->dt;
    bool sleepIsland = true;

    // Sleep check and apply gravity
    for (int i = 0; i < island->numRigidBodies; i++) {
        OimoRigidBody* rb = island->rigidBodies[i];

        // Store previous transform
        rb->_ptransform = rb->_transform;

        // Clear contact impulses
        rb->_linearContactImpulse = oimo_vec3_zero();
        rb->_angularContactImpulse = oimo_vec3_zero();

        // Don't let the rigid body sleep yet
        rb->_sleeping = 0;

        // Update sleep time
        if (oimo_rigid_body_is_sleepy(rb)) {
            rb->_sleepTime += dt;
        } else {
            rb->_sleepTime = 0.0f;
        }

        // Check if awake
        if (rb->_sleepTime < rb->_sleepingTimeThreshold) {
            sleepIsland = false;
        }

        // Apply forces
        if (rb->_type == OIMO_RIGID_BODY_DYNAMIC) {
            OimoScalar linScale = oimo_island_fast_inv_exp(dt * rb->_linearDamping);
            OimoScalar angScale = oimo_island_fast_inv_exp(dt * rb->_angularDamping);

            OimoVec3 linAcc = oimo_vec3_scale(island->gravity, rb->_gravityScale);
            OimoVec3 forceAcc = oimo_vec3_scale(rb->_force, rb->_invMass);
            linAcc = oimo_vec3_add(linAcc, forceAcc);
            OimoVec3 angAcc = oimo_mat3_mul_vec3(&rb->_invInertia, rb->_torque);

            OimoVec3 linAccDt = oimo_vec3_scale(linAcc, dt);
            rb->_vel = oimo_vec3_add(rb->_vel, linAccDt);
            rb->_vel = oimo_vec3_scale(rb->_vel, linScale);
            OimoVec3 angAccDt = oimo_vec3_scale(angAcc, dt);
            rb->_angVel = oimo_vec3_add(rb->_angVel, angAccDt);
            rb->_angVel = oimo_vec3_scale(rb->_angVel, angScale);
        }
    }

    // Sleep the whole island if all bodies are sleepy
    if (sleepIsland) {
        for (int i = 0; i < island->numRigidBodies; i++) {
            oimo_rigid_body_sleep(island->rigidBodies[i]);
        }
        return;
    }

    // Solve velocity constraints
    for (int i = 0; i < island->numSolvers; i++) {
        oimo_pgs_contact_solver_pre_solve_velocity(island->solvers[i], timeStep);
    }
    for (int i = 0; i < island->numSolvers; i++) {
        oimo_pgs_contact_solver_warm_start(island->solvers[i], timeStep);
    }
    for (int t = 0; t < numVelocityIterations; t++) {
        for (int i = 0; i < island->numSolvers; i++) {
            oimo_pgs_contact_solver_solve_velocity(island->solvers[i]);
        }
    }

    // Integrate positions
    for (int i = 0; i < island->numRigidBodies; i++) {
        oimo_rigid_body_integrate(island->rigidBodies[i], dt);
    }

    // Solve split impulse position correction
    for (int i = 0; i < island->numSolversSi; i++) {
        oimo_pgs_contact_solver_pre_solve_position(island->solversSi[i], timeStep);
    }
    for (int t = 0; t < numPositionIterations; t++) {
        for (int i = 0; i < island->numSolversSi; i++) {
            oimo_pgs_contact_solver_solve_position_split_impulse(island->solversSi[i]);
        }
    }

    // Integrate pseudo velocity
    for (int i = 0; i < island->numRigidBodies; i++) {
        oimo_rigid_body_integrate_pseudo_velocity(island->rigidBodies[i]);
    }

    // Solve NGS position correction
    for (int i = 0; i < island->numSolversNgs; i++) {
        oimo_pgs_contact_solver_pre_solve_position(island->solversNgs[i], timeStep);
    }
    for (int t = 0; t < numPositionIterations; t++) {
        for (int i = 0; i < island->numSolversNgs; i++) {
            oimo_pgs_contact_solver_solve_position_ngs(island->solversNgs[i], timeStep);
        }
    }

    // Post solve
    for (int i = 0; i < island->numSolvers; i++) {
        oimo_pgs_contact_solver_post_solve(island->solvers[i]);
    }

    // Synchronize shapes
    for (int i = 0; i < island->numRigidBodies; i++) {
        oimo_rigid_body_sync_shapes(island->rigidBodies[i]);
    }
}

#endif // OIMO_DYNAMICS_ISLAND_H
