#pragma once

// static_mesh_geometry.h - Static triangle mesh collision geometry with BVH

#include "geometry.h"
#include "../broadphase/bvh.h"
#include "../../common/vec3.h"
#include "../../common/mat3.h"
#include "../../common/transform.h"
#include <stdlib.h>
#include <string.h>
#include <math.h>

#ifdef __cplusplus
extern "C" {
#endif

// Triangle structure
typedef struct OimoTriangle {
    OimoVec3 v0, v1, v2;     // Vertices
    OimoVec3 normal;         // Face normal
    OimoVec3 edge1, edge2;   // Precomputed edges for collision
} OimoTriangle;

// Static mesh geometry
typedef struct OimoStaticMeshGeometry {
    OimoGeometry base;

    // Mesh data
    OimoTriangle* triangles;
    int16_t triangle_count;

    // BVH for spatial queries
    OimoBvhTree bvh;
    OimoBvhTriangle* bvh_triangles;  // BVH triangle data (centroids + AABBs)

    // Overall bounds
    OimoAabb bounds;
} OimoStaticMeshGeometry;

// Compute triangle normal from vertices
static inline OimoVec3 oimo_compute_triangle_normal(const OimoVec3* v0, const OimoVec3* v1, const OimoVec3* v2) {
    OimoVec3 edge1 = oimo_vec3_sub(*v1, *v0);
    OimoVec3 edge2 = oimo_vec3_sub(*v2, *v0);
    OimoVec3 normal = oimo_vec3_cross(edge1, edge2);
    return oimo_vec3_normalize(normal);
}

// Compute triangle centroid
static inline OimoVec3 oimo_compute_triangle_centroid(const OimoVec3* v0, const OimoVec3* v1, const OimoVec3* v2) {
    return oimo_vec3(
        (v0->x + v1->x + v2->x) / 3.0f,
        (v0->y + v1->y + v2->y) / 3.0f,
        (v0->z + v1->z + v2->z) / 3.0f
    );
}

// Compute triangle AABB
static inline void oimo_compute_triangle_aabb(const OimoVec3* v0, const OimoVec3* v1, const OimoVec3* v2, OimoAabb* aabb) {
    aabb->min.x = fminf(v0->x, fminf(v1->x, v2->x));
    aabb->min.y = fminf(v0->y, fminf(v1->y, v2->y));
    aabb->min.z = fminf(v0->z, fminf(v1->z, v2->z));
    aabb->max.x = fmaxf(v0->x, fmaxf(v1->x, v2->x));
    aabb->max.y = fmaxf(v0->y, fmaxf(v1->y, v2->y));
    aabb->max.z = fmaxf(v0->z, fmaxf(v1->z, v2->z));
}

// Initialize static mesh geometry from vertex and index arrays
// vertices: array of Vec3 positions
// indices: array of triangle indices (3 per triangle)
// vertex_count: number of vertices
// index_count: number of indices (must be multiple of 3)
static inline bool oimo_static_mesh_geometry_init(
    OimoStaticMeshGeometry* geom,
    const OimoVec3* vertices,
    const int16_t* indices,
    int vertex_count,
    int index_count
) {
    oimo_geometry_init(&geom->base, OIMO_GEOMETRY_STATIC_MESH);

    geom->triangle_count = (int16_t)(index_count / 3);
    if (geom->triangle_count == 0 || geom->triangle_count > OIMO_BVH_MAX_TRIANGLES) {
        return false;
    }

    // Allocate triangles
    geom->triangles = (OimoTriangle*)malloc(sizeof(OimoTriangle) * geom->triangle_count);
    if (!geom->triangles) return false;

    // Allocate BVH triangle data
    geom->bvh_triangles = (OimoBvhTriangle*)malloc(sizeof(OimoBvhTriangle) * geom->triangle_count);
    if (!geom->bvh_triangles) {
        free(geom->triangles);
        return false;
    }

    // Initialize BVH
    if (!oimo_bvh_tree_init(&geom->bvh, geom->triangle_count)) {
        free(geom->triangles);
        free(geom->bvh_triangles);
        return false;
    }

    // Build triangles and compute bounds
    oimo_aabb_init(&geom->bounds);

    for (int i = 0; i < geom->triangle_count; i++) {
        int idx = i * 3;
        const OimoVec3* v0 = &vertices[indices[idx]];
        const OimoVec3* v1 = &vertices[indices[idx + 1]];
        const OimoVec3* v2 = &vertices[indices[idx + 2]];

        // Store triangle data
        geom->triangles[i].v0 = *v0;
        geom->triangles[i].v1 = *v1;
        geom->triangles[i].v2 = *v2;
        geom->triangles[i].normal = oimo_compute_triangle_normal(v0, v1, v2);
        geom->triangles[i].edge1 = oimo_vec3_sub(*v1, *v0);
        geom->triangles[i].edge2 = oimo_vec3_sub(*v2, *v0);

        // Build BVH data
        geom->bvh_triangles[i].centroid = oimo_compute_triangle_centroid(v0, v1, v2);
        oimo_compute_triangle_aabb(v0, v1, v2, &geom->bvh_triangles[i].aabb);
        geom->bvh_triangles[i].original_index = (int16_t)i;

        // Expand overall bounds
        oimo_aabb_merge(&geom->bounds, &geom->bounds, &geom->bvh_triangles[i].aabb);
    }

    // Build BVH
    if (!oimo_bvh_tree_build(&geom->bvh, geom->bvh_triangles, geom->triangle_count)) {
        oimo_bvh_tree_free(&geom->bvh);
        free(geom->triangles);
        free(geom->bvh_triangles);
        return false;
    }

    // Compute approximate volume (bounding box volume)
    OimoVec3 size = oimo_vec3_sub(geom->bounds.max, geom->bounds.min);
    geom->base.volume = size.x * size.y * size.z;

    // Compute approximate inertia (as if it were a box)
    float mass = 1.0f;  // Normalized
    geom->base.inertia_coeff = oimo_mat3_diagonal(
        mass / 12.0f * (size.y * size.y + size.z * size.z),
        mass / 12.0f * (size.z * size.z + size.x * size.x),
        mass / 12.0f * (size.x * size.x + size.y * size.y)
    );

    return true;
}

// Free static mesh geometry
static inline void oimo_static_mesh_geometry_free(OimoStaticMeshGeometry* geom) {
    oimo_bvh_tree_free(&geom->bvh);
    if (geom->triangles) {
        free(geom->triangles);
        geom->triangles = NULL;
    }
    if (geom->bvh_triangles) {
        free(geom->bvh_triangles);
        geom->bvh_triangles = NULL;
    }
    geom->triangle_count = 0;
}

// Query triangles overlapping an AABB (in local space)
static inline void oimo_static_mesh_query_triangles(
    const OimoStaticMeshGeometry* geom,
    const OimoAabb* aabb,
    OimoBvhQueryResult* result
) {
    oimo_bvh_query(&geom->bvh, aabb, result);
}

// Get triangle by index
static inline const OimoTriangle* oimo_static_mesh_get_triangle(
    const OimoStaticMeshGeometry* geom,
    int index
) {
    if (index < 0 || index >= geom->triangle_count) return NULL;
    return &geom->triangles[index];
}

// Compute AABB in world space
static inline void oimo_static_mesh_compute_aabb(
    const OimoStaticMeshGeometry* geom,
    OimoAabb* aabb,
    const OimoTransform* tf
) {
    // Transform all 8 corners of local bounds and find enclosing AABB
    OimoVec3 corners[8];
    corners[0] = oimo_vec3(geom->bounds.min.x, geom->bounds.min.y, geom->bounds.min.z);
    corners[1] = oimo_vec3(geom->bounds.max.x, geom->bounds.min.y, geom->bounds.min.z);
    corners[2] = oimo_vec3(geom->bounds.min.x, geom->bounds.max.y, geom->bounds.min.z);
    corners[3] = oimo_vec3(geom->bounds.max.x, geom->bounds.max.y, geom->bounds.min.z);
    corners[4] = oimo_vec3(geom->bounds.min.x, geom->bounds.min.y, geom->bounds.max.z);
    corners[5] = oimo_vec3(geom->bounds.max.x, geom->bounds.min.y, geom->bounds.max.z);
    corners[6] = oimo_vec3(geom->bounds.min.x, geom->bounds.max.y, geom->bounds.max.z);
    corners[7] = oimo_vec3(geom->bounds.max.x, geom->bounds.max.y, geom->bounds.max.z);

    aabb->min = oimo_vec3(1e30f, 1e30f, 1e30f);
    aabb->max = oimo_vec3(-1e30f, -1e30f, -1e30f);

    for (int i = 0; i < 8; i++) {
        OimoVec3 world = oimo_mat3_mul_vec3(&tf->rotation, corners[i]);
        world = oimo_vec3_add(world, tf->position);

        if (world.x < aabb->min.x) aabb->min.x = world.x;
        if (world.y < aabb->min.y) aabb->min.y = world.y;
        if (world.z < aabb->min.z) aabb->min.z = world.z;
        if (world.x > aabb->max.x) aabb->max.x = world.x;
        if (world.y > aabb->max.y) aabb->max.y = world.y;
        if (world.z > aabb->max.z) aabb->max.z = world.z;
    }
}

// Ray cast against static mesh (uses BVH for acceleration)
static inline bool oimo_static_mesh_ray_cast(
    const OimoStaticMeshGeometry* geom,
    const OimoVec3* begin,
    const OimoVec3* end,
    OimoRayCastHit* hit
) {
    OimoVec3 ray_dir = oimo_vec3_sub(*end, *begin);
    float ray_length_sq = oimo_vec3_dot(ray_dir, ray_dir);
    if (ray_length_sq < 1e-12f) return false;

    float ray_length = sqrtf(ray_length_sq);
    ray_dir = oimo_vec3_scale(ray_dir, 1.0f / ray_length);

    // Build ray AABB
    OimoAabb ray_aabb;
    ray_aabb.min.x = fminf(begin->x, end->x);
    ray_aabb.min.y = fminf(begin->y, end->y);
    ray_aabb.min.z = fminf(begin->z, end->z);
    ray_aabb.max.x = fmaxf(begin->x, end->x);
    ray_aabb.max.y = fmaxf(begin->y, end->y);
    ray_aabb.max.z = fmaxf(begin->z, end->z);

    // Query overlapping triangles
    OimoBvhQueryResult query;
    oimo_static_mesh_query_triangles(geom, &ray_aabb, &query);

    float closest_t = 1e30f;
    int closest_tri = -1;

    // Möller–Trumbore ray-triangle intersection
    for (int i = 0; i < query.count; i++) {
        const OimoTriangle* tri = &geom->triangles[query.triangles[i]];

        OimoVec3 h = oimo_vec3_cross(ray_dir, tri->edge2);
        float a = oimo_vec3_dot(tri->edge1, h);

        if (a > -1e-6f && a < 1e-6f) continue;  // Parallel

        float f = 1.0f / a;
        OimoVec3 s = oimo_vec3_sub(*begin, tri->v0);
        float u = f * oimo_vec3_dot(s, h);

        if (u < 0.0f || u > 1.0f) continue;

        OimoVec3 q = oimo_vec3_cross(s, tri->edge1);
        float v = f * oimo_vec3_dot(ray_dir, q);

        if (v < 0.0f || u + v > 1.0f) continue;

        float t = f * oimo_vec3_dot(tri->edge2, q);

        if (t > 1e-6f && t <= ray_length && t < closest_t) {
            closest_t = t;
            closest_tri = query.triangles[i];
        }
    }

    if (closest_tri >= 0) {
        OimoVec3 scaled_dir = oimo_vec3_scale(ray_dir, closest_t);
        hit->position = oimo_vec3_add(*begin, scaled_dir);
        hit->normal = geom->triangles[closest_tri].normal;
        hit->fraction = closest_t / ray_length;
        return true;
    }

    return false;
}

#ifdef __cplusplus
}
#endif
