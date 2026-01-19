#pragma once

// contact.h
// 1:1 port from OimoPhysics Contact.hx

#include <stdbool.h>
#include "../common/vec3.h"
#include "../collision/narrowphase/detector.h"
#include "../collision/narrowphase/detector_result.h"
#include "rigidbody/shape.h"
#include "rigidbody/rigid_body.h"
#include "contact_link.h"
#include "constraint/contact/manifold.h"
#include "constraint/contact/manifold_updater.h"
#include "constraint/contact/contact_constraint.h"
#include "constraint/solver/pgs/pgs_contact_constraint_solver.h"

typedef struct OimoContact {
    struct OimoContact* _next;
    struct OimoContact* _prev;

    OimoContactLink _link1;
    OimoContactLink _link2;

    OimoShape* _s1;
    OimoShape* _s2;
    OimoRigidBody* _b1;
    OimoRigidBody* _b2;

    // Detector data
    OimoDetector* _detector;
    OimoDetectorResult _detectorResult;

    // Temp flags
    bool _latest;
    bool _shouldBeSkipped;

    // Constraint/manifold data
    OimoManifold _manifold;
    OimoManifoldUpdater _updater;
    OimoContactConstraint _contactConstraint;
    OimoPgsContactConstraintSolver _solver;

    bool _touching;
    bool _triggering;  // True if either shape is a trigger
} OimoContact;

static inline void oimo_contact_init(OimoContact* c) {
    c->_next = NULL;
    c->_prev = NULL;
    c->_link1 = oimo_contact_link_create();
    c->_link2 = oimo_contact_link_create();
    c->_s1 = NULL;
    c->_s2 = NULL;
    c->_b1 = NULL;
    c->_b2 = NULL;
    c->_detector = NULL;
    c->_detectorResult = oimo_detector_result_create();
    c->_latest = false;
    c->_shouldBeSkipped = false;
    c->_manifold = oimo_manifold_create();
    oimo_manifold_updater_init(&c->_updater, &c->_manifold);
    oimo_contact_constraint_init(&c->_contactConstraint, &c->_manifold);
    oimo_pgs_contact_solver_init(&c->_solver, &c->_contactConstraint);
    c->_touching = false;
    c->_triggering = false;
}

// Attach contact to shapes
static inline void oimo_contact_attach(OimoContact* c, OimoShape* s1, OimoShape* s2, OimoDetector* detector) {
    c->_s1 = s1;
    c->_s2 = s2;
    c->_b1 = s1->_rigidBody;
    c->_b2 = s2->_rigidBody;
    c->_touching = false;
    c->_triggering = false;
    c->_detector = detector;

    // Attach links to rigid bodies
    c->_link1._contact = c;
    c->_link2._contact = c;
    c->_link1._other = c->_b2;
    c->_link2._other = c->_b1;

    // Add to rigid body contact link lists
    // Link1 to b1
    c->_link1._next = c->_b1->_contactLinkList;
    c->_link1._prev = NULL;
    if (c->_b1->_contactLinkList != NULL) {
        c->_b1->_contactLinkList->_prev = &c->_link1;
    }
    c->_b1->_contactLinkList = &c->_link1;
    if (c->_b1->_contactLinkListLast == NULL) {
        c->_b1->_contactLinkListLast = &c->_link1;
    }
    c->_b1->_numContactLinks++;

    // Link2 to b2
    c->_link2._next = c->_b2->_contactLinkList;
    c->_link2._prev = NULL;
    if (c->_b2->_contactLinkList != NULL) {
        c->_b2->_contactLinkList->_prev = &c->_link2;
    }
    c->_b2->_contactLinkList = &c->_link2;
    if (c->_b2->_contactLinkListLast == NULL) {
        c->_b2->_contactLinkListLast = &c->_link2;
    }
    c->_b2->_numContactLinks++;

    oimo_contact_constraint_attach(&c->_contactConstraint, s1, s2);
}

// Detach contact from shapes
static inline void oimo_contact_detach(OimoContact* c) {
    // Remove link1 from b1
    if (c->_link1._prev != NULL) {
        c->_link1._prev->_next = c->_link1._next;
    } else {
        c->_b1->_contactLinkList = c->_link1._next;
    }
    if (c->_link1._next != NULL) {
        c->_link1._next->_prev = c->_link1._prev;
    } else {
        c->_b1->_contactLinkListLast = c->_link1._prev;
    }
    c->_b1->_numContactLinks--;

    // Remove link2 from b2
    if (c->_link2._prev != NULL) {
        c->_link2._prev->_next = c->_link2._next;
    } else {
        c->_b2->_contactLinkList = c->_link2._next;
    }
    if (c->_link2._next != NULL) {
        c->_link2._next->_prev = c->_link2._prev;
    } else {
        c->_b2->_contactLinkListLast = c->_link2._prev;
    }
    c->_b2->_numContactLinks--;

    c->_link1._other = NULL;
    c->_link2._other = NULL;
    c->_link1._contact = NULL;
    c->_link2._contact = NULL;

    c->_s1 = NULL;
    c->_s2 = NULL;
    c->_b1 = NULL;
    c->_b2 = NULL;
    c->_touching = false;
    c->_triggering = false;

    oimo_manifold_clear(&c->_manifold);
    c->_detector = NULL;

    oimo_contact_constraint_detach(&c->_contactConstraint);
}

// Update manifold with collision detection result
// Uses collision_matrix for detection dispatch
static inline void oimo_contact_update_manifold_with_matrix(
    OimoContact* c,
    OimoCollisionMatrix* matrix)
{
    if (c->_s1 == NULL || c->_s2 == NULL) return;
    if (c->_s1->_geom == NULL || c->_s2->_geom == NULL) return;

    OimoTransform* tf1 = &c->_s1->_transform;
    OimoTransform* tf2 = &c->_s2->_transform;

    // Run narrowphase detection using collision matrix
    oimo_collision_matrix_detect(matrix, &c->_detectorResult,
        c->_s1->_geom, c->_s2->_geom, tf1, tf2);

    if (c->_detectorResult.num_points > 0) {
        // Build basis from normal
        oimo_manifold_build_basis(&c->_manifold, c->_detectorResult.normal);

        // Incremental update for persistent contacts
        if (c->_manifold._numPoints > 0) {
            oimo_manifold_updater_incremental_update(&c->_updater, &c->_detectorResult, tf1, tf2);
        } else {
            oimo_manifold_updater_total_update(&c->_updater, &c->_detectorResult, tf1, tf2);
        }

        c->_touching = true;
        // 1:1 from OimoPhysics: _triggering = _touching && (_s1._isTrigger || _s2._isTrigger)
        c->_triggering = (c->_s1->_isTrigger || c->_s2->_isTrigger);
    } else {
        oimo_manifold_clear(&c->_manifold);
        c->_touching = false;
        c->_triggering = false;
    }
}

static inline bool oimo_contact_is_touching(const OimoContact* c) {
    return c->_touching;
}

static inline OimoShape* oimo_contact_get_shape1(const OimoContact* c) {
    return c->_s1;
}

static inline OimoShape* oimo_contact_get_shape2(const OimoContact* c) {
    return c->_s2;
}

static inline OimoManifold* oimo_contact_get_manifold(OimoContact* c) {
    return &c->_manifold;
}

static inline OimoContact* oimo_contact_get_next(const OimoContact* c) {
    return c->_next;
}

static inline OimoContact* oimo_contact_get_prev(const OimoContact* c) {
    return c->_prev;
}
