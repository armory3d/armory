#pragma once

#include "../geometry/aabb.h"
#include "../../common/vec3.h"

// Forward declaration
struct OimoShape;

typedef struct OimoProxy {
    struct OimoProxy* _prev;    // Previous proxy in list
    struct OimoProxy* _next;    // Next proxy in list

    // Fattened AABB (stored as min/max vectors like OimoPhysics)
    OimoVec3 _aabbMin;
    OimoVec3 _aabbMax;

    int _id;                    // Unique proxy ID

        void* userData;
} OimoProxy;

static inline void oimo_proxy_init(OimoProxy* proxy, void* userData, int id) {
    proxy->userData = userData;
    proxy->_id = id;
    proxy->_prev = NULL;
    proxy->_next = NULL;
    proxy->_aabbMin = oimo_vec3_zero();
    proxy->_aabbMax = oimo_vec3_zero();
}

static inline void oimo_proxy_set_aabb(OimoProxy* proxy, const OimoAabb* aabb) {
    proxy->_aabbMin = aabb->min;
    proxy->_aabbMax = aabb->max;
}

static inline int oimo_proxy_get_id(const OimoProxy* proxy) {
    return proxy->_id;
}

static inline OimoAabb oimo_proxy_get_fat_aabb(const OimoProxy* proxy) {
    OimoAabb aabb;
    aabb.min = proxy->_aabbMin;
    aabb.max = proxy->_aabbMax;
    return aabb;
}

static inline void oimo_proxy_get_fat_aabb_to(const OimoProxy* proxy, OimoAabb* aabb) {
    aabb->min = proxy->_aabbMin;
    aabb->max = proxy->_aabbMax;
}

