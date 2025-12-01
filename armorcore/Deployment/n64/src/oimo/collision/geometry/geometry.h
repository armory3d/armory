/**
 * OimoPhysics N64 Port - Base Geometry
 *
 * Abstract collision geometry base structure and functions.
 * Based on OimoPhysics Geometry.hx
 */

#ifndef OIMO_COLLISION_GEOMETRY_GEOMETRY_H
#define OIMO_COLLISION_GEOMETRY_GEOMETRY_H

#include "../../common/setting.h"
#include "../../common/vec3.h"
#include "../../common/mat3.h"
#include "../../common/transform.h"
#include "geometry_type.h"
#include "aabb.h"

// ============================================================================
// Ray Cast Hit Result
// ============================================================================
typedef struct OimoRayCastHit {
    OimoVec3 position;    // Hit position in world space
    OimoVec3 normal;      // Hit normal in world space
    OimoScalar fraction;  // Fraction along ray (0 to 1)
} OimoRayCastHit;

// Initialize ray cast hit
static inline void oimo_raycast_hit_init(OimoRayCastHit* hit) {
    hit->position = oimo_vec3_zero();
    hit->normal = oimo_vec3_zero();
    hit->fraction = 0;
}

// ============================================================================
// Base Geometry Structure
// ============================================================================

// Note: This is a "base class" in C. Specific geometries (Sphere, Box) will
// include this as the first member to allow casting.
typedef struct OimoGeometry {
    OimoGeometryType type;    // Geometry type
    OimoScalar volume;        // Volume of the geometry
    OimoMat3 inertia_coeff;   // Inertia tensor coefficients (I / mass)
} OimoGeometry;

// ============================================================================
// Geometry Initialization (used by derived types)
// ============================================================================

static inline void oimo_geometry_init(OimoGeometry* geom, OimoGeometryType type) {
    geom->type = type;
    geom->volume = 0;
    geom->inertia_coeff = oimo_mat3_zero();
}

// ============================================================================
// Getters
// ============================================================================

// Get geometry type
static inline OimoGeometryType oimo_geometry_get_type(const OimoGeometry* geom) {
    return geom->type;
}

// Get volume
static inline OimoScalar oimo_geometry_get_volume(const OimoGeometry* geom) {
    return geom->volume;
}

// Get inertia tensor for given mass: I = mass * inertia_coeff
static inline OimoMat3 oimo_geometry_get_inertia(const OimoGeometry* geom, OimoScalar mass) {
    return oimo_mat3_scale(&geom->inertia_coeff, mass);
}

// ============================================================================
// Mass Data Computation
// ============================================================================

// Compute mass from volume and density
static inline OimoScalar oimo_geometry_compute_mass(const OimoGeometry* geom, OimoScalar density) {
    return geom->volume * density;
}

// ============================================================================
// Forward Declarations for Virtual Functions
// ============================================================================
// These will be implemented by specific geometry types (sphere, box)
// In C, we use function pointers or switch statements based on type.

// Forward declarations - actual implementations in sphere_geometry.h and box_geometry.h
struct OimoSphereGeometry;
struct OimoBoxGeometry;

// ============================================================================
// Generic Dispatch Functions
// ============================================================================
// These check geometry type and call the appropriate implementation.
// Implementations are provided after including sphere and box headers.

// Compute AABB for geometry at given transform
// (Implementation requires sphere_geometry.h and box_geometry.h)
void oimo_geometry_compute_aabb(const OimoGeometry* geom, OimoAabb* aabb, const OimoTransform* tf);

// Ray cast against geometry at given transform
// Returns 1 if hit, 0 otherwise
// (Implementation requires sphere_geometry.h and box_geometry.h)
int oimo_geometry_ray_cast(
    const OimoGeometry* geom,
    const OimoVec3* begin,
    const OimoVec3* end,
    const OimoTransform* tf,
    OimoRayCastHit* hit
);

#endif // OIMO_COLLISION_GEOMETRY_GEOMETRY_H
