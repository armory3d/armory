/**
 * OimoPhysics N64 Port
 *
 * A port of OimoPhysics (https://github.com/saharan/OimoPhysics)
 * for the Nintendo 64 using libdragon.
 *
 * This is a minimal implementation supporting only Box and Sphere shapes.
 *
 * Usage:
 *   #include "oimo/oimo.h"
 */

#ifndef OIMO_OIMO_H
#define OIMO_OIMO_H

// ============================================================================
// Common Module - Math Foundation
// ============================================================================
#include "common/setting.h"
#include "common/math_util.h"
#include "common/vec3.h"
#include "common/mat3.h"
#include "common/quat.h"
#include "common/transform.h"

// ============================================================================
// Collision Module - Geometry
// ============================================================================
#include "collision/geometry/geometry_type.h"
#include "collision/geometry/aabb.h"
#include "collision/geometry/geometry.h"
#include "collision/geometry/sphere_geometry.h"
#include "collision/geometry/box_geometry.h"

// ============================================================================
// Collision Module - Narrowphase Detection
// ============================================================================
#include "collision/narrowphase/detector_result.h"
#include "collision/narrowphase/detector.h"
#include "collision/narrowphase/sphere_sphere_detector.h"
#include "collision/narrowphase/sphere_box_detector.h"
#include "collision/narrowphase/box_box_detector.h"
#include "collision/narrowphase/collision_matrix.h"

// ============================================================================
// Collision Module - Broadphase (to be implemented)
// ============================================================================
// #include "collision/broadphase/broadphase.h"

// ============================================================================
// Dynamics Module (to be implemented)
// ============================================================================
// #include "dynamics/rigidbody/rigidbody.h"
// #include "dynamics/constraint/contact/contact_constraint.h"
// #include "dynamics/world.h"

#endif // OIMO_OIMO_H
