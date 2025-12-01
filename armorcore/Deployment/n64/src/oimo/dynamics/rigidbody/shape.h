#ifndef OIMO_DYNAMICS_RIGIDBODY_SHAPE_H
#define OIMO_DYNAMICS_RIGIDBODY_SHAPE_H

#include "../../common/transform.h"
#include "../../collision/geometry/geometry.h"
#include "../../collision/geometry/aabb.h"
#include "../../collision/broadphase/proxy.h"
#include "shape_config.h"

// Forward declarations
struct OimoRigidBody;
struct OimoWorld;

typedef struct OimoShape {
    int _id;
    struct OimoShape* _prev;
    struct OimoShape* _next;
    struct OimoRigidBody* _rigidBody;
    OimoGeometry* _geom;
    int _isTrigger;

    OimoTransform _localTransform;  // Relative to rigid body
    OimoTransform _ptransform;      // Previous world transform
    OimoTransform _transform;       // Current world transform

    OimoScalar _restitution;
    OimoScalar _friction;
    OimoScalar _density;

    OimoAabb _aabb;
    OimoProxy* _proxy;

    int _collisionGroup;
    int _collisionMask;

    void* userData;
} OimoShape;

// Initialize shape from config
static inline void oimo_shape_init(OimoShape* shape, const OimoShapeConfig* config) {
    shape->_id = -1;
    shape->_prev = NULL;
    shape->_next = NULL;
    shape->_rigidBody = NULL;
    shape->_isTrigger = 0;

    shape->_localTransform = oimo_transform(&config->position, &config->rotation);
    shape->_ptransform = oimo_transform_copy(&shape->_localTransform);
    shape->_transform = oimo_transform_copy(&shape->_localTransform);

    shape->_restitution = config->restitution;
    shape->_friction = config->friction;
    shape->_density = config->density;
    shape->_geom = config->geometry;
    shape->_collisionGroup = config->collisionGroup;
    shape->_collisionMask = config->collisionMask;

    shape->_aabb = oimo_aabb_zero();
    shape->_proxy = NULL;
    shape->userData = NULL;
}

// Forward declaration for capsule geometry
#include "../../collision/geometry/capsule_geometry.h"

// Sync shape transforms with rigid body (called during simulation)
// tf1 = previous body transform, tf2 = current body transform
// 1:1 from OimoPhysics Shape._sync
static inline void oimo_shape_sync(OimoShape* shape, const OimoTransform* tf1, const OimoTransform* tf2) {
    // _ptransform = _localTransform * tf1
    shape->_ptransform = oimo_transform_mul(&shape->_localTransform, tf1);
    // _transform = _localTransform * tf2
    shape->_transform = oimo_transform_mul(&shape->_localTransform, tf2);

    // Compute combined AABB from both transforms
    OimoAabb aabb1, aabb2;

    // Compute AABB at previous transform
    if (shape->_geom->type == OIMO_GEOMETRY_SPHERE) {
        OimoSphereGeometry* sphere = (OimoSphereGeometry*)shape->_geom;
        oimo_sphere_geometry_compute_aabb(sphere, &aabb1, &shape->_ptransform);
        oimo_sphere_geometry_compute_aabb(sphere, &aabb2, &shape->_transform);
    } else if (shape->_geom->type == OIMO_GEOMETRY_BOX) {
        OimoBoxGeometry* box = (OimoBoxGeometry*)shape->_geom;
        oimo_box_geometry_compute_aabb(box, &aabb1, &shape->_ptransform);
        oimo_box_geometry_compute_aabb(box, &aabb2, &shape->_transform);
    } else if (shape->_geom->type == OIMO_GEOMETRY_CAPSULE) {
        OimoCapsuleGeometry* capsule = (OimoCapsuleGeometry*)shape->_geom;
        oimo_capsule_geometry_compute_aabb(capsule, &aabb1, &shape->_ptransform);
        oimo_capsule_geometry_compute_aabb(capsule, &aabb2, &shape->_transform);
    }

    // Combine AABBs (min of mins, max of maxes)
    shape->_aabb.min.x = oimo_min(aabb1.min.x, aabb2.min.x);
    shape->_aabb.min.y = oimo_min(aabb1.min.y, aabb2.min.y);
    shape->_aabb.min.z = oimo_min(aabb1.min.z, aabb2.min.z);
    shape->_aabb.max.x = oimo_max(aabb1.max.x, aabb2.max.x);
    shape->_aabb.max.y = oimo_max(aabb1.max.y, aabb2.max.y);
    shape->_aabb.max.z = oimo_max(aabb1.max.z, aabb2.max.z);

    // CRITICAL: Update proxy AABB for broadphase collision detection
    // 1:1 from OimoPhysics: _rigidBody._world._broadPhase.moveProxy(_proxy, _aabb, displacement)
    if (shape->_proxy != NULL) {
        shape->_proxy->_aabbMin = shape->_aabb.min;
        shape->_proxy->_aabbMax = shape->_aabb.max;
    }
}

// Getters
static inline OimoScalar oimo_shape_get_friction(const OimoShape* shape) {
    return shape->_friction;
}

static inline void oimo_shape_set_friction(OimoShape* shape, OimoScalar friction) {
    shape->_friction = friction;
}

static inline OimoScalar oimo_shape_get_restitution(const OimoShape* shape) {
    return shape->_restitution;
}

static inline void oimo_shape_set_restitution(OimoShape* shape, OimoScalar restitution) {
    shape->_restitution = restitution;
}

static inline OimoScalar oimo_shape_get_density(const OimoShape* shape) {
    return shape->_density;
}

static inline OimoTransform oimo_shape_get_local_transform(const OimoShape* shape) {
    return oimo_transform_copy(&shape->_localTransform);
}

static inline OimoTransform oimo_shape_get_transform(const OimoShape* shape) {
    return oimo_transform_copy(&shape->_transform);
}

static inline OimoAabb oimo_shape_get_aabb(const OimoShape* shape) {
    return oimo_aabb_copy(&shape->_aabb);
}

static inline OimoGeometry* oimo_shape_get_geometry(const OimoShape* shape) {
    return shape->_geom;
}

static inline int oimo_shape_get_collision_group(const OimoShape* shape) {
    return shape->_collisionGroup;
}

static inline void oimo_shape_set_collision_group(OimoShape* shape, int group) {
    shape->_collisionGroup = group;
}

static inline int oimo_shape_get_collision_mask(const OimoShape* shape) {
    return shape->_collisionMask;
}

static inline void oimo_shape_set_collision_mask(OimoShape* shape, int mask) {
    shape->_collisionMask = mask;
}

static inline struct OimoRigidBody* oimo_shape_get_rigid_body(const OimoShape* shape) {
    return shape->_rigidBody;
}

static inline OimoShape* oimo_shape_get_prev(const OimoShape* shape) {
    return shape->_prev;
}

static inline OimoShape* oimo_shape_get_next(const OimoShape* shape) {
    return shape->_next;
}

#endif // OIMO_DYNAMICS_RIGIDBODY_SHAPE_H
