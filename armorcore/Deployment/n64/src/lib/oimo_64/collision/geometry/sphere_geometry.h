#ifndef SPHERE_GEOMETRY_H
#define SPHERE_GEOMETRY_H

#include "../../dynamics/rigidbody/rigidbody.h"

#ifdef __cplusplus
extern "C" {
#endif

// =============================================================================
// Sphere Geometry API
// =============================================================================

// Get sphere radius from shape (returns 0 if not a sphere)
float sphere_get_radius(const Shape* shape);

// Set sphere radius (updates AABB and mass if attached to body)
void sphere_set_radius(Shape* shape, float radius);

// Compute volume of sphere: (4/3) * PI * r^3
float sphere_volume(float radius);

// Compute surface area of sphere: 4 * PI * r^2
float sphere_surface_area(float radius);

#ifdef __cplusplus
}
#endif

#endif
