#ifndef BOX_GEOMETRY_H
#define BOX_GEOMETRY_H

#include "../../dynamics/rigidbody/rigidbody.h"

#ifdef __cplusplus
extern "C" {
#endif

// =============================================================================
// Box Geometry API
// =============================================================================

// Get box half-extents from shape (outputs zero vector if not a box)
void box_get_half_extents(const Shape* shape, Vec3* out);

// Set box half-extents (updates AABB and mass if attached to body)
void box_set_half_extents(Shape* shape, const Vec3* halfExtents);

// Set box half-extents from individual values
void box_set_half_extents3(Shape* shape, float hx, float hy, float hz);

// Compute volume of box: 8 * hx * hy * hz
float box_volume(const Vec3* halfExtents);

// Compute surface area of box
float box_surface_area(const Vec3* halfExtents);

// Get full dimensions (width=2*hx, height=2*hy, depth=2*hz)
void box_get_dimensions(const Shape* shape, Vec3* out);

#ifdef __cplusplus
}
#endif

#endif
