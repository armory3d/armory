// manifold.h
// 1:1 port from OimoPhysics Manifold.hx
#ifndef OIMO_DYNAMICS_CONSTRAINT_CONTACT_MANIFOLD_H
#define OIMO_DYNAMICS_CONSTRAINT_CONTACT_MANIFOLD_H

#include "../../../common/vec3.h"
#include "../../../common/mat3.h"
#include "../../../common/transform.h"
#include "../../../common/setting.h"
#include "../../../common/math_util.h"
#include "manifold_point.h"

typedef struct OimoManifold {
    OimoVec3 _normal;
    OimoVec3 _tangent;
    OimoVec3 _binormal;
    int _numPoints;
    OimoManifoldPoint _points[OIMO_MAX_MANIFOLD_POINTS];
} OimoManifold;

static inline OimoManifold oimo_manifold_create(void) {
    OimoManifold m;
    m._normal = oimo_vec3_zero();
    m._tangent = oimo_vec3_zero();
    m._binormal = oimo_vec3_zero();
    m._numPoints = 0;
    for (int i = 0; i < OIMO_MAX_MANIFOLD_POINTS; i++) {
        m._points[i] = oimo_manifold_point_create();
    }
    return m;
}

static inline void oimo_manifold_clear(OimoManifold* m) {
    for (int i = 0; i < m->_numPoints; i++) {
        oimo_manifold_point_clear(&m->_points[i]);
    }
    m->_numPoints = 0;
}

// Build orthonormal basis from normal - 1:1 from Manifold._buildBasis
static inline void oimo_manifold_build_basis(OimoManifold* m, OimoVec3 normal) {
    m->_normal = normal;

    OimoScalar nx = normal.x;
    OimoScalar ny = normal.y;
    OimoScalar nz = normal.z;
    OimoScalar nx2 = nx * nx;
    OimoScalar ny2 = ny * ny;
    OimoScalar nz2 = nz * nz;

    OimoScalar tx, ty, tz;
    OimoScalar bx, by, bz;

    // compare3min: find smallest component squared
    if (nx2 <= ny2 && nx2 <= nz2) {
        // nx2 is smallest
        OimoScalar invL = 1.0f / oimo_sqrt(ny2 + nz2);
        tx = 0.0f;
        ty = -nz * invL;
        tz = ny * invL;
        bx = ny * tz - nz * ty;
        by = -nx * tz;
        bz = nx * ty;
    } else if (ny2 <= nx2 && ny2 <= nz2) {
        // ny2 is smallest
        OimoScalar invL = 1.0f / oimo_sqrt(nx2 + nz2);
        tx = nz * invL;
        ty = 0.0f;
        tz = -nx * invL;
        bx = ny * tz;
        by = nz * tx - nx * tz;
        bz = -ny * tx;
    } else {
        // nz2 is smallest
        OimoScalar invL = 1.0f / oimo_sqrt(nx2 + ny2);
        tx = -ny * invL;
        ty = nx * invL;
        tz = 0.0f;
        bx = -nz * ty;
        by = nz * tx;
        bz = nx * ty - ny * tx;
    }

    m->_tangent = oimo_vec3(tx, ty, tz);
    m->_binormal = oimo_vec3(bx, by, bz);
}

// Update depths and positions - 1:1 from Manifold._updateDepthsAndPositions
static inline void oimo_manifold_update_depths_and_positions(
    OimoManifold* m,
    const OimoTransform* tf1,
    const OimoTransform* tf2
) {
    for (int i = 0; i < m->_numPoints; i++) {
        OimoManifoldPoint* p = &m->_points[i];

        // relPos = R * localPos
        p->_relPos1 = oimo_mat3_mul_vec3(&tf1->rotation, p->_localPos1);
        p->_relPos2 = oimo_mat3_mul_vec3(&tf2->rotation, p->_localPos2);

        // pos = relPos + tf.position
        p->_pos1 = oimo_vec3_add(p->_relPos1, tf1->position);
        p->_pos2 = oimo_vec3_add(p->_relPos2, tf2->position);

        // Compute depth from difference along normal
        OimoVec3 diff = oimo_vec3_sub(p->_pos1, p->_pos2);
        OimoScalar dotN = oimo_vec3_dot(diff, m->_normal);
        p->_depth = -dotN;
    }
}

// Public getters
static inline OimoVec3 oimo_manifold_get_normal(const OimoManifold* m) {
    return m->_normal;
}

static inline OimoVec3 oimo_manifold_get_tangent(const OimoManifold* m) {
    return m->_tangent;
}

static inline OimoVec3 oimo_manifold_get_binormal(const OimoManifold* m) {
    return m->_binormal;
}

static inline int oimo_manifold_get_num_points(const OimoManifold* m) {
    return m->_numPoints;
}

static inline OimoManifoldPoint* oimo_manifold_get_points(OimoManifold* m) {
    return m->_points;
}

#endif // OIMO_DYNAMICS_CONSTRAINT_CONTACT_MANIFOLD_H
