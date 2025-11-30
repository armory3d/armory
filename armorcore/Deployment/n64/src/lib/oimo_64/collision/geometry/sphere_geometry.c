#include "sphere_geometry.h"

#define PI 3.14159265358979323846f

// =============================================================================
// Sphere Geometry Implementation
// =============================================================================

float sphere_get_radius(const Shape* shape) {
    if (shape && shape->type == SHAPE_SPHERE) {
        return shape->geom.sphere.radius;
    }
    return 0.0f;
}

void sphere_set_radius(Shape* shape, float radius) {
    if (shape && shape->type == SHAPE_SPHERE) {
        shape->geom.sphere.radius = radius;
        if (shape->body) {
            shape_update_aabb(shape);
            rigidbody_update_mass(shape->body);
        }
    }
}

float sphere_volume(float radius) {
    return (4.0f / 3.0f) * PI * radius * radius * radius;
}

float sphere_surface_area(float radius) {
    return 4.0f * PI * radius * radius;
}
