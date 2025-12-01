// manifold_updater.h
// 1:1 port from OimoPhysics ManifoldUpdater.hx
#ifndef OIMO_DYNAMICS_CONSTRAINT_CONTACT_MANIFOLD_UPDATER_H
#define OIMO_DYNAMICS_CONSTRAINT_CONTACT_MANIFOLD_UPDATER_H

#include "../../../common/vec3.h"
#include "../../../common/mat3.h"
#include "../../../common/transform.h"
#include "../../../common/setting.h"
#include "../../../collision/narrowphase/detector_result.h"
#include "manifold.h"

typedef struct OimoManifoldUpdater {
    OimoManifold* _manifold;
    int numOldPoints;
    OimoManifoldPoint oldPoints[OIMO_MAX_MANIFOLD_POINTS];
} OimoManifoldUpdater;

static inline OimoManifoldUpdater oimo_manifold_updater_create(OimoManifold* manifold) {
    OimoManifoldUpdater updater;
    updater._manifold = manifold;
    updater.numOldPoints = 0;
    for (int i = 0; i < OIMO_MAX_MANIFOLD_POINTS; i++) {
        updater.oldPoints[i] = oimo_manifold_point_create();
    }
    return updater;
}

static inline void oimo_manifold_updater_init(OimoManifoldUpdater* updater, OimoManifold* manifold) {
    updater->_manifold = manifold;
    updater->numOldPoints = 0;
    for (int i = 0; i < OIMO_MAX_MANIFOLD_POINTS; i++) {
        updater->oldPoints[i] = oimo_manifold_point_create();
    }
}

// Remove a manifold point at given index
static inline void oimo_manifold_updater_remove_point(OimoManifoldUpdater* updater, int index) {
    OimoManifold* m = updater->_manifold;
    int lastIndex = --m->_numPoints;
    if (index != lastIndex) {
        OimoManifoldPoint tmp = m->_points[index];
        m->_points[index] = m->_points[lastIndex];
        m->_points[lastIndex] = tmp;
    }
    oimo_manifold_point_clear(&m->_points[lastIndex]);
}

// Remove outdated points - 1:1 from ManifoldUpdater.removeOutdatedPoints
static inline void oimo_manifold_updater_remove_outdated_points(OimoManifoldUpdater* updater) {
    OimoManifold* m = updater->_manifold;
    int index = m->_numPoints;

    while (--index >= 0) {
        OimoManifoldPoint* p = &m->_points[index];

        OimoVec3 diff = oimo_vec3_sub(p->_pos1, p->_pos2);
        OimoScalar dotN = oimo_vec3_dot(m->_normal, diff);

        if (dotN > OIMO_CONTACT_PERSISTENCE_THRESHOLD) {
            oimo_manifold_updater_remove_point(updater, index);
            continue;
        }

        // Compute projection of diff (remove normal component)
        OimoVec3 scaled = oimo_vec3_scale(m->_normal, dotN);
        diff = oimo_vec3_sub(diff, scaled);
        if (oimo_vec3_dot(diff, diff) > OIMO_CONTACT_PERSISTENCE_THRESHOLD * OIMO_CONTACT_PERSISTENCE_THRESHOLD) {
            oimo_manifold_updater_remove_point(updater, index);
            continue;
        }
    }
}

// Compute area of quadrilateral for point selection - 1:1 from ManifoldUpdater.quadAreaFast
static inline OimoScalar oimo_manifold_updater_quad_area_fast(
    OimoVec3 p1, OimoVec3 p2, OimoVec3 p3, OimoVec3 p4
) {
    // Possible diagonals
    OimoVec3 v12 = oimo_vec3_sub(p2, p1);
    OimoVec3 v34 = oimo_vec3_sub(p4, p3);
    OimoVec3 v13 = oimo_vec3_sub(p3, p1);
    OimoVec3 v24 = oimo_vec3_sub(p4, p2);
    OimoVec3 v14 = oimo_vec3_sub(p4, p1);
    OimoVec3 v23 = oimo_vec3_sub(p3, p2);

    OimoVec3 cross1 = oimo_vec3_cross(v12, v34);
    OimoVec3 cross2 = oimo_vec3_cross(v13, v24);
    OimoVec3 cross3 = oimo_vec3_cross(v14, v23);

    OimoScalar a1 = oimo_vec3_dot(cross1, cross1);
    OimoScalar a2 = oimo_vec3_dot(cross2, cross2);
    OimoScalar a3 = oimo_vec3_dot(cross3, cross3);

    if (a1 > a2) {
        return (a1 > a3) ? a1 : a3;
    } else {
        return (a2 > a3) ? a2 : a3;
    }
}

// Compute target index for point replacement - 1:1 from ManifoldUpdater.computeTargetIndex
static inline int oimo_manifold_updater_compute_target_index(
    OimoManifoldUpdater* updater,
    const OimoDetectorResultPoint* newPoint,
    const OimoTransform* tf1,
    const OimoTransform* tf2
) {
    OimoManifold* m = updater->_manifold;
    OimoManifoldPoint* p1 = &m->_points[0];
    OimoManifoldPoint* p2 = &m->_points[1];
    OimoManifoldPoint* p3 = &m->_points[2];
    OimoManifoldPoint* p4 = &m->_points[3];

    OimoScalar maxDepth = p1->_depth;
    int maxDepthIndex = 0;
    if (p2->_depth > maxDepth) { maxDepth = p2->_depth; maxDepthIndex = 1; }
    if (p3->_depth > maxDepth) { maxDepth = p3->_depth; maxDepthIndex = 2; }
    if (p4->_depth > maxDepth) { maxDepth = p4->_depth; maxDepthIndex = 3; }

    OimoVec3 rp1 = oimo_vec3_sub(newPoint->position1, tf1->position);

    OimoScalar a1 = oimo_manifold_updater_quad_area_fast(p2->_relPos1, p3->_relPos1, p4->_relPos1, rp1);
    OimoScalar a2 = oimo_manifold_updater_quad_area_fast(p1->_relPos1, p3->_relPos1, p4->_relPos1, rp1);
    OimoScalar a3 = oimo_manifold_updater_quad_area_fast(p1->_relPos1, p2->_relPos1, p4->_relPos1, rp1);
    OimoScalar a4 = oimo_manifold_updater_quad_area_fast(p1->_relPos1, p2->_relPos1, p3->_relPos1, rp1);

    OimoScalar max = a1;
    int target = 0;
    if ((a2 > max && maxDepthIndex != 1) || maxDepthIndex == 0) { max = a2; target = 1; }
    if (a3 > max && maxDepthIndex != 2) { max = a3; target = 2; }
    if (a4 > max && maxDepthIndex != 3) { max = a4; target = 3; }

    return target;
}

// Add manifold point - 1:1 from ManifoldUpdater.addManifoldPoint
static inline void oimo_manifold_updater_add_point(
    OimoManifoldUpdater* updater,
    const OimoDetectorResultPoint* point,
    const OimoTransform* tf1,
    const OimoTransform* tf2
) {
    OimoManifold* m = updater->_manifold;
    int num = m->_numPoints;

    if (num == OIMO_MAX_MANIFOLD_POINTS) {
        int targetIndex = oimo_manifold_updater_compute_target_index(updater, point, tf1, tf2);
        oimo_manifold_point_initialize(&m->_points[targetIndex], point, tf1, tf2);
        return;
    }

    oimo_manifold_point_initialize(&m->_points[num], point, tf1, tf2);
    m->_numPoints++;
}

// Distance squared between manifold point and result point
static inline OimoScalar oimo_manifold_updater_dist_sq(
    const OimoManifoldPoint* mp,
    const OimoDetectorResultPoint* result,
    const OimoTransform* tf1,
    const OimoTransform* tf2
) {
    OimoVec3 rp1 = oimo_vec3_sub(result->position1, tf1->position);
    OimoVec3 rp2 = oimo_vec3_sub(result->position2, tf2->position);

    OimoVec3 diff1 = oimo_vec3_sub(mp->_relPos1, rp1);
    OimoVec3 diff2 = oimo_vec3_sub(mp->_relPos2, rp2);

    OimoScalar sq1 = oimo_vec3_dot(diff1, diff1);
    OimoScalar sq2 = oimo_vec3_dot(diff2, diff2);

    return (sq1 < sq2) ? sq1 : sq2;
}

// Find nearest contact point - 1:1 from ManifoldUpdater.findNearestContactPointIndex
static inline int oimo_manifold_updater_find_nearest_index(
    OimoManifoldUpdater* updater,
    const OimoDetectorResultPoint* target,
    const OimoTransform* tf1,
    const OimoTransform* tf2
) {
    OimoManifold* m = updater->_manifold;
    OimoScalar nearestSq = OIMO_CONTACT_PERSISTENCE_THRESHOLD * OIMO_CONTACT_PERSISTENCE_THRESHOLD;
    int idx = -1;

    for (int i = 0; i < m->_numPoints; i++) {
        OimoScalar d = oimo_manifold_updater_dist_sq(&m->_points[i], target, tf1, tf2);
        if (d < nearestSq) {
            nearestSq = d;
            idx = i;
        }
    }
    return idx;
}

// Save old data for warm starting
static inline void oimo_manifold_updater_save_old_data(OimoManifoldUpdater* updater) {
    OimoManifold* m = updater->_manifold;
    updater->numOldPoints = m->_numPoints;
    for (int i = 0; i < updater->numOldPoints; i++) {
        oimo_manifold_point_copy_from(&updater->oldPoints[i], &m->_points[i]);
    }
}

// Update contact point by ID for warm starting
static inline void oimo_manifold_updater_update_by_id(OimoManifoldUpdater* updater, OimoManifoldPoint* cp) {
    for (int i = 0; i < updater->numOldPoints; i++) {
        OimoManifoldPoint* ocp = &updater->oldPoints[i];
        if (cp->_id == ocp->_id) {
            oimo_contact_impulse_copy_from(&cp->_impulse, &ocp->_impulse);
            cp->_warmStarted = true;
            break;
        }
    }
}

// Total update - replace all points - 1:1 from ManifoldUpdater.totalUpdate
static inline void oimo_manifold_updater_total_update(
    OimoManifoldUpdater* updater,
    const OimoDetectorResult* result,
    const OimoTransform* tf1,
    const OimoTransform* tf2
) {
    oimo_manifold_updater_save_old_data(updater);

    OimoManifold* m = updater->_manifold;
    int num = result->num_points;
    m->_numPoints = num;

    for (int i = 0; i < num; i++) {
        OimoManifoldPoint* p = &m->_points[i];
        oimo_manifold_point_initialize(p, &result->points[i], tf1, tf2);
        oimo_manifold_updater_update_by_id(updater, p);
    }
}

// Incremental update - 1:1 from ManifoldUpdater.incrementalUpdate
static inline void oimo_manifold_updater_incremental_update(
    OimoManifoldUpdater* updater,
    const OimoDetectorResult* result,
    const OimoTransform* tf1,
    const OimoTransform* tf2
) {
    OimoManifold* m = updater->_manifold;

    // Update old data
    oimo_manifold_update_depths_and_positions(m, tf1, tf2);

    // Set warm started flag
    for (int i = 0; i < m->_numPoints; i++) {
        m->_points[i]._warmStarted = true;
    }

    // Remove outdated points
    oimo_manifold_updater_remove_outdated_points(updater);

    // Add new points
    for (int i = 0; i < result->num_points; i++) {
        const OimoDetectorResultPoint* newPoint = &result->points[i];
        int idx = oimo_manifold_updater_find_nearest_index(updater, newPoint, tf1, tf2);

        if (idx == -1) {
            oimo_manifold_updater_add_point(updater, newPoint, tf1, tf2);
        } else {
            oimo_manifold_point_update_depth_and_positions(&m->_points[idx], newPoint, tf1, tf2);
        }
    }
}

#endif // OIMO_DYNAMICS_CONSTRAINT_CONTACT_MANIFOLD_UPDATER_H
