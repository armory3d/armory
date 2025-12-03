#ifndef OIMO_OIMO_H
#define OIMO_OIMO_H

#include "common/setting.h"
#include "common/math_util.h"
#include "common/vec3.h"
#include "common/mat3.h"
#include "common/quat.h"
#include "common/transform.h"

#include "collision/geometry/geometry_type.h"
#include "collision/geometry/aabb.h"
#include "collision/geometry/geometry.h"
#include "collision/geometry/sphere_geometry.h"
#include "collision/geometry/box_geometry.h"
#include "collision/geometry/capsule_geometry.h"

#include "collision/narrowphase/detector_result.h"
#include "collision/narrowphase/detector.h"
#include "collision/narrowphase/sphere_sphere_detector.h"
#include "collision/narrowphase/sphere_box_detector.h"
#include "collision/narrowphase/box_box_detector.h"
#include "collision/narrowphase/collision_matrix.h"

#include "collision/broadphase/broadphase_type.h"
#include "collision/broadphase/proxy.h"
#include "collision/broadphase/proxy_pair.h"
#include "collision/broadphase/broadphase.h"
#include "collision/broadphase/bruteforce_broadphase.h"

#include "dynamics/rigidbody/rigid_body_type.h"
#include "dynamics/rigidbody/mass_data.h"
#include "dynamics/rigidbody/shape_config.h"
#include "dynamics/rigidbody/rigid_body_config.h"
#include "dynamics/rigidbody/shape.h"
#include "dynamics/rigidbody/rigid_body.h"

#include "dynamics/time_step.h"
#include "dynamics/contact_link.h"
#include "dynamics/constraint/position_correction_algorithm.h"
#include "dynamics/constraint/info/jacobian_row.h"
#include "dynamics/constraint/contact/contact_impulse.h"
#include "dynamics/constraint/contact/manifold_point.h"
#include "dynamics/constraint/contact/manifold.h"
#include "dynamics/constraint/contact/manifold_updater.h"
#include "dynamics/constraint/contact/contact_constraint.h"
#include "dynamics/constraint/info/contact/contact_solver_info_row.h"
#include "dynamics/constraint/info/contact/contact_solver_info.h"
#include "dynamics/constraint/solver/contact_solver_mass_data_row.h"
#include "dynamics/constraint/solver/pgs/pgs_contact_constraint_solver.h"

#include "dynamics/contact.h"
#include "dynamics/contact_manager.h"
#include "dynamics/island.h"
#include "dynamics/world.h"

// Armory3D compatibility layer

// Body type aliases
#define OIMO_BODY_STATIC    OIMO_RIGID_BODY_STATIC
#define OIMO_BODY_DYNAMIC   OIMO_RIGID_BODY_DYNAMIC
#define OIMO_BODY_KINEMATIC OIMO_RIGID_BODY_KINEMATIC

// Config defaults
static inline OimoRigidBodyConfig oimo_rigidbody_config_default(void) {
    return oimo_rigid_body_config();
}

static inline OimoShapeConfig oimo_shape_config_default(void) {
    return oimo_shape_config();
}

// Geometry pool allocation
#define OIMO_MAX_GEOMETRIES 64
static OimoSphereGeometry _oimo_sphere_pool[OIMO_MAX_GEOMETRIES];
static OimoBoxGeometry _oimo_box_pool[OIMO_MAX_GEOMETRIES];
static OimoCapsuleGeometry _oimo_capsule_pool[OIMO_MAX_GEOMETRIES];
static int _oimo_sphere_pool_idx = 0;
static int _oimo_box_pool_idx = 0;
static int _oimo_capsule_pool_idx = 0;

static inline OimoGeometry* oimo_geometry_sphere(OimoScalar radius) {
    if (_oimo_sphere_pool_idx >= OIMO_MAX_GEOMETRIES) {
        debugf("Oimo: sphere geometry pool exhausted (%d max)\n", OIMO_MAX_GEOMETRIES);
        return NULL;
    }
    OimoSphereGeometry* g = &_oimo_sphere_pool[_oimo_sphere_pool_idx++];
    oimo_sphere_geometry_init(g, radius);
    return (OimoGeometry*)g;
}

static inline OimoGeometry* oimo_geometry_box(OimoScalar hw, OimoScalar hh, OimoScalar hd) {
    if (_oimo_box_pool_idx >= OIMO_MAX_GEOMETRIES) {
        debugf("Oimo: box geometry pool exhausted (%d max)\n", OIMO_MAX_GEOMETRIES);
        return NULL;
    }
    OimoBoxGeometry* g = &_oimo_box_pool[_oimo_box_pool_idx++];
    oimo_box_geometry_init3(g, hw, hh, hd);
    return (OimoGeometry*)g;
}

static inline OimoGeometry* oimo_geometry_capsule(OimoScalar radius, OimoScalar halfHeight) {
    if (_oimo_capsule_pool_idx >= OIMO_MAX_GEOMETRIES) {
        debugf("Oimo: capsule geometry pool exhausted (%d max)\n", OIMO_MAX_GEOMETRIES);
        return NULL;
    }
    OimoCapsuleGeometry* g = &_oimo_capsule_pool[_oimo_capsule_pool_idx++];
    oimo_capsule_geometry_init(g, radius, halfHeight);
    return (OimoGeometry*)g;
}

// Reset pools
static inline void oimo_geometry_pools_reset(void) {
    _oimo_sphere_pool_idx = 0;
    _oimo_box_pool_idx = 0;
    _oimo_capsule_pool_idx = 0;
}

// Function aliases
#define oimo_rigidbody_init             oimo_rigid_body_init
#define oimo_rigidbody_add_shape        oimo_rigid_body_add_shape
#define oimo_rigidbody_remove_shape     oimo_rigid_body_remove_shape
#define oimo_rigidbody_update_mass      oimo_rigid_body_update_mass


#define oimo_world_add_rigidbody        oimo_world_add_rigid_body
#define oimo_world_remove_rigidbody     oimo_world_remove_rigid_body

#endif
