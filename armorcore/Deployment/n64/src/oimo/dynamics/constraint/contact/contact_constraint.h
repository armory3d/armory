// contact_constraint.h
// 1:1 port from OimoPhysics ContactConstraint.hx
#ifndef OIMO_DYNAMICS_CONSTRAINT_CONTACT_CONTACT_CONSTRAINT_H
#define OIMO_DYNAMICS_CONSTRAINT_CONTACT_CONTACT_CONSTRAINT_H

#include "../../../common/vec3.h"
#include "../../../common/mat3.h"
#include "../../../common/transform.h"
#include "../../../common/setting.h"
#include "../../../common/math_util.h"
#include "../../rigidbody/shape.h"
#include "../../rigidbody/rigid_body.h"
#include "../../time_step.h"
#include "../position_correction_algorithm.h"
#include "../info/jacobian_row.h"
#include "../info/contact/contact_solver_info.h"
#include "manifold.h"

typedef struct OimoContactConstraint {
    int _positionCorrectionAlgorithm;
    OimoManifold* _manifold;

    OimoShape* _s1;
    OimoShape* _s2;
    OimoTransform* _tf1;
    OimoTransform* _tf2;
    OimoScalar _invM1;
    OimoScalar _invM2;
    OimoScalar _friction;
    OimoScalar _restitution;

    OimoMat3 _invI1;
    OimoMat3 _invI2;

    OimoRigidBody* _b1;
    OimoRigidBody* _b2;
} OimoContactConstraint;

static inline void oimo_contact_constraint_init(OimoContactConstraint* cc, OimoManifold* manifold) {
    cc->_positionCorrectionAlgorithm = OIMO_POSITION_CORRECTION_BAUMGARTE;
    cc->_manifold = manifold;
    cc->_s1 = NULL;
    cc->_s2 = NULL;
    cc->_tf1 = NULL;
    cc->_tf2 = NULL;
    cc->_invM1 = 0.0f;
    cc->_invM2 = 0.0f;
    cc->_friction = 0.0f;
    cc->_restitution = 0.0f;
    cc->_invI1 = oimo_mat3_identity();
    cc->_invI2 = oimo_mat3_identity();
    cc->_b1 = NULL;
    cc->_b2 = NULL;
}

static inline void oimo_contact_constraint_attach(OimoContactConstraint* cc, OimoShape* s1, OimoShape* s2) {
    cc->_s1 = s1;
    cc->_s2 = s2;
    cc->_b1 = s1->_rigidBody;
    cc->_b2 = s2->_rigidBody;
    cc->_tf1 = &cc->_b1->_transform;
    cc->_tf2 = &cc->_b2->_transform;
}

static inline void oimo_contact_constraint_detach(OimoContactConstraint* cc) {
    cc->_s1 = NULL;
    cc->_s2 = NULL;
    cc->_b1 = NULL;
    cc->_b2 = NULL;
    cc->_tf1 = NULL;
    cc->_tf2 = NULL;
}

static inline void oimo_contact_constraint_sync_manifold(OimoContactConstraint* cc) {
    oimo_manifold_update_depths_and_positions(cc->_manifold, cc->_tf1, cc->_tf2);
}

// Get velocity solver info - 1:1 from ContactConstraint._getVelocitySolverInfo
static inline void oimo_contact_constraint_get_velocity_solver_info(
    OimoContactConstraint* cc,
    OimoTimeStep* timeStep,
    OimoContactSolverInfo* info
) {
    info->b1 = cc->_b1;
    info->b2 = cc->_b2;

    OimoVec3 normal = cc->_manifold->_normal;
    OimoVec3 tangent = cc->_manifold->_tangent;
    OimoVec3 binormal = cc->_manifold->_binormal;

    // Combined friction and restitution
    OimoScalar friction = oimo_sqrt(cc->_s1->_friction * cc->_s2->_friction);
    OimoScalar restitution = oimo_sqrt(cc->_s1->_restitution * cc->_s2->_restitution);

    int num = cc->_manifold->_numPoints;
    info->numRows = 0;

    for (int i = 0; i < num; i++) {
        OimoManifoldPoint* p = &cc->_manifold->_points[i];

        if (p->_depth < 0.0f) {
            p->_disabled = true;
            oimo_contact_impulse_clear(&p->_impulse);
            continue;  // Skip separated points
        } else {
            p->_disabled = false;
        }

        OimoContactSolverInfoRow* row = &info->rows[info->numRows++];

        row->friction = friction;
        row->cfm = 0.0f;

        // Set Jacobian for normal
        OimoJacobianRow* j = &row->jacobianN;
        j->lin1 = normal;
        j->lin2 = normal;
        j->ang1 = oimo_vec3_cross(p->_relPos1, normal);
        j->ang2 = oimo_vec3_cross(p->_relPos2, normal);

        // Set Jacobian for tangent
        j = &row->jacobianT;
        j->lin1 = tangent;
        j->lin2 = tangent;
        j->ang1 = oimo_vec3_cross(p->_relPos1, tangent);
        j->ang2 = oimo_vec3_cross(p->_relPos2, tangent);

        // Set Jacobian for binormal
        j = &row->jacobianB;
        j->lin1 = binormal;
        j->lin2 = binormal;
        j->ang1 = oimo_vec3_cross(p->_relPos1, binormal);
        j->ang2 = oimo_vec3_cross(p->_relPos2, binormal);

        // Compute relative velocity along normal
        j = &row->jacobianN;
        OimoScalar rvn =
            (oimo_vec3_dot(j->lin1, cc->_b1->_vel) + oimo_vec3_dot(j->ang1, cc->_b1->_angVel)) -
            (oimo_vec3_dot(j->lin2, cc->_b2->_vel) + oimo_vec3_dot(j->ang2, cc->_b2->_angVel));

        // Disable bounce for warm-started contacts
        if (rvn < -OIMO_CONTACT_ENABLE_BOUNCE_THRESHOLD && !p->_warmStarted) {
            row->rhs = -rvn * restitution;
        } else {
            row->rhs = 0.0f;
        }

        // Set minimum RHS for Baumgarte position correction
        if (cc->_positionCorrectionAlgorithm == OIMO_POSITION_CORRECTION_BAUMGARTE) {
            if (p->_depth > OIMO_LINEAR_SLOP) {
                OimoScalar minRhs = (p->_depth - OIMO_LINEAR_SLOP) * OIMO_VELOCITY_BAUMGARTE * timeStep->invDt;
                if (row->rhs < minRhs) row->rhs = minRhs;
            }
        }

        // Reset impulses if warm starting is disabled
        if (!p->_warmStarted) {
            oimo_contact_impulse_clear(&p->_impulse);
        }

        row->impulse = &p->_impulse;
    }
}

// Get position solver info - 1:1 from ContactConstraint._getPositionSolverInfo
static inline void oimo_contact_constraint_get_position_solver_info(
    OimoContactConstraint* cc,
    OimoContactSolverInfo* info
) {
    info->b1 = cc->_b1;
    info->b2 = cc->_b2;

    OimoVec3 normal = cc->_manifold->_normal;

    int num = cc->_manifold->_numPoints;
    info->numRows = 0;

    for (int i = 0; i < num; i++) {
        OimoManifoldPoint* p = &cc->_manifold->_points[i];

        if (p->_disabled) {
            continue;  // Skip disabled points
        }

        OimoContactSolverInfoRow* row = &info->rows[info->numRows++];

        // Set normal Jacobian
        OimoJacobianRow* j = &row->jacobianN;
        j->lin1 = normal;
        j->lin2 = normal;
        j->ang1 = oimo_vec3_cross(p->_relPos1, normal);
        j->ang2 = oimo_vec3_cross(p->_relPos2, normal);

        row->rhs = p->_depth - OIMO_LINEAR_SLOP;
        if (row->rhs < 0.0f) {
            row->rhs = 0.0f;
        }

        row->impulse = &p->_impulse;
    }
}

static inline bool oimo_contact_constraint_is_touching(const OimoContactConstraint* cc) {
    for (int i = 0; i < cc->_manifold->_numPoints; i++) {
        if (cc->_manifold->_points[i]._depth >= 0.0f) return true;
    }
    return false;
}

static inline OimoShape* oimo_contact_constraint_get_shape1(const OimoContactConstraint* cc) {
    return cc->_s1;
}

static inline OimoShape* oimo_contact_constraint_get_shape2(const OimoContactConstraint* cc) {
    return cc->_s2;
}

static inline OimoManifold* oimo_contact_constraint_get_manifold(const OimoContactConstraint* cc) {
    return cc->_manifold;
}

#endif // OIMO_DYNAMICS_CONSTRAINT_CONTACT_CONTACT_CONSTRAINT_H
