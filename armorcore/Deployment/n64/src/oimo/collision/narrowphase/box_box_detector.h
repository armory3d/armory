/**
 * Oimo Physics - N64 Port
 * Box vs Box Detector - SAT with Face Clipping
 *
 * Based on OimoPhysics by saharan
 * https://github.com/saharan/OimoPhysics
 *
 * This is the most complex collision detector. It uses:
 * - Separating Axis Theorem (SAT) with 15 potential axes
 *   (6 face normals + 9 edge cross products)
 * - Face clipping for contact manifold generation
 * - Edge-edge contact handling
 */

#ifndef OIMO_COLLISION_NARROWPHASE_BOX_BOX_DETECTOR_H
#define OIMO_COLLISION_NARROWPHASE_BOX_BOX_DETECTOR_H

#include "detector.h"
#include "detector_result.h"
#include "../geometry/box_geometry.h"
#include "../../common/transform.h"
#include "../../common/math_util.h"
#include "../../common/mat3.h"
#include "../../common/setting.h"

#ifdef __cplusplus
extern "C" {
#endif

// Edge axis bias multiplier for preferring face contacts
#define OIMO_BOX_BOX_EDGE_BIAS_MULT 1.0f

/**
 * Incident vertex - used during face clipping.
 */
typedef struct OimoIncidentVertex {
    OimoScalar x, y;      // Projected 2D coordinates on reference face
    OimoScalar wx, wy, wz; // World coordinates (relative to c1)
} OimoIncidentVertex;

/**
 * Face clipper - clips incident face against reference face.
 */
typedef struct OimoFaceClipper {
    OimoScalar w, h;  // Reference face half-dimensions
    int num_vertices;
    OimoIncidentVertex vertices[8];
    int num_tmp_vertices;
    OimoIncidentVertex tmp_vertices[8];
} OimoFaceClipper;

/**
 * Box vs Box collision detector.
 */
typedef struct OimoBoxBoxDetector {
    OimoDetector base;
    OimoFaceClipper clipper;
} OimoBoxBoxDetector;

// ==================== Incident Vertex Functions ====================

static inline void oimo_incident_vertex_init(OimoIncidentVertex* v,
    OimoScalar x, OimoScalar y, OimoScalar wx, OimoScalar wy, OimoScalar wz)
{
    v->x = x;
    v->y = y;
    v->wx = wx;
    v->wy = wy;
    v->wz = wz;
}

static inline void oimo_incident_vertex_copy(OimoIncidentVertex* dst, const OimoIncidentVertex* src) {
    dst->x = src->x;
    dst->y = src->y;
    dst->wx = src->wx;
    dst->wy = src->wy;
    dst->wz = src->wz;
}

static inline void oimo_incident_vertex_interp(OimoIncidentVertex* out,
    const OimoIncidentVertex* v1, const OimoIncidentVertex* v2, OimoScalar t)
{
    out->x = v1->x + (v2->x - v1->x) * t;
    out->y = v1->y + (v2->y - v1->y) * t;
    out->wx = v1->wx + (v2->wx - v1->wx) * t;
    out->wy = v1->wy + (v2->wy - v1->wy) * t;
    out->wz = v1->wz + (v2->wz - v1->wz) * t;
}

// ==================== Face Clipper Functions ====================

static inline void oimo_face_clipper_init(OimoFaceClipper* clipper, OimoScalar w, OimoScalar h) {
    clipper->w = w;
    clipper->h = h;
    clipper->num_vertices = 0;
    clipper->num_tmp_vertices = 0;
}

static inline void oimo_face_clipper_add_vertex(OimoFaceClipper* clipper,
    OimoScalar x, OimoScalar y, OimoScalar wx, OimoScalar wy, OimoScalar wz)
{
    oimo_incident_vertex_init(&clipper->vertices[clipper->num_vertices++], x, y, wx, wy, wz);
}

static inline void oimo_face_clipper_flip(OimoFaceClipper* clipper) {
    // Swap vertices and tmp_vertices
    OimoIncidentVertex temp[8];
    for (int i = 0; i < 8; i++) {
        oimo_incident_vertex_copy(&temp[i], &clipper->vertices[i]);
        oimo_incident_vertex_copy(&clipper->vertices[i], &clipper->tmp_vertices[i]);
        oimo_incident_vertex_copy(&clipper->tmp_vertices[i], &temp[i]);
    }
    clipper->num_vertices = clipper->num_tmp_vertices;
    clipper->num_tmp_vertices = 0;
}

static inline void oimo_face_clipper_add_tmp(OimoFaceClipper* clipper, const OimoIncidentVertex* v) {
    oimo_incident_vertex_copy(&clipper->tmp_vertices[clipper->num_tmp_vertices++], v);
}

static inline void oimo_face_clipper_interp_tmp(OimoFaceClipper* clipper,
    const OimoIncidentVertex* v1, const OimoIncidentVertex* v2, OimoScalar t)
{
    oimo_incident_vertex_interp(&clipper->tmp_vertices[clipper->num_tmp_vertices++], v1, v2, t);
}

static inline void oimo_face_clipper_clip_with_param(OimoFaceClipper* clipper,
    const OimoIncidentVertex* v1, const OimoIncidentVertex* v2,
    OimoScalar s1, OimoScalar s2)
{
    if (s1 > 0 && s2 > 0) {
        oimo_face_clipper_add_tmp(clipper, v1);
    } else if (s1 > 0 && s2 <= 0) {
        // v2 is clipped
        oimo_face_clipper_add_tmp(clipper, v1);
        oimo_face_clipper_interp_tmp(clipper, v1, v2, s1 / (s1 - s2));
    } else if (s1 <= 0 && s2 > 0) {
        // v1 is clipped
        oimo_face_clipper_interp_tmp(clipper, v1, v2, s1 / (s1 - s2));
    }
    // else: both outside, skip
}

static inline void oimo_face_clipper_clip_l(OimoFaceClipper* clipper) {
    for (int i = 0; i < clipper->num_vertices; i++) {
        OimoIncidentVertex* v1 = &clipper->vertices[i];
        OimoIncidentVertex* v2 = &clipper->vertices[(i + 1) % clipper->num_vertices];
        OimoScalar s1 = clipper->w + v1->x;
        OimoScalar s2 = clipper->w + v2->x;
        oimo_face_clipper_clip_with_param(clipper, v1, v2, s1, s2);
    }
}

static inline void oimo_face_clipper_clip_r(OimoFaceClipper* clipper) {
    for (int i = 0; i < clipper->num_vertices; i++) {
        OimoIncidentVertex* v1 = &clipper->vertices[i];
        OimoIncidentVertex* v2 = &clipper->vertices[(i + 1) % clipper->num_vertices];
        OimoScalar s1 = clipper->w - v1->x;
        OimoScalar s2 = clipper->w - v2->x;
        oimo_face_clipper_clip_with_param(clipper, v1, v2, s1, s2);
    }
}

static inline void oimo_face_clipper_clip_t(OimoFaceClipper* clipper) {
    for (int i = 0; i < clipper->num_vertices; i++) {
        OimoIncidentVertex* v1 = &clipper->vertices[i];
        OimoIncidentVertex* v2 = &clipper->vertices[(i + 1) % clipper->num_vertices];
        OimoScalar s1 = clipper->h + v1->y;
        OimoScalar s2 = clipper->h + v2->y;
        oimo_face_clipper_clip_with_param(clipper, v1, v2, s1, s2);
    }
}

static inline void oimo_face_clipper_clip_b(OimoFaceClipper* clipper) {
    for (int i = 0; i < clipper->num_vertices; i++) {
        OimoIncidentVertex* v1 = &clipper->vertices[i];
        OimoIncidentVertex* v2 = &clipper->vertices[(i + 1) % clipper->num_vertices];
        OimoScalar s1 = clipper->h - v1->y;
        OimoScalar s2 = clipper->h - v2->y;
        oimo_face_clipper_clip_with_param(clipper, v1, v2, s1, s2);
    }
}

static inline void oimo_face_clipper_clip(OimoFaceClipper* clipper) {
    oimo_face_clipper_clip_l(clipper);
    oimo_face_clipper_flip(clipper);
    oimo_face_clipper_clip_r(clipper);
    oimo_face_clipper_flip(clipper);
    oimo_face_clipper_clip_t(clipper);
    oimo_face_clipper_flip(clipper);
    oimo_face_clipper_clip_b(clipper);
    oimo_face_clipper_flip(clipper);
}

/**
 * Reduce vertices to 4 or fewer for manifold.
 */
static inline void oimo_face_clipper_reduce(OimoFaceClipper* clipper) {
    if (clipper->num_vertices <= 4) {
        return;
    }

    // Find 4 extreme points along diagonal directions
    OimoScalar e1x = 1.0f;
    OimoScalar e1y = 1.0f;
    OimoScalar e2x = -1.0f;
    OimoScalar e2y = 1.0f;

    OimoScalar max1 = -1e30f;
    OimoScalar min1 = 1e30f;
    OimoScalar max2 = -1e30f;
    OimoScalar min2 = 1e30f;

    int max1_idx = 0, min1_idx = 0, max2_idx = 0, min2_idx = 0;

    for (int i = 0; i < clipper->num_vertices; i++) {
        OimoIncidentVertex* v = &clipper->vertices[i];
        OimoScalar dot1 = v->x * e1x + v->y * e1y;
        OimoScalar dot2 = v->x * e2x + v->y * e2y;

        if (i == 0) {
            max1 = dot1; max1_idx = i;
            min1 = dot1; min1_idx = i;
            max2 = dot2; max2_idx = i;
            min2 = dot2; min2_idx = i;
        } else {
            if (dot1 > max1) { max1 = dot1; max1_idx = i; }
            if (dot1 < min1) { min1 = dot1; min1_idx = i; }
            if (dot2 > max2) { max2 = dot2; max2_idx = i; }
            if (dot2 < min2) { min2 = dot2; min2_idx = i; }
        }
    }

    // Copy selected vertices
    oimo_incident_vertex_copy(&clipper->tmp_vertices[0], &clipper->vertices[max1_idx]);
    oimo_incident_vertex_copy(&clipper->tmp_vertices[1], &clipper->vertices[max2_idx]);
    oimo_incident_vertex_copy(&clipper->tmp_vertices[2], &clipper->vertices[min1_idx]);
    oimo_incident_vertex_copy(&clipper->tmp_vertices[3], &clipper->vertices[min2_idx]);
    clipper->num_tmp_vertices = 4;

    oimo_face_clipper_flip(clipper);
}

// ==================== Helper Functions ====================

/**
 * Project box onto axis (returns half the projected extent).
 */
static inline OimoScalar oimo_box_box_project(const OimoVec3* axis,
    const OimoVec3* sx, const OimoVec3* sy, const OimoVec3* sz)
{
    OimoScalar dx = oimo_abs(oimo_vec3_dot(axis, sx));
    OimoScalar dy = oimo_abs(oimo_vec3_dot(axis, sy));
    OimoScalar dz = oimo_abs(oimo_vec3_dot(axis, sz));
    return dx + dy + dz;
}

/**
 * 2D version of project (for edge axes).
 */
static inline OimoScalar oimo_box_box_project2(const OimoVec3* axis,
    const OimoVec3* sx, const OimoVec3* sy)
{
    OimoScalar dx = oimo_abs(oimo_vec3_dot(axis, sx));
    OimoScalar dy = oimo_abs(oimo_vec3_dot(axis, sy));
    return dx + dy;
}

/**
 * SAT check - checks if axis is separating and updates minimum.
 * Returns true if separated (should early exit).
 */
static inline bool oimo_sat_check(
    OimoScalar* min_depth, int* min_id, int* min_sign, OimoVec3* min_axis,
    OimoScalar proj1, OimoScalar proj2, OimoScalar proj_c12,
    const OimoVec3* axis, int id, OimoScalar bias_mult)
{
    OimoScalar sum = proj1 + proj2;
    bool neg = proj_c12 < 0.0f;
    OimoScalar abs_proj = neg ? -proj_c12 : proj_c12;

    if (abs_proj >= sum) {
        return true;  // Separated
    }

    OimoScalar depth = sum - abs_proj;
    if (depth * bias_mult < *min_depth) {
        *min_depth = depth * bias_mult;
        *min_id = id;
        *min_axis = *axis;
        *min_sign = neg ? -1 : 1;
    }

    return false;
}

/**
 * Supporting vertex for rectangle (2D supporting point).
 */
static inline void oimo_supporting_vertex_rect(OimoVec3* out,
    const OimoVec3* half_ext_x, const OimoVec3* half_ext_y, const OimoVec3* axis)
{
    bool sign_x = oimo_vec3_dot(half_ext_x, axis) > 0.0f;
    bool sign_y = oimo_vec3_dot(half_ext_y, axis) > 0.0f;

    if (sign_x) {
        if (sign_y) {
            oimo_vec3_add_to(out, half_ext_x, half_ext_y);
        } else {
            oimo_vec3_sub_to(out, half_ext_x, half_ext_y);
        }
    } else {
        if (sign_y) {
            oimo_vec3_sub_to(out, half_ext_y, half_ext_x);
        } else {
            oimo_vec3_add_to(out, half_ext_x, half_ext_y);
            oimo_vec3_negate_to(out, out);
        }
    }
}

/**
 * Get box face vertices given the face ID.
 * Vertices are ordered CCW when viewed from outside.
 *
 * OimoPhysics getBoxFace macro signs:
 * x+: (1,1,1), (1,-1,1), (1,-1,-1), (1,1,-1)
 * x-: (-1,1,1), (-1,1,-1), (-1,-1,-1), (-1,-1,1)
 * y+: (1,1,1), (1,1,-1), (-1,1,-1), (-1,1,1)
 * y-: (1,-1,1), (-1,-1,1), (-1,-1,-1), (1,-1,-1)
 * z+: (1,1,1), (-1,1,1), (-1,-1,1), (1,-1,1)
 * z-: (1,1,-1), (1,-1,-1), (-1,-1,-1), (-1,1,-1)
 */
static inline void oimo_get_box_face(
    OimoVec3* v1, OimoVec3* v2, OimoVec3* v3, OimoVec3* v4,
    const OimoVec3* sx, const OimoVec3* sy, const OimoVec3* sz, int face_id)
{
    OimoVec3 tmp, tmp2;
    switch (face_id) {
        case 0: // x+: (1,1,1), (1,-1,1), (1,-1,-1), (1,1,-1)
            // v1 = sx + sy + sz
            oimo_vec3_add_to(&tmp, sx, sy); oimo_vec3_add_to(v1, &tmp, sz);
            // v2 = sx - sy + sz
            oimo_vec3_sub_to(&tmp, sx, sy); oimo_vec3_add_to(v2, &tmp, sz);
            // v3 = sx - sy - sz
            oimo_vec3_sub_to(&tmp, sx, sy); oimo_vec3_sub_to(v3, &tmp, sz);
            // v4 = sx + sy - sz
            oimo_vec3_add_to(&tmp, sx, sy); oimo_vec3_sub_to(v4, &tmp, sz);
            break;
        case 1: // x-: (-1,1,1), (-1,1,-1), (-1,-1,-1), (-1,-1,1)
            // v1 = -sx + sy + sz
            oimo_vec3_sub_to(&tmp, sy, sx); oimo_vec3_add_to(v1, &tmp, sz);
            // v2 = -sx + sy - sz
            oimo_vec3_sub_to(&tmp, sy, sx); oimo_vec3_sub_to(v2, &tmp, sz);
            // v3 = -sx - sy - sz
            oimo_vec3_add_to(&tmp, sx, sy); oimo_vec3_negate_to(&tmp, &tmp); oimo_vec3_sub_to(v3, &tmp, sz);
            // v4 = -sx - sy + sz
            oimo_vec3_add_to(&tmp, sx, sy); oimo_vec3_negate_to(&tmp, &tmp); oimo_vec3_add_to(v4, &tmp, sz);
            break;
        case 2: // y+: (1,1,1), (1,1,-1), (-1,1,-1), (-1,1,1)
            // v1 = sx + sy + sz
            oimo_vec3_add_to(&tmp, sx, sy); oimo_vec3_add_to(v1, &tmp, sz);
            // v2 = sx + sy - sz
            oimo_vec3_add_to(&tmp, sx, sy); oimo_vec3_sub_to(v2, &tmp, sz);
            // v3 = -sx + sy - sz
            oimo_vec3_sub_to(&tmp, sy, sx); oimo_vec3_sub_to(v3, &tmp, sz);
            // v4 = -sx + sy + sz
            oimo_vec3_sub_to(&tmp, sy, sx); oimo_vec3_add_to(v4, &tmp, sz);
            break;
        case 3: // y-: (1,-1,1), (-1,-1,1), (-1,-1,-1), (1,-1,-1)
            // v1 = sx - sy + sz
            oimo_vec3_sub_to(&tmp, sx, sy); oimo_vec3_add_to(v1, &tmp, sz);
            // v2 = -sx - sy + sz
            oimo_vec3_add_to(&tmp, sx, sy); oimo_vec3_negate_to(&tmp, &tmp); oimo_vec3_add_to(v2, &tmp, sz);
            // v3 = -sx - sy - sz
            oimo_vec3_add_to(&tmp, sx, sy); oimo_vec3_negate_to(&tmp, &tmp); oimo_vec3_sub_to(v3, &tmp, sz);
            // v4 = sx - sy - sz
            oimo_vec3_sub_to(&tmp, sx, sy); oimo_vec3_sub_to(v4, &tmp, sz);
            break;
        case 4: // z+: (1,1,1), (-1,1,1), (-1,-1,1), (1,-1,1)
            // v1 = sx + sy + sz
            oimo_vec3_add_to(&tmp, sx, sy); oimo_vec3_add_to(v1, &tmp, sz);
            // v2 = -sx + sy + sz
            oimo_vec3_sub_to(&tmp, sy, sx); oimo_vec3_add_to(v2, &tmp, sz);
            // v3 = -sx - sy + sz
            oimo_vec3_add_to(&tmp, sx, sy); oimo_vec3_negate_to(&tmp, &tmp); oimo_vec3_add_to(v3, &tmp, sz);
            // v4 = sx - sy + sz
            oimo_vec3_sub_to(&tmp, sx, sy); oimo_vec3_add_to(v4, &tmp, sz);
            break;
        default: // z- (case 5): (1,1,-1), (1,-1,-1), (-1,-1,-1), (-1,1,-1)
            // v1 = sx + sy - sz
            oimo_vec3_add_to(&tmp, sx, sy); oimo_vec3_sub_to(v1, &tmp, sz);
            // v2 = sx - sy - sz
            oimo_vec3_sub_to(&tmp, sx, sy); oimo_vec3_sub_to(v2, &tmp, sz);
            // v3 = -sx - sy - sz
            oimo_vec3_add_to(&tmp, sx, sy); oimo_vec3_negate_to(&tmp, &tmp); oimo_vec3_sub_to(v3, &tmp, sz);
            // v4 = -sx + sy - sz
            oimo_vec3_sub_to(&tmp, sy, sx); oimo_vec3_sub_to(v4, &tmp, sz);
            break;
    }
}

// ==================== Main Detector ====================

/**
 * Initialize the box-box detector.
 */
static inline void oimo_box_box_detector_init(OimoBoxBoxDetector* detector) {
    oimo_detector_init(&detector->base, OIMO_DETECTOR_BOX_BOX, false);
}

/**
 * Detect collision between two boxes using SAT and face clipping.
 */
static inline void oimo_box_box_detector_detect(
    OimoBoxBoxDetector* detector,
    OimoDetectorResult* result,
    const OimoBoxGeometry* box1,
    const OimoBoxGeometry* box2,
    const OimoTransform* tf1,
    const OimoTransform* tf2)
{
    result->incremental = false;

    // Centers
    OimoVec3 c1 = tf1->position;
    OimoVec3 c2 = tf2->position;
    OimoVec3 c12;
    oimo_vec3_sub_to(&c12, &c2, &c1);

    // Basis vectors from rotation matrices
    OimoVec3 x1 = oimo_mat3_get_col(&tf1->rotation, 0);
    OimoVec3 y1 = oimo_mat3_get_col(&tf1->rotation, 1);
    OimoVec3 z1 = oimo_mat3_get_col(&tf1->rotation, 2);
    OimoVec3 x2 = oimo_mat3_get_col(&tf2->rotation, 0);
    OimoVec3 y2 = oimo_mat3_get_col(&tf2->rotation, 1);
    OimoVec3 z2 = oimo_mat3_get_col(&tf2->rotation, 2);

    // Half extents
    OimoScalar w1 = box1->half_extents.x;
    OimoScalar h1 = box1->half_extents.y;
    OimoScalar d1 = box1->half_extents.z;
    OimoScalar w2 = box2->half_extents.x;
    OimoScalar h2 = box2->half_extents.y;
    OimoScalar d2 = box2->half_extents.z;

    // Scaled basis vectors
    OimoVec3 sx1, sy1, sz1, sx2, sy2, sz2;
    oimo_vec3_scale_to(&sx1, &x1, w1);
    oimo_vec3_scale_to(&sy1, &y1, h1);
    oimo_vec3_scale_to(&sz1, &z1, d1);
    oimo_vec3_scale_to(&sx2, &x2, w2);
    oimo_vec3_scale_to(&sy2, &y2, h2);
    oimo_vec3_scale_to(&sz2, &z2, d2);

    // SAT variables
    OimoScalar proj1, proj2, proj_c12;
    OimoScalar min_depth = 1e30f;
    int min_id = -1;
    int min_sign = 0;
    OimoVec3 min_axis;
    oimo_vec3_set(&min_axis, 0.0f, 0.0f, 0.0f);

    // ===================== 6 Face Axes =====================

    // Axis = x1
    proj1 = w1;
    proj2 = oimo_box_box_project(&x1, &sx2, &sy2, &sz2);
    proj_c12 = oimo_vec3_dot(&x1, &c12);
    if (oimo_sat_check(&min_depth, &min_id, &min_sign, &min_axis, proj1, proj2, proj_c12, &x1, 0, 1.0f)) return;

    // Axis = y1
    proj1 = h1;
    proj2 = oimo_box_box_project(&y1, &sx2, &sy2, &sz2);
    proj_c12 = oimo_vec3_dot(&y1, &c12);
    if (oimo_sat_check(&min_depth, &min_id, &min_sign, &min_axis, proj1, proj2, proj_c12, &y1, 1, 1.0f)) return;

    // Axis = z1
    proj1 = d1;
    proj2 = oimo_box_box_project(&z1, &sx2, &sy2, &sz2);
    proj_c12 = oimo_vec3_dot(&z1, &c12);
    if (oimo_sat_check(&min_depth, &min_id, &min_sign, &min_axis, proj1, proj2, proj_c12, &z1, 2, 1.0f)) return;

    // Apply bias to prefer face contacts over edge contacts
    if (min_depth > OIMO_LINEAR_SLOP) {
        min_depth -= OIMO_LINEAR_SLOP;
    } else {
        min_depth = 0.0f;
    }

    // Axis = x2
    proj1 = oimo_box_box_project(&x2, &sx1, &sy1, &sz1);
    proj2 = w2;
    proj_c12 = oimo_vec3_dot(&x2, &c12);
    if (oimo_sat_check(&min_depth, &min_id, &min_sign, &min_axis, proj1, proj2, proj_c12, &x2, 3, 1.0f)) return;

    // Axis = y2
    proj1 = oimo_box_box_project(&y2, &sx1, &sy1, &sz1);
    proj2 = h2;
    proj_c12 = oimo_vec3_dot(&y2, &c12);
    if (oimo_sat_check(&min_depth, &min_id, &min_sign, &min_axis, proj1, proj2, proj_c12, &y2, 4, 1.0f)) return;

    // Axis = z2
    proj1 = oimo_box_box_project(&z2, &sx1, &sy1, &sz1);
    proj2 = d2;
    proj_c12 = oimo_vec3_dot(&z2, &c12);
    if (oimo_sat_check(&min_depth, &min_id, &min_sign, &min_axis, proj1, proj2, proj_c12, &z2, 5, 1.0f)) return;

    // Apply bias again before edge checks
    if (min_depth > OIMO_LINEAR_SLOP) {
        min_depth -= OIMO_LINEAR_SLOP;
    } else {
        min_depth = 0.0f;
    }

    // ===================== 9 Edge Axes =====================

    OimoVec3 edge_axis;

    // cross(x1, x2)
    oimo_vec3_cross_to(&edge_axis, &x1, &x2);
    if (!oimo_vec3_is_zero(&edge_axis, OIMO_EPSILON)) {
        oimo_vec3_normalize_to(&edge_axis, &edge_axis);
        proj1 = oimo_box_box_project2(&edge_axis, &sy1, &sz1);
        proj2 = oimo_box_box_project2(&edge_axis, &sy2, &sz2);
        proj_c12 = oimo_vec3_dot(&edge_axis, &c12);
        if (oimo_sat_check(&min_depth, &min_id, &min_sign, &min_axis, proj1, proj2, proj_c12, &edge_axis, 6, OIMO_BOX_BOX_EDGE_BIAS_MULT)) return;
    }

    // cross(x1, y2)
    oimo_vec3_cross_to(&edge_axis, &x1, &y2);
    if (!oimo_vec3_is_zero(&edge_axis, OIMO_EPSILON)) {
        oimo_vec3_normalize_to(&edge_axis, &edge_axis);
        proj1 = oimo_box_box_project2(&edge_axis, &sy1, &sz1);
        proj2 = oimo_box_box_project2(&edge_axis, &sx2, &sz2);
        proj_c12 = oimo_vec3_dot(&edge_axis, &c12);
        if (oimo_sat_check(&min_depth, &min_id, &min_sign, &min_axis, proj1, proj2, proj_c12, &edge_axis, 7, OIMO_BOX_BOX_EDGE_BIAS_MULT)) return;
    }

    // cross(x1, z2)
    oimo_vec3_cross_to(&edge_axis, &x1, &z2);
    if (!oimo_vec3_is_zero(&edge_axis, OIMO_EPSILON)) {
        oimo_vec3_normalize_to(&edge_axis, &edge_axis);
        proj1 = oimo_box_box_project2(&edge_axis, &sy1, &sz1);
        proj2 = oimo_box_box_project2(&edge_axis, &sx2, &sy2);
        proj_c12 = oimo_vec3_dot(&edge_axis, &c12);
        if (oimo_sat_check(&min_depth, &min_id, &min_sign, &min_axis, proj1, proj2, proj_c12, &edge_axis, 8, OIMO_BOX_BOX_EDGE_BIAS_MULT)) return;
    }

    // cross(y1, x2)
    oimo_vec3_cross_to(&edge_axis, &y1, &x2);
    if (!oimo_vec3_is_zero(&edge_axis, OIMO_EPSILON)) {
        oimo_vec3_normalize_to(&edge_axis, &edge_axis);
        proj1 = oimo_box_box_project2(&edge_axis, &sx1, &sz1);
        proj2 = oimo_box_box_project2(&edge_axis, &sy2, &sz2);
        proj_c12 = oimo_vec3_dot(&edge_axis, &c12);
        if (oimo_sat_check(&min_depth, &min_id, &min_sign, &min_axis, proj1, proj2, proj_c12, &edge_axis, 9, OIMO_BOX_BOX_EDGE_BIAS_MULT)) return;
    }

    // cross(y1, y2)
    oimo_vec3_cross_to(&edge_axis, &y1, &y2);
    if (!oimo_vec3_is_zero(&edge_axis, OIMO_EPSILON)) {
        oimo_vec3_normalize_to(&edge_axis, &edge_axis);
        proj1 = oimo_box_box_project2(&edge_axis, &sx1, &sz1);
        proj2 = oimo_box_box_project2(&edge_axis, &sx2, &sz2);
        proj_c12 = oimo_vec3_dot(&edge_axis, &c12);
        if (oimo_sat_check(&min_depth, &min_id, &min_sign, &min_axis, proj1, proj2, proj_c12, &edge_axis, 10, OIMO_BOX_BOX_EDGE_BIAS_MULT)) return;
    }

    // cross(y1, z2)
    oimo_vec3_cross_to(&edge_axis, &y1, &z2);
    if (!oimo_vec3_is_zero(&edge_axis, OIMO_EPSILON)) {
        oimo_vec3_normalize_to(&edge_axis, &edge_axis);
        proj1 = oimo_box_box_project2(&edge_axis, &sx1, &sz1);
        proj2 = oimo_box_box_project2(&edge_axis, &sx2, &sy2);
        proj_c12 = oimo_vec3_dot(&edge_axis, &c12);
        if (oimo_sat_check(&min_depth, &min_id, &min_sign, &min_axis, proj1, proj2, proj_c12, &edge_axis, 11, OIMO_BOX_BOX_EDGE_BIAS_MULT)) return;
    }

    // cross(z1, x2)
    oimo_vec3_cross_to(&edge_axis, &z1, &x2);
    if (!oimo_vec3_is_zero(&edge_axis, OIMO_EPSILON)) {
        oimo_vec3_normalize_to(&edge_axis, &edge_axis);
        proj1 = oimo_box_box_project2(&edge_axis, &sx1, &sy1);
        proj2 = oimo_box_box_project2(&edge_axis, &sy2, &sz2);
        proj_c12 = oimo_vec3_dot(&edge_axis, &c12);
        if (oimo_sat_check(&min_depth, &min_id, &min_sign, &min_axis, proj1, proj2, proj_c12, &edge_axis, 12, OIMO_BOX_BOX_EDGE_BIAS_MULT)) return;
    }

    // cross(z1, y2)
    oimo_vec3_cross_to(&edge_axis, &z1, &y2);
    if (!oimo_vec3_is_zero(&edge_axis, OIMO_EPSILON)) {
        oimo_vec3_normalize_to(&edge_axis, &edge_axis);
        proj1 = oimo_box_box_project2(&edge_axis, &sx1, &sy1);
        proj2 = oimo_box_box_project2(&edge_axis, &sx2, &sz2);
        proj_c12 = oimo_vec3_dot(&edge_axis, &c12);
        if (oimo_sat_check(&min_depth, &min_id, &min_sign, &min_axis, proj1, proj2, proj_c12, &edge_axis, 13, OIMO_BOX_BOX_EDGE_BIAS_MULT)) return;
    }

    // cross(z1, z2)
    oimo_vec3_cross_to(&edge_axis, &z1, &z2);
    if (!oimo_vec3_is_zero(&edge_axis, OIMO_EPSILON)) {
        oimo_vec3_normalize_to(&edge_axis, &edge_axis);
        proj1 = oimo_box_box_project2(&edge_axis, &sx1, &sy1);
        proj2 = oimo_box_box_project2(&edge_axis, &sx2, &sy2);
        proj_c12 = oimo_vec3_dot(&edge_axis, &c12);
        if (oimo_sat_check(&min_depth, &min_id, &min_sign, &min_axis, proj1, proj2, proj_c12, &edge_axis, 14, OIMO_BOX_BOX_EDGE_BIAS_MULT)) return;
    }

    // ===================== Edge-Edge Contact =====================

    if (min_id >= 6) {
        // Flip axis to point from box1 to box2
        oimo_vec3_scale_to(&min_axis, &min_axis, (OimoScalar)min_sign);

        // Direction indices
        int id1 = (min_id - 6) / 3;  // 0=x, 1=y, 2=z
        int id2 = (min_id - 6) % 3;

        OimoVec3 p1, p2;  // Points on edges
        OimoVec3 d1_dir, d2_dir;  // Edge directions

        // Select edge on box1
        switch (id1) {
            case 0:
                d1_dir = x1;
                oimo_supporting_vertex_rect(&p1, &sy1, &sz1, &min_axis);
                break;
            case 1:
                d1_dir = y1;
                oimo_supporting_vertex_rect(&p1, &sx1, &sz1, &min_axis);
                break;
            default:
                d1_dir = z1;
                oimo_supporting_vertex_rect(&p1, &sx1, &sy1, &min_axis);
                break;
        }
        oimo_vec3_add_to(&p1, &c1, &p1);

        // Select edge on box2
        switch (id2) {
            case 0:
                d2_dir = x2;
                oimo_supporting_vertex_rect(&p2, &sy2, &sz2, &min_axis);
                break;
            case 1:
                d2_dir = y2;
                oimo_supporting_vertex_rect(&p2, &sx2, &sz2, &min_axis);
                break;
            default:
                d2_dir = z2;
                oimo_supporting_vertex_rect(&p2, &sx2, &sy2, &min_axis);
                break;
        }
        oimo_vec3_sub_to(&p2, &c2, &p2);

        // Compute closest points on the two edges
        OimoVec3 r;
        oimo_vec3_sub_to(&r, &p1, &p2);

        OimoScalar dot12 = oimo_vec3_dot(&d1_dir, &d2_dir);
        OimoScalar dot1r = oimo_vec3_dot(&d1_dir, &r);
        OimoScalar dot2r = oimo_vec3_dot(&d2_dir, &r);

        OimoScalar inv_det = 1.0f / (1.0f - dot12 * dot12);
        OimoScalar t1 = (dot12 * dot2r - dot1r) * inv_det;
        OimoScalar t2 = (dot2r - dot12 * dot1r) * inv_det;

        OimoVec3 cp1, cp2;
        OimoVec3 scaled;
        oimo_vec3_scale_to(&scaled, &d1_dir, t1);
        oimo_vec3_add_to(&cp1, &p1, &scaled);
        oimo_vec3_scale_to(&scaled, &d2_dir, t2);
        oimo_vec3_add_to(&cp2, &p2, &scaled);

        // Normal points from box2 to box1
        OimoVec3 normal;
        oimo_vec3_negate_to(&normal, &min_axis);

        oimo_detector_set_normal(&detector->base, result, &normal);
        oimo_detector_add_point(&detector->base, result, &cp1, &cp2, min_depth, 4);
        return;
    }

    // ===================== Face-Face Contact =====================

    bool swapped = false;

    // If collision is with box2's face, swap boxes
    if (min_id >= 3) {
        min_sign = -min_sign;
        oimo_vec3_negate_to(&c12, &c12);

        // Swap all box1 and box2 data
        OimoVec3 tmp_v;
        OimoScalar tmp_s;

        #define SWAP_VEC(a, b) tmp_v = a; a = b; b = tmp_v
        #define SWAP_SCALAR(a, b) tmp_s = a; a = b; b = tmp_s

        SWAP_VEC(c1, c2);
        SWAP_VEC(x1, x2);
        SWAP_VEC(y1, y2);
        SWAP_VEC(z1, z2);
        SWAP_VEC(sx1, sx2);
        SWAP_VEC(sy1, sy2);
        SWAP_VEC(sz1, sz2);
        SWAP_SCALAR(w1, w2);
        SWAP_SCALAR(h1, h2);
        SWAP_SCALAR(d1, d2);

        #undef SWAP_VEC
        #undef SWAP_SCALAR

        min_id -= 3;
        swapped = true;
    }

    // Find reference face on box1
    OimoVec3 ref_center, ref_normal, ref_x, ref_y;
    OimoScalar ref_w, ref_h;

    switch (min_id) {
        case 0: // X face
            ref_center = sx1;
            ref_normal = x1;
            ref_x = y1;
            ref_y = z1;
            ref_w = h1;
            ref_h = d1;
            break;
        case 1: // Y face
            ref_center = sy1;
            ref_normal = y1;
            ref_x = z1;
            ref_y = x1;
            ref_w = d1;
            ref_h = w1;
            break;
        default: // Z face
            ref_center = sz1;
            ref_normal = z1;
            ref_x = x1;
            ref_y = y1;
            ref_w = w1;
            ref_h = h1;
            break;
    }

    if (min_sign < 0) {
        oimo_vec3_negate_to(&ref_center, &ref_center);
        oimo_vec3_negate_to(&ref_normal, &ref_normal);
        // Swap ref_x and ref_y, and their dimensions
        OimoVec3 tmp_v = ref_x;
        ref_x = ref_y;
        ref_y = tmp_v;
        OimoScalar tmp_s = ref_w;
        ref_w = ref_h;
        ref_h = tmp_s;
    }

    oimo_vec3_add_to(&ref_center, &ref_center, &c1);

    // Find incident face on box2
    OimoScalar min_inc_dot = 1.0f;
    int inc_id = 0;

    OimoScalar inc_dot;
    inc_dot = oimo_vec3_dot(&ref_normal, &x2);
    if (inc_dot < min_inc_dot) { min_inc_dot = inc_dot; inc_id = 0; }
    if (-inc_dot < min_inc_dot) { min_inc_dot = -inc_dot; inc_id = 1; }

    inc_dot = oimo_vec3_dot(&ref_normal, &y2);
    if (inc_dot < min_inc_dot) { min_inc_dot = inc_dot; inc_id = 2; }
    if (-inc_dot < min_inc_dot) { min_inc_dot = -inc_dot; inc_id = 3; }

    inc_dot = oimo_vec3_dot(&ref_normal, &z2);
    if (inc_dot < min_inc_dot) { min_inc_dot = inc_dot; inc_id = 4; }
    if (-inc_dot < min_inc_dot) { min_inc_dot = -inc_dot; inc_id = 5; }

    // Get incident face vertices
    OimoVec3 inc_v1, inc_v2, inc_v3, inc_v4;
    oimo_get_box_face(&inc_v1, &inc_v2, &inc_v3, &inc_v4, &sx2, &sy2, &sz2, inc_id);

    // Translate to reference frame (relative to c1)
    oimo_vec3_add_to(&inc_v1, &inc_v1, &c12);
    oimo_vec3_add_to(&inc_v2, &inc_v2, &c12);
    oimo_vec3_add_to(&inc_v3, &inc_v3, &c12);
    oimo_vec3_add_to(&inc_v4, &inc_v4, &c12);

    // Clip incident face against reference face
    oimo_face_clipper_init(&detector->clipper, ref_w, ref_h);
    oimo_face_clipper_add_vertex(&detector->clipper,
        oimo_vec3_dot(&inc_v1, &ref_x), oimo_vec3_dot(&inc_v1, &ref_y),
        inc_v1.x, inc_v1.y, inc_v1.z);
    oimo_face_clipper_add_vertex(&detector->clipper,
        oimo_vec3_dot(&inc_v2, &ref_x), oimo_vec3_dot(&inc_v2, &ref_y),
        inc_v2.x, inc_v2.y, inc_v2.z);
    oimo_face_clipper_add_vertex(&detector->clipper,
        oimo_vec3_dot(&inc_v3, &ref_x), oimo_vec3_dot(&inc_v3, &ref_y),
        inc_v3.x, inc_v3.y, inc_v3.z);
    oimo_face_clipper_add_vertex(&detector->clipper,
        oimo_vec3_dot(&inc_v4, &ref_x), oimo_vec3_dot(&inc_v4, &ref_y),
        inc_v4.x, inc_v4.y, inc_v4.z);

    oimo_face_clipper_clip(&detector->clipper);
    oimo_face_clipper_reduce(&detector->clipper);

    // Generate contact points
    OimoVec3 normal;
    if (swapped) {
        normal = ref_normal;
    } else {
        oimo_vec3_negate_to(&normal, &ref_normal);
    }
    oimo_detector_set_normal(&detector->base, result, &normal);

    for (int i = 0; i < detector->clipper.num_vertices; i++) {
        OimoIncidentVertex* v = &detector->clipper.vertices[i];

        OimoVec3 clipped_vertex;
        oimo_vec3_set(&clipped_vertex, v->wx, v->wy, v->wz);
        oimo_vec3_add_to(&clipped_vertex, &clipped_vertex, &c1);

        OimoVec3 clipped_to_ref;
        oimo_vec3_sub_to(&clipped_to_ref, &ref_center, &clipped_vertex);
        OimoScalar depth = oimo_vec3_dot(&clipped_to_ref, &ref_normal);

        OimoVec3 clipped_on_ref;
        OimoVec3 scaled;
        oimo_vec3_scale_to(&scaled, &ref_normal, depth);
        oimo_vec3_add_to(&clipped_on_ref, &clipped_vertex, &scaled);

        if (depth > -OIMO_CONTACT_PERSISTENCE_THRESHOLD) {
            if (swapped) {
                oimo_detector_add_point(&detector->base, result, &clipped_vertex, &clipped_on_ref, depth, i);
            } else {
                oimo_detector_add_point(&detector->base, result, &clipped_on_ref, &clipped_vertex, depth, i);
            }
        }
    }
}

#ifdef __cplusplus
}
#endif

#endif // OIMO_COLLISION_NARROWPHASE_BOX_BOX_DETECTOR_H


