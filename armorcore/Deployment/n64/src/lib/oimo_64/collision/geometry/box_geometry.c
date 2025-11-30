#include "box_geometry.h"

// =============================================================================
// Box Geometry Implementation
// =============================================================================

void box_get_half_extents(const Shape* shape, Vec3* out) {
    if (shape && shape->type == SHAPE_BOX) {
        *out = shape->geom.box.halfExtents;
    } else {
        *out = vec3_zero();
    }
}

void box_set_half_extents(Shape* shape, const Vec3* halfExtents) {
    if (shape && shape->type == SHAPE_BOX) {
        shape->geom.box.halfExtents = *halfExtents;
        if (shape->body) {
            shape_update_aabb(shape);
            rigidbody_update_mass(shape->body);
        }
    }
}

void box_set_half_extents3(Shape* shape, float hx, float hy, float hz) {
    Vec3 half = vec3_new(hx, hy, hz);
    box_set_half_extents(shape, &half);
}

float box_volume(const Vec3* halfExtents) {
    return 8.0f * halfExtents->x * halfExtents->y * halfExtents->z;
}

float box_surface_area(const Vec3* halfExtents) {
    float w = 2.0f * halfExtents->x;
    float h = 2.0f * halfExtents->y;
    float d = 2.0f * halfExtents->z;
    return 2.0f * (w * h + h * d + d * w);
}

void box_get_dimensions(const Shape* shape, Vec3* out) {
    if (shape && shape->type == SHAPE_BOX) {
        out->x = 2.0f * shape->geom.box.halfExtents.x;
        out->y = 2.0f * shape->geom.box.halfExtents.y;
        out->z = 2.0f * shape->geom.box.halfExtents.z;
    } else {
        *out = vec3_zero();
    }
}
