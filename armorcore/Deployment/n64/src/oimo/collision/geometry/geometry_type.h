/**
 * OimoPhysics N64 Port - Geometry Types
 *
 * Enumeration of collision geometry types.
 * Based on OimoPhysics GeometryType.hx
 */

#ifndef OIMO_COLLISION_GEOMETRY_GEOMETRY_TYPE_H
#define OIMO_COLLISION_GEOMETRY_GEOMETRY_TYPE_H

// ============================================================================
// Geometry Type Enum
// ============================================================================

typedef enum OimoGeometryType {
    OIMO_GEOMETRY_SPHERE = 0,
    OIMO_GEOMETRY_BOX    = 1,
    // Future types (not implemented for N64):
    // OIMO_GEOMETRY_CYLINDER   = 2,
    // OIMO_GEOMETRY_CONE       = 3,
    // OIMO_GEOMETRY_CAPSULE    = 4,
    // OIMO_GEOMETRY_CONVEX_HULL = 5,

    // Count of supported types
    OIMO_GEOMETRY_TYPE_COUNT = 2
} OimoGeometryType;

// ============================================================================
// Type Checking
// ============================================================================

// Check if type is a convex geometry (all our supported types are convex)
static inline int oimo_geometry_is_convex(OimoGeometryType type) {
    return type == OIMO_GEOMETRY_SPHERE || type == OIMO_GEOMETRY_BOX;
}

// Get geometry type name (for debugging)
static inline const char* oimo_geometry_type_name(OimoGeometryType type) {
    switch (type) {
        case OIMO_GEOMETRY_SPHERE: return "Sphere";
        case OIMO_GEOMETRY_BOX:    return "Box";
        default:                   return "Unknown";
    }
}

#endif // OIMO_COLLISION_GEOMETRY_GEOMETRY_TYPE_H
