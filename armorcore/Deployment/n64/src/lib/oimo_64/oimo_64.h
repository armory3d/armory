#ifndef OIMO_64_H
#define OIMO_64_H

/**
 * oimo_64 - Lightweight Physics Engine for N64
 *
 * A minimal physics engine inspired by OimoPhysics, optimized for N64 constraints.
 * Supports sphere and box collision shapes, rigid body dynamics, contact callbacks,
 * and raycasting.
 *
 * Features:
 * - Sphere and Box collision shapes
 * - Dynamic, Static, and Kinematic body types
 * - Gravity and damping
 * - Contact detection with callbacks (onBegin, onEnd, onPreSolve, onPostSolve)
 * - Impulse-based constraint solver
 * - Raycasting
 * - Auto-sleeping for performance
 * - Collision filtering (groups and masks)
 *
 * Basic Usage:
 *
 *   // Create world
 *   World* world = world_create_default();
 *
 *   // Create a dynamic body
 *   RigidBody* ball = rigidbody_create();
 *   Shape* sphere = shape_create_sphere(1.0f);
 *   rigidbody_add_shape(ball, sphere);
 *   Vec3 pos = vec3_new(0, 10, 0);
 *   rigidbody_set_position(ball, &pos);
 *   world_add_body(world, ball);
 *
 *   // Create a static floor
 *   RigidBody* floor = rigidbody_create();
 *   rigidbody_set_type(floor, RIGIDBODY_STATIC);
 *   Shape* box = shape_create_box(10, 0.5f, 10);
 *   rigidbody_add_shape(floor, box);
 *   world_add_body(world, floor);
 *
 *   // Simulation loop
 *   while (running) {
 *       world_step(world, 1.0f / 60.0f);
 *       // Render objects using rigidbody_get_position()
 *   }
 *
 *   // Cleanup
 *   world_destroy(world);
 *   rigidbody_destroy(ball);
 *   rigidbody_destroy(floor);
 */

// Math types (uses libdragon's optimized fm_vec3_t, fm_quat_t, etc.)
#include "common/Vec3.h"
#include "common/Mat3.h"
#include "common/Quat.h"
#include "common/Transform.h"

// Collision shapes
#include "collision/geometry/sphere_geometry.h"
#include "collision/geometry/box_geometry.h"

// Dynamics
#include "dynamics/rigidbody/rigidbody.h"
#include "dynamics/world.h"

#endif
