#ifndef OIMO_DYNAMICS_RIGIDBODY_RIGID_BODY_H
#define OIMO_DYNAMICS_RIGIDBODY_RIGID_BODY_H

#include "../../common/vec3.h"
#include "../../common/mat3.h"
#include "../../common/quat.h"
#include "../../common/transform.h"
#include "../../common/setting.h"
#include "../../common/math_util.h"
#include "rigid_body_type.h"
#include "rigid_body_config.h"
#include "mass_data.h"
#include "shape.h"

// Forward declarations
struct OimoWorld;
struct OimoContactLink;
struct OimoJointLink;

typedef struct OimoRigidBody {
    struct OimoRigidBody* _next;
    struct OimoRigidBody* _prev;

    // Shape linked list
    OimoShape* _shapeList;
    OimoShape* _shapeListLast;
    int _numShapes;

    // Velocities
    OimoVec3 _vel;
    OimoVec3 _angVel;
    OimoVec3 _pseudoVel;
    OimoVec3 _angPseudoVel;

    // Transforms
    OimoTransform _ptransform;  // Previous
    OimoTransform _transform;   // Current

    int _type;

    // Sleeping
    OimoScalar _sleepTime;
    int _sleeping;
    int _autoSleep;
    OimoScalar _sleepingVelocityThreshold;
    OimoScalar _sleepingAngularVelocityThreshold;
    OimoScalar _sleepingTimeThreshold;

    // Mass properties
    OimoScalar _mass;
    OimoScalar _invMass;
    OimoMat3 _localInertia;
    OimoMat3 _invLocalInertia;
    OimoMat3 _invLocalInertiaWithoutRotFactor;
    OimoMat3 _invInertia;
    OimoVec3 _rotFactor;

    // Damping
    OimoScalar _linearDamping;
    OimoScalar _angularDamping;

    // Forces (accumulated per frame)
    OimoVec3 _force;
    OimoVec3 _torque;

    // Contact impulses (for querying)
    OimoVec3 _linearContactImpulse;
    OimoVec3 _angularContactImpulse;

    // World reference
    struct OimoWorld* _world;

    // Contact/Joint links
    struct OimoContactLink* _contactLinkList;
    struct OimoContactLink* _contactLinkListLast;
    int _numContactLinks;

    struct OimoJointLink* _jointLinkList;
    struct OimoJointLink* _jointLinkListLast;
    int _numJointLinks;

    int _addedToIsland;
    OimoScalar _gravityScale;

    void* userData;
} OimoRigidBody;

static inline void oimo_rigid_body_update_inv_inertia(OimoRigidBody* rb) {
    // _invInertia = R * _invLocalInertia * R^T
    OimoMat3 tmp = oimo_mat3_mul(&rb->_transform.rotation, &rb->_invLocalInertia);
    OimoMat3 rt = oimo_mat3_transpose(&rb->_transform.rotation);
    rb->_invInertia = oimo_mat3_mul(&tmp, &rt);
}

static inline void oimo_rigid_body_complete_mass_data(OimoRigidBody* rb) {
    OimoScalar det = oimo_mat3_determinant(&rb->_localInertia);

    if (rb->_mass > 0 && det > 0 && rb->_type == OIMO_RIGID_BODY_DYNAMIC) {
        rb->_invMass = 1.0f / rb->_mass;
        rb->_invLocalInertia = oimo_mat3_inverse(&rb->_localInertia);
        rb->_invLocalInertiaWithoutRotFactor = rb->_invLocalInertia;

        // Apply rotation factor
        rb->_invLocalInertia.e00 *= rb->_rotFactor.x;
        rb->_invLocalInertia.e10 *= rb->_rotFactor.x;
        rb->_invLocalInertia.e20 *= rb->_rotFactor.x;
        rb->_invLocalInertia.e01 *= rb->_rotFactor.y;
        rb->_invLocalInertia.e11 *= rb->_rotFactor.y;
        rb->_invLocalInertia.e21 *= rb->_rotFactor.y;
        rb->_invLocalInertia.e02 *= rb->_rotFactor.z;
        rb->_invLocalInertia.e12 *= rb->_rotFactor.z;
        rb->_invLocalInertia.e22 *= rb->_rotFactor.z;
    } else {
        rb->_invMass = 0;
        rb->_invLocalInertia = oimo_mat3_zero();
        rb->_invLocalInertiaWithoutRotFactor = oimo_mat3_zero();

        // Minimum mass for dynamic bodies to avoid NaN
        if (rb->_type == OIMO_RIGID_BODY_DYNAMIC) {
            rb->_invMass = 1e-9f;
            rb->_invLocalInertiaWithoutRotFactor = oimo_mat3(
                1e-9f, 0, 0,
                0, 1e-9f, 0,
                0, 0, 1e-9f
            );
            rb->_invLocalInertia = rb->_invLocalInertiaWithoutRotFactor;
        }
    }
    oimo_rigid_body_update_inv_inertia(rb);
}

static inline void oimo_rigid_body_sync_shapes(OimoRigidBody* rb) {
    OimoShape* s = rb->_shapeList;
    while (s != NULL) {
        oimo_shape_sync(s, &rb->_ptransform, &rb->_transform);
        s = s->_next;
    }
}

static inline void oimo_rigid_body_update_mass(OimoRigidBody* rb);

static inline void oimo_rigid_body_shape_modified(OimoRigidBody* rb) {
    oimo_rigid_body_update_mass(rb);
    oimo_rigid_body_sync_shapes(rb);
}

static inline void oimo_rigid_body_wake_up(OimoRigidBody* rb) {
    rb->_sleeping = 0;
    rb->_sleepTime = 0;
}

static inline void oimo_rigid_body_sleep(OimoRigidBody* rb) {
    rb->_sleeping = 1;
    rb->_sleepTime = 0;
}

static inline void oimo_rigid_body_update_transform_ext(OimoRigidBody* rb) {
    rb->_ptransform = oimo_transform_copy(&rb->_transform);
    oimo_rigid_body_sync_shapes(rb);
    oimo_rigid_body_wake_up(rb);
}

static inline void oimo_rigid_body_init(OimoRigidBody* rb, const OimoRigidBodyConfig* config) {
    rb->_next = NULL;
    rb->_prev = NULL;

    rb->_shapeList = NULL;
    rb->_shapeListLast = NULL;
    rb->_numShapes = 0;

    rb->_contactLinkList = NULL;
    rb->_contactLinkListLast = NULL;
    rb->_numContactLinks = 0;

    rb->_jointLinkList = NULL;
    rb->_jointLinkListLast = NULL;
    rb->_numJointLinks = 0;

    rb->_vel = config->linearVelocity;
    rb->_angVel = config->angularVelocity;
    rb->_pseudoVel = oimo_vec3_zero();
    rb->_angPseudoVel = oimo_vec3_zero();

    rb->_ptransform = oimo_transform(&config->position, &config->rotation);
    rb->_transform = oimo_transform_copy(&rb->_ptransform);

    rb->_type = config->type;

    rb->_sleepTime = 0;
    rb->_sleeping = 0;
    rb->_autoSleep = config->autoSleep;
    rb->_sleepingVelocityThreshold = config->sleepingVelocityThreshold;
    rb->_sleepingAngularVelocityThreshold = config->sleepingAngularVelocityThreshold;
    rb->_sleepingTimeThreshold = config->sleepingTimeThreshold;

    rb->_mass = 0;
    rb->_invMass = 0;
    rb->_localInertia = oimo_mat3_zero();
    rb->_invLocalInertia = oimo_mat3_zero();
    rb->_invLocalInertiaWithoutRotFactor = oimo_mat3_zero();
    rb->_invInertia = oimo_mat3_zero();

    rb->_linearDamping = config->linearDamping;
    rb->_angularDamping = config->angularDamping;

    rb->_force = oimo_vec3_zero();
    rb->_torque = oimo_vec3_zero();
    rb->_linearContactImpulse = oimo_vec3_zero();
    rb->_angularContactImpulse = oimo_vec3_zero();

    rb->_rotFactor = oimo_vec3(1, 1, 1);
    rb->_addedToIsland = 0;
    rb->_gravityScale = 1.0f;
    rb->_world = NULL;
    rb->userData = NULL;
}

static inline void oimo_rigid_body_apply_translation(OimoRigidBody* rb, const OimoVec3* translation) {
    oimo_vec3_add_eq(&rb->_transform.position, translation);
}

static inline void oimo_rigid_body_apply_rotation(OimoRigidBody* rb, const OimoVec3* rotation) {
    OimoScalar theta = oimo_vec3_len(*rotation);
    OimoScalar halfTheta = theta * 0.5f;
    OimoScalar rotationToSinAxisFactor;
    OimoScalar cosHalfTheta;

    if (halfTheta < 0.5f) {
        // Maclaurin expansion for small angles
        OimoScalar ht2 = halfTheta * halfTheta;
        rotationToSinAxisFactor = 0.5f * (1.0f - ht2 * (1.0f / 6.0f) + ht2 * ht2 * (1.0f / 120.0f));
        cosHalfTheta = 1.0f - ht2 * 0.5f + ht2 * ht2 * (1.0f / 24.0f);
    } else {
        rotationToSinAxisFactor = oimo_sin(halfTheta) / theta;
        cosHalfTheta = oimo_cos(halfTheta);
    }

    OimoVec3 sinAxis = oimo_vec3_scale(*rotation, rotationToSinAxisFactor);
    OimoQuat dq = oimo_quat(sinAxis.x, sinAxis.y, sinAxis.z, cosHalfTheta);

    // Get current rotation as quaternion
    OimoQuat q = oimo_mat3_to_quat(&rb->_transform.rotation);

    // Integrate: q = dq * q
    q = oimo_quat_mul(&dq, &q);
    q = oimo_quat_normalize(&q);

    // Update rotation matrix
    rb->_transform.rotation = oimo_quat_to_mat3(&q);

    oimo_rigid_body_update_inv_inertia(rb);
}

static inline void oimo_rigid_body_integrate(OimoRigidBody* rb, OimoScalar dt) {
    if (rb->_type == OIMO_RIGID_BODY_STATIC) {
        rb->_vel = oimo_vec3_zero();
        rb->_angVel = oimo_vec3_zero();
        rb->_pseudoVel = oimo_vec3_zero();
        rb->_angPseudoVel = oimo_vec3_zero();
        return;
    }

    OimoVec3 translation = oimo_vec3_scale(rb->_vel, dt);
    OimoVec3 rotation = oimo_vec3_scale(rb->_angVel, dt);

    OimoScalar translationLengthSq = oimo_vec3_len_sq(translation);
    OimoScalar rotationLengthSq = oimo_vec3_len_sq(rotation);

    if (translationLengthSq <= OIMO_EPSILON && rotationLengthSq <= OIMO_EPSILON) {
        return;
    }

    // Limit linear velocity - use inv_sqrt to avoid sqrt in common case
    if (translationLengthSq > OIMO_MAX_TRANSLATION_PER_STEP * OIMO_MAX_TRANSLATION_PER_STEP) {
        OimoScalar l = OIMO_MAX_TRANSLATION_PER_STEP * oimo_inv_sqrt(translationLengthSq);
        oimo_vec3_scale_eq(&rb->_vel, l);
        oimo_vec3_scale_eq(&translation, l);
    }

    // Limit angular velocity - use inv_sqrt to avoid sqrt in common case
    if (rotationLengthSq > OIMO_MAX_ROTATION_PER_STEP * OIMO_MAX_ROTATION_PER_STEP) {
        OimoScalar l = OIMO_MAX_ROTATION_PER_STEP * oimo_inv_sqrt(rotationLengthSq);
        oimo_vec3_scale_eq(&rb->_angVel, l);
        oimo_vec3_scale_eq(&rotation, l);
    }

    oimo_rigid_body_apply_translation(rb, &translation);
    oimo_rigid_body_apply_rotation(rb, &rotation);
}

static inline void oimo_rigid_body_integrate_pseudo_velocity(OimoRigidBody* rb) {
    OimoScalar pseudoVelLengthSq = oimo_vec3_len_sq(rb->_pseudoVel);
    OimoScalar angPseudoVelLengthSq = oimo_vec3_len_sq(rb->_angPseudoVel);

    if (pseudoVelLengthSq <= OIMO_EPSILON && angPseudoVelLengthSq <= OIMO_EPSILON) {
        return;
    }

    if (rb->_type == OIMO_RIGID_BODY_STATIC) {
        rb->_pseudoVel = oimo_vec3_zero();
        rb->_angPseudoVel = oimo_vec3_zero();
        return;
    }

    OimoVec3 translation = rb->_pseudoVel;
    OimoVec3 rotation = rb->_angPseudoVel;

    rb->_pseudoVel = oimo_vec3_zero();
    rb->_angPseudoVel = oimo_vec3_zero();

    oimo_rigid_body_apply_translation(rb, &translation);
    oimo_rigid_body_apply_rotation(rb, &rotation);
}

static inline int oimo_rigid_body_is_sleepy(const OimoRigidBody* rb) {
    return rb->_autoSleep &&
           oimo_vec3_len_sq(rb->_vel) < rb->_sleepingVelocityThreshold * rb->_sleepingVelocityThreshold &&
           oimo_vec3_len_sq(rb->_angVel) < rb->_sleepingAngularVelocityThreshold * rb->_sleepingAngularVelocityThreshold;
}

static inline int oimo_rigid_body_is_alone(const OimoRigidBody* rb) {
    return rb->_numContactLinks == 0 && rb->_numJointLinks == 0;
}

static inline void oimo_rigid_body_update_mass(OimoRigidBody* rb) {
    OimoMat3 totalInertia = oimo_mat3_zero();
    OimoScalar totalMass = 0;

    OimoShape* s = rb->_shapeList;
    while (s != NULL) {
        OimoGeometry* g = s->_geom;

        OimoScalar mass = s->_density * g->volume;

        // I_transformed = R * I_localCoeff * R^T * mass
        OimoMat3 inertia = oimo_mat3_mul(&s->_localTransform.rotation, &g->inertia_coeff);
        OimoMat3 rt = oimo_mat3_transpose(&s->_localTransform.rotation);
        inertia = oimo_mat3_mul(&inertia, &rt);
        inertia = oimo_mat3_scale(&inertia, mass);

        // Add parallel axis theorem contribution
        OimoVec3* p = &s->_localTransform.position;
        OimoScalar xx = p->x * p->x, yy = p->y * p->y, zz = p->z * p->z;
        OimoScalar xy = p->x * p->y, xz = p->x * p->z, yz = p->y * p->z;

        OimoMat3 cogInertia = oimo_mat3(
            (yy + zz) * mass, -xy * mass,       -xz * mass,
            -xy * mass,       (xx + zz) * mass, -yz * mass,
            -xz * mass,       -yz * mass,       (xx + yy) * mass
        );

        inertia = oimo_mat3_add(&inertia, &cogInertia);

        totalMass += mass;
        totalInertia = oimo_mat3_add(&totalInertia, &inertia);

        s = s->_next;
    }

    rb->_mass = totalMass;
    rb->_localInertia = totalInertia;

    oimo_rigid_body_complete_mass_data(rb);
    oimo_rigid_body_wake_up(rb);
}

// Set mass data directly (like OimoPhysics setMassData)
// This overrides the auto-calculated mass from density * volume
static inline void oimo_rigid_body_set_mass_data(OimoRigidBody* rb, const OimoMassData* massData) {
    rb->_mass = massData->mass;
    rb->_localInertia = massData->localInertia;

    oimo_rigid_body_complete_mass_data(rb);
    oimo_rigid_body_wake_up(rb);
}

// Convenience function to just set mass (keeping computed inertia)
static inline void oimo_rigid_body_set_mass(OimoRigidBody* rb, OimoScalar mass) {
    rb->_mass = mass;
    oimo_rigid_body_complete_mass_data(rb);
    oimo_rigid_body_wake_up(rb);
}

static inline OimoVec3 oimo_rigid_body_get_position(const OimoRigidBody* rb) {
    return rb->_transform.position;
}

static inline void oimo_rigid_body_set_position(OimoRigidBody* rb, const OimoVec3* position) {
    rb->_transform.position = *position;
    oimo_rigid_body_update_transform_ext(rb);
}

static inline OimoMat3 oimo_rigid_body_get_rotation(const OimoRigidBody* rb) {
    return rb->_transform.rotation;
}

static inline void oimo_rigid_body_set_rotation(OimoRigidBody* rb, const OimoMat3* rotation) {
    rb->_transform.rotation = *rotation;
    oimo_rigid_body_update_inv_inertia(rb);
    oimo_rigid_body_update_transform_ext(rb);
}

static inline OimoQuat oimo_rigid_body_get_orientation(const OimoRigidBody* rb) {
    return oimo_mat3_to_quat(&rb->_transform.rotation);
}

static inline void oimo_rigid_body_set_orientation(OimoRigidBody* rb, const OimoQuat* q) {
    rb->_transform.rotation = oimo_quat_to_mat3(q);
    oimo_rigid_body_update_inv_inertia(rb);
    oimo_rigid_body_update_transform_ext(rb);
}

static inline OimoTransform oimo_rigid_body_get_transform(const OimoRigidBody* rb) {
    return oimo_transform_copy(&rb->_transform);
}

static inline void oimo_rigid_body_set_transform(OimoRigidBody* rb, const OimoTransform* tf) {
    rb->_transform = oimo_transform_copy(tf);
    oimo_rigid_body_update_inv_inertia(rb);
    oimo_rigid_body_update_transform_ext(rb);
}

static inline OimoScalar oimo_rigid_body_get_mass(const OimoRigidBody* rb) {
    return rb->_mass;
}

static inline OimoVec3 oimo_rigid_body_get_linear_velocity(const OimoRigidBody* rb) {
    return rb->_vel;
}

static inline void oimo_rigid_body_set_linear_velocity(OimoRigidBody* rb, const OimoVec3* vel) {
    if (rb->_type == OIMO_RIGID_BODY_STATIC) {
        rb->_vel = oimo_vec3_zero();
    } else {
        rb->_vel = *vel;
    }
    oimo_rigid_body_wake_up(rb);
}

static inline OimoVec3 oimo_rigid_body_get_angular_velocity(const OimoRigidBody* rb) {
    return rb->_angVel;
}

static inline void oimo_rigid_body_set_angular_velocity(OimoRigidBody* rb, const OimoVec3* vel) {
    if (rb->_type == OIMO_RIGID_BODY_STATIC) {
        rb->_angVel = oimo_vec3_zero();
    } else {
        rb->_angVel = *vel;
    }
    oimo_rigid_body_wake_up(rb);
}

static inline void oimo_rigid_body_apply_impulse(OimoRigidBody* rb, const OimoVec3* impulse, const OimoVec3* positionInWorld) {
    // Linear impulse
    oimo_vec3_add_scaled_eq(&rb->_vel, impulse, rb->_invMass);

    // Angular impulse
    OimoVec3 r = oimo_vec3_sub(*positionInWorld, rb->_transform.position);
    OimoVec3 angImp = oimo_vec3_cross(r, *impulse);
    angImp = oimo_mat3_mul_vec3(&rb->_invInertia, angImp);
    oimo_vec3_add_eq(&rb->_angVel, &angImp);

    oimo_rigid_body_wake_up(rb);
}

static inline void oimo_rigid_body_apply_linear_impulse(OimoRigidBody* rb, const OimoVec3* impulse) {
    oimo_vec3_add_scaled_eq(&rb->_vel, impulse, rb->_invMass);
    oimo_rigid_body_wake_up(rb);
}

static inline void oimo_rigid_body_apply_angular_impulse(OimoRigidBody* rb, const OimoVec3* impulse) {
    OimoVec3 angImp = oimo_mat3_mul_vec3(&rb->_invInertia, *impulse);
    oimo_vec3_add_eq(&rb->_angVel, &angImp);
    oimo_rigid_body_wake_up(rb);
}

static inline void oimo_rigid_body_apply_force(OimoRigidBody* rb, const OimoVec3* force, const OimoVec3* positionInWorld) {
    oimo_vec3_add_eq(&rb->_force, force);

    OimoVec3 r = oimo_vec3_sub(*positionInWorld, rb->_transform.position);
    OimoVec3 torque = oimo_vec3_cross(r, *force);
    oimo_vec3_add_eq(&rb->_torque, &torque);

    oimo_rigid_body_wake_up(rb);
}

static inline void oimo_rigid_body_apply_force_to_center(OimoRigidBody* rb, const OimoVec3* force) {
    oimo_vec3_add_eq(&rb->_force, force);
    oimo_rigid_body_wake_up(rb);
}

static inline void oimo_rigid_body_apply_torque(OimoRigidBody* rb, const OimoVec3* torque) {
    oimo_vec3_add_eq(&rb->_torque, torque);
    oimo_rigid_body_wake_up(rb);
}

static inline int oimo_rigid_body_get_type(const OimoRigidBody* rb) {
    return rb->_type;
}

static inline void oimo_rigid_body_set_type(OimoRigidBody* rb, int type) {
    rb->_type = type;
    oimo_rigid_body_update_mass(rb);
}

static inline int oimo_rigid_body_is_sleeping(const OimoRigidBody* rb) {
    return rb->_sleeping;
}

static inline OimoScalar oimo_rigid_body_get_gravity_scale(const OimoRigidBody* rb) {
    return rb->_gravityScale;
}

static inline void oimo_rigid_body_set_gravity_scale(OimoRigidBody* rb, OimoScalar scale) {
    rb->_gravityScale = scale;
    oimo_rigid_body_wake_up(rb);
}

static inline int oimo_rigid_body_get_num_shapes(const OimoRigidBody* rb) {
    return rb->_numShapes;
}

static inline OimoShape* oimo_rigid_body_get_shape_list(const OimoRigidBody* rb) {
    return rb->_shapeList;
}

static inline OimoRigidBody* oimo_rigid_body_get_prev(const OimoRigidBody* rb) {
    return rb->_prev;
}

static inline OimoRigidBody* oimo_rigid_body_get_next(const OimoRigidBody* rb) {
    return rb->_next;
}

static inline void oimo_rigid_body_add_shape_internal(OimoRigidBody* rb, OimoShape* shape) {
    // Add to linked list
    if (rb->_shapeListLast != NULL) {
        rb->_shapeListLast->_next = shape;
        shape->_prev = rb->_shapeListLast;
        shape->_next = NULL;
        rb->_shapeListLast = shape;
    } else {
        rb->_shapeList = shape;
        rb->_shapeListLast = shape;
        shape->_prev = NULL;
        shape->_next = NULL;
    }
    rb->_numShapes++;
    shape->_rigidBody = rb;
}

static inline void oimo_rigid_body_remove_shape_internal(OimoRigidBody* rb, OimoShape* shape) {
    // Remove from linked list
    if (shape->_prev != NULL) {
        shape->_prev->_next = shape->_next;
    } else {
        rb->_shapeList = shape->_next;
    }
    if (shape->_next != NULL) {
        shape->_next->_prev = shape->_prev;
    } else {
        rb->_shapeListLast = shape->_prev;
    }
    shape->_prev = NULL;
    shape->_next = NULL;
    rb->_numShapes--;
    shape->_rigidBody = NULL;
}

// Public shape management functions
static inline void oimo_rigid_body_add_shape(OimoRigidBody* rb, OimoShape* shape) {
    oimo_rigid_body_add_shape_internal(rb, shape);
    // Sync transform
    oimo_shape_sync(shape, &rb->_ptransform, &rb->_transform);
}

static inline void oimo_rigid_body_remove_shape(OimoRigidBody* rb, OimoShape* shape) {
    oimo_rigid_body_remove_shape_internal(rb, shape);
}

// Public mass getter/setter (for compatibility with body->mass pattern)
#define mass _mass

// Compatibility aliases (without underscore between rigid and body)
// Note: oimo_rigidbody_apply_force maps to _to_center variant (2 args, not 3)
#define oimo_rigidbody_apply_force           oimo_rigid_body_apply_force_to_center
#define oimo_rigidbody_apply_force_to_center oimo_rigid_body_apply_force_to_center
#define oimo_rigidbody_apply_torque          oimo_rigid_body_apply_torque
#define oimo_rigidbody_apply_impulse         oimo_rigid_body_apply_impulse
#define oimo_rigidbody_apply_linear_impulse  oimo_rigid_body_apply_linear_impulse
#define oimo_rigidbody_apply_angular_impulse oimo_rigid_body_apply_angular_impulse
#define oimo_rigidbody_wake_up               oimo_rigid_body_wake_up
#define oimo_rigidbody_sleep                 oimo_rigid_body_sleep
#define oimo_rigidbody_get_type              oimo_rigid_body_get_type
#define oimo_rigidbody_set_type              oimo_rigid_body_set_type

#endif // OIMO_DYNAMICS_RIGIDBODY_RIGID_BODY_H
