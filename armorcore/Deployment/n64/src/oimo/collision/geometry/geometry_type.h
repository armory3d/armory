#pragma once

typedef enum OimoGeometryType {
    OIMO_GEOMETRY_SPHERE  = 0,
    OIMO_GEOMETRY_BOX     = 1,
    OIMO_GEOMETRY_CAPSULE = 2,
    OIMO_GEOMETRY_STATIC_MESH = 3,

    // Count of supported types
    OIMO_GEOMETRY_TYPE_COUNT = 4
} OimoGeometryType;

// Check if type is a convex geometry
static inline int oimo_geometry_is_convex(OimoGeometryType type) {
    return type == OIMO_GEOMETRY_SPHERE || type == OIMO_GEOMETRY_BOX || type == OIMO_GEOMETRY_CAPSULE;
}

// Check if type is a mesh geometry (concave, static only)
static inline int oimo_geometry_is_mesh(OimoGeometryType type) {
    return type == OIMO_GEOMETRY_STATIC_MESH;
}

// Get geometry type name (for debugging)
static inline const char* oimo_geometry_type_name(OimoGeometryType type) {
    switch (type) {
        case OIMO_GEOMETRY_SPHERE:      return "Sphere";
        case OIMO_GEOMETRY_BOX:         return "Box";
        case OIMO_GEOMETRY_CAPSULE:     return "Capsule";
        case OIMO_GEOMETRY_STATIC_MESH: return "StaticMesh";
        default:                        return "Unknown";
    }
}

