#ifndef OIMO_COLLISION_GEOMETRY_GEOMETRY_H
#define OIMO_COLLISION_GEOMETRY_GEOMETRY_H

#include "../../common/setting.h"
#include "../../common/vec3.h"
#include "../../common/mat3.h"
#include "../../common/transform.h"
#include "geometry_type.h"
#include "aabb.h"

typedef struct OimoRayCastHit {
    OimoVec3 position;
    OimoVec3 normal;
    OimoScalar fraction;
} OimoRayCastHit;

static inline void oimo_raycast_hit_init(OimoRayCastHit* hit) {
    hit->position = oimo_vec3_zero();
    hit->normal = oimo_vec3_zero();
    hit->fraction = 0;
}

typedef struct OimoGeometry {
    OimoGeometryType type;
    OimoScalar volume;
    OimoMat3 inertia_coeff;
} OimoGeometry;

static inline void oimo_geometry_init(OimoGeometry* geom, OimoGeometryType type) {
    geom->type = type;
    geom->volume = 0;
    geom->inertia_coeff = oimo_mat3_zero();
}

static inline OimoGeometryType oimo_geometry_get_type(const OimoGeometry* geom) {
    return geom->type;
}

static inline OimoScalar oimo_geometry_get_volume(const OimoGeometry* geom) {
    return geom->volume;
}

static inline OimoMat3 oimo_geometry_get_inertia(const OimoGeometry* geom, OimoScalar mass) {
    return oimo_mat3_scale(&geom->inertia_coeff, mass);
}

static inline OimoScalar oimo_geometry_compute_mass(const OimoGeometry* geom, OimoScalar density) {
    return geom->volume * density;
}

struct OimoSphereGeometry;
struct OimoBoxGeometry;

void oimo_geometry_compute_aabb(const OimoGeometry* geom, OimoAabb* aabb, const OimoTransform* tf);

int oimo_geometry_ray_cast(
    const OimoGeometry* geom,
    const OimoVec3* begin,
    const OimoVec3* end,
    const OimoTransform* tf,
    OimoRayCastHit* hit
);

#endif
