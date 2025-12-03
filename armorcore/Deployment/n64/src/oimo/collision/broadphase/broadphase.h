#ifndef OIMO_COLLISION_BROADPHASE_BROADPHASE_H
#define OIMO_COLLISION_BROADPHASE_BROADPHASE_H

#include "broadphase_type.h"
#include "proxy.h"
#include "proxy_pair.h"
#include "../geometry/aabb.h"
#include "../../common/vec3.h"
#include "../../common/math_util.h"

#define OIMO_MAX_PROXIES 128
#define OIMO_MAX_PROXY_PAIRS 256

typedef void (*OimoBroadPhaseProxyCallback)(OimoProxy* proxy, void* userData);

typedef struct OimoBroadPhase {
    int _type;
    int _numProxies;
    OimoProxy* _proxyList;
    OimoProxy* _proxyListLast;
    OimoProxyPair* _proxyPairList;
    int _incremental;
    int _testCount;
    OimoProxyPair* _proxyPairPool;
    int _idCount;
    OimoProxy _proxyStorage[OIMO_MAX_PROXIES];
    OimoProxyPair _pairStorage[OIMO_MAX_PROXY_PAIRS];
    int _proxyStorageUsed;
    int _pairStorageUsed;
} OimoBroadPhase;

static inline void oimo_broadphase_list_push(OimoBroadPhase* bp, OimoProxy* p) {
    if (bp->_proxyListLast != NULL) {
        bp->_proxyListLast->_next = p;
        p->_prev = bp->_proxyListLast;
        p->_next = NULL;
        bp->_proxyListLast = p;
    } else {
        bp->_proxyList = p;
        bp->_proxyListLast = p;
        p->_prev = NULL;
        p->_next = NULL;
    }
}

static inline void oimo_broadphase_list_remove(OimoBroadPhase* bp, OimoProxy* p) {
    OimoProxy* prev = p->_prev;
    OimoProxy* next = p->_next;

    if (prev != NULL) {
        prev->_next = next;
    } else {
        bp->_proxyList = next;
    }

    if (next != NULL) {
        next->_prev = prev;
    } else {
        bp->_proxyListLast = prev;
    }

    p->_prev = NULL;
    p->_next = NULL;
}

static inline OimoProxyPair* oimo_broadphase_pick_pair(OimoBroadPhase* bp) {
    OimoProxyPair* pp;

    if (bp->_proxyPairPool != NULL) {
        // Reuse from pool
        pp = bp->_proxyPairPool;
        bp->_proxyPairPool = pp->_next;
    } else {
        // Allocate from storage
        if (bp->_pairStorageUsed < OIMO_MAX_PROXY_PAIRS) {
            pp = &bp->_pairStorage[bp->_pairStorageUsed++];
            oimo_proxy_pair_init(pp);
        } else {
            // Out of pairs - should not happen in normal usage
            return NULL;
        }
    }

    return pp;
}

static inline void oimo_broadphase_pick_and_push_pair(OimoBroadPhase* bp, OimoProxy* p1, OimoProxy* p2) {
    OimoProxyPair* pp = oimo_broadphase_pick_pair(bp);
    if (pp == NULL) return;

    // Add to front of list: M.singleList_addFirst(_proxyPairList, _next, pp)
    pp->_next = bp->_proxyPairList;
    bp->_proxyPairList = pp;

    pp->_p1 = p1;
    pp->_p2 = p2;
}

static inline int oimo_broadphase_is_overlapping(const OimoProxy* p1, const OimoProxy* p2);
static inline void oimo_broadphase_add_proxy(OimoBroadPhase* bp, OimoProxy* p);
static inline void oimo_broadphase_remove_proxy(OimoBroadPhase* bp, OimoProxy* p);
static inline void oimo_broadphase_pool_pairs(OimoBroadPhase* bp) {
    OimoProxyPair* p = bp->_proxyPairList;

    if (p != NULL) {
        // Clear pair references and find end of list
        OimoProxyPair* last = p;
        while (1) {
            p->_p1 = NULL;
            p->_p2 = NULL;
            if (p->_next == NULL) {
                last = p;
                break;
            }
            p = p->_next;
        }

        // Move entire list to pool
        last->_next = bp->_proxyPairPool;
        bp->_proxyPairPool = bp->_proxyPairList;
        bp->_proxyPairList = NULL;
    }
}

// O(n²) brute-force pair collection
static inline void oimo_broadphase_collect_pairs_bruteforce(OimoBroadPhase* bp) {
    // Return previous pairs to pool
    oimo_broadphase_pool_pairs(bp);

    bp->_testCount = 0;

    // Brute-force all pairs
    OimoProxy* p1 = bp->_proxyList;
    while (p1 != NULL) {
        OimoProxy* p2 = p1->_next;
        while (p2 != NULL) {
            bp->_testCount++;
            if (oimo_broadphase_is_overlapping(p1, p2)) {
                oimo_broadphase_pick_and_push_pair(bp, p1, p2);
            }
            p2 = p2->_next;
        }
        p1 = p1->_next;
    }
}

static inline void oimo_broadphase_collect_pairs(OimoBroadPhase* bp) {
    oimo_broadphase_collect_pairs_bruteforce(bp);
}

static inline void oimo_broadphase_init(OimoBroadPhase* bp, int type) {
    bp->_type = type;
    bp->_numProxies = 0;
    bp->_proxyList = NULL;
    bp->_proxyListLast = NULL;
    bp->_proxyPairList = NULL;
    bp->_incremental = 0;
    bp->_testCount = 0;
    bp->_proxyPairPool = NULL;
    bp->_idCount = 0;
    bp->_proxyStorageUsed = 0;
    bp->_pairStorageUsed = 0;
}

static inline OimoProxy* oimo_broadphase_create_proxy(OimoBroadPhase* bp, void* userData, const OimoAabb* aabb) {
    if (bp->_proxyStorageUsed >= OIMO_MAX_PROXIES) {
        return NULL;  // Out of proxy storage
    }

    OimoProxy* p = &bp->_proxyStorage[bp->_proxyStorageUsed++];
    oimo_proxy_init(p, userData, bp->_idCount++);

    // Set AABB
    p->_aabbMin = aabb->min;
    p->_aabbMax = aabb->max;

    // Add to broadphase
    oimo_broadphase_add_proxy(bp, p);

    return p;
}

static inline void oimo_broadphase_destroy_proxy(OimoBroadPhase* bp, OimoProxy* p) {
    oimo_broadphase_remove_proxy(bp, p);
}

static inline void oimo_broadphase_add_proxy(OimoBroadPhase* bp, OimoProxy* p) {
    bp->_numProxies++;
    oimo_broadphase_list_push(bp, p);
}

static inline void oimo_broadphase_remove_proxy(OimoBroadPhase* bp, OimoProxy* p) {
    bp->_numProxies--;
    oimo_broadphase_list_remove(bp, p);
}

static inline int oimo_broadphase_is_overlapping(const OimoProxy* p1, const OimoProxy* p2) {
    return (p1->_aabbMin.x <= p2->_aabbMax.x && p1->_aabbMax.x >= p2->_aabbMin.x) &&
           (p1->_aabbMin.y <= p2->_aabbMax.y && p1->_aabbMax.y >= p2->_aabbMin.y) &&
           (p1->_aabbMin.z <= p2->_aabbMax.z && p1->_aabbMax.z >= p2->_aabbMin.z);
}

static inline OimoProxyPair* oimo_broadphase_get_proxy_pair_list(const OimoBroadPhase* bp) {
    return bp->_proxyPairList;
}

static inline int oimo_broadphase_is_incremental(const OimoBroadPhase* bp) {
    return bp->_incremental;
}

static inline int oimo_broadphase_get_test_count(const OimoBroadPhase* bp) {
    return bp->_testCount;
}

// AABB-segment intersection using SAT (6 axes)
static inline int oimo_aabb_segment_test(
    const OimoVec3* aabbMin,
    const OimoVec3* aabbMax,
    const OimoVec3* begin,
    const OimoVec3* end
) {
    OimoScalar x1 = begin->x, y1 = begin->y, z1 = begin->z;
    OimoScalar x2 = end->x, y2 = end->y, z2 = end->z;

    // Segment bounding box
    OimoScalar sminx = oimo_min(x1, x2);
    OimoScalar sminy = oimo_min(y1, y2);
    OimoScalar sminz = oimo_min(z1, z2);
    OimoScalar smaxx = oimo_max(x1, x2);
    OimoScalar smaxy = oimo_max(y1, y2);
    OimoScalar smaxz = oimo_max(z1, z2);

    OimoScalar pminx = aabbMin->x, pminy = aabbMin->y, pminz = aabbMin->z;
    OimoScalar pmaxx = aabbMax->x, pmaxy = aabbMax->y, pmaxz = aabbMax->z;

    // Test axes (1,0,0), (0,1,0), (0,0,1)
    if (pminx > smaxx || pmaxx < sminx ||
        pminy > smaxy || pmaxy < sminy ||
        pminz > smaxz || pmaxz < sminz) {
        return 0;
    }

    // Segment direction
    OimoScalar dx = x2 - x1;
    OimoScalar dy = y2 - y1;
    OimoScalar dz = z2 - z1;
    OimoScalar adx = oimo_abs(dx);
    OimoScalar ady = oimo_abs(dy);
    OimoScalar adz = oimo_abs(dz);

    // AABB half-extents and center
    OimoScalar pextx = (pmaxx - pminx) * 0.5f;
    OimoScalar pexty = (pmaxy - pminy) * 0.5f;
    OimoScalar pextz = (pmaxz - pminz) * 0.5f;
    OimoScalar pcntx = (pmaxx + pminx) * 0.5f;
    OimoScalar pcnty = (pmaxy + pminy) * 0.5f;
    OimoScalar pcntz = (pmaxz + pminz) * 0.5f;

    // Vector from AABB center to segment start
    OimoScalar cpx = x1 - pcntx;
    OimoScalar cpy = y1 - pcnty;
    OimoScalar cpz = z1 - pcntz;

    // Test cross product axes:
    // axis4: d × (1,0,0) = (0, dz, -dy)
    // axis5: d × (0,1,0) = (-dz, 0, dx)
    // axis6: d × (0,0,1) = (dy, -dx, 0)
    if (oimo_abs(cpy * dz - cpz * dy) - (pexty * adz + pextz * ady) > 0 ||
        oimo_abs(cpz * dx - cpx * dz) - (pextz * adx + pextx * adz) > 0 ||
        oimo_abs(cpx * dy - cpy * dx) - (pextx * ady + pexty * adx) > 0) {
        return 0;
    }

    return 1;
}

#endif // OIMO_COLLISION_BROADPHASE_BROADPHASE_H
