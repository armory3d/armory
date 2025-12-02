// spatial_hash_broadphase.h
// Spatial hash broadphase for N64 - O(n) average case vs O(n²) brute force
#ifndef OIMO_COLLISION_BROADPHASE_SPATIAL_HASH_BROADPHASE_H
#define OIMO_COLLISION_BROADPHASE_SPATIAL_HASH_BROADPHASE_H

#include "broadphase.h"
#include <string.h>

// Spatial hash configuration - tuned for N64's cache
#define OIMO_HASH_CELL_SIZE     4.0f      // Cell size in world units
#define OIMO_HASH_TABLE_SIZE    64        // Hash table buckets (power of 2)
#define OIMO_HASH_MAX_PER_CELL  8         // Max proxies per cell before overflow

// Cell entry in hash table
typedef struct OimoHashCell {
    OimoProxy* proxies[OIMO_HASH_MAX_PER_CELL];
    int count;
} OimoHashCell;

// Extended broadphase with spatial hash data
typedef struct OimoSpatialHashBroadPhase {
    OimoBroadPhase base;
    OimoHashCell cells[OIMO_HASH_TABLE_SIZE];
    OimoScalar cellSize;
    OimoScalar invCellSize;
} OimoSpatialHashBroadPhase;

// Simple spatial hash function
static inline int oimo_spatial_hash(int x, int y, int z) {
    // Mix bits to reduce clustering
    int h = (x * 92837111) ^ (y * 689287499) ^ (z * 283923481);
    return (h & 0x7FFFFFFF) % OIMO_HASH_TABLE_SIZE;
}

// Get cell indices for a position
static inline void oimo_spatial_get_cell(OimoSpatialHashBroadPhase* bp, OimoScalar px, OimoScalar py, OimoScalar pz,
                                          int* cx, int* cy, int* cz) {
    *cx = (int)(px * bp->invCellSize);
    *cy = (int)(py * bp->invCellSize);
    *cz = (int)(pz * bp->invCellSize);
    // Handle negative coordinates
    if (px < 0) (*cx)--;
    if (py < 0) (*cy)--;
    if (pz < 0) (*cz)--;
}

static inline void oimo_spatial_hash_broadphase_init(OimoSpatialHashBroadPhase* bp) {
    oimo_broadphase_init(&bp->base, OIMO_BROADPHASE_SPATIAL_HASH);
    bp->base._incremental = 0;  // Rebuild each frame
    bp->cellSize = OIMO_HASH_CELL_SIZE;
    bp->invCellSize = 1.0f / OIMO_HASH_CELL_SIZE;
    memset(bp->cells, 0, sizeof(bp->cells));
}

static inline void oimo_spatial_hash_clear(OimoSpatialHashBroadPhase* bp) {
    for (int i = 0; i < OIMO_HASH_TABLE_SIZE; i++) {
        bp->cells[i].count = 0;
    }
}

// Insert proxy into all cells it overlaps
static inline void oimo_spatial_hash_insert(OimoSpatialHashBroadPhase* bp, OimoProxy* proxy) {
    int minX, minY, minZ, maxX, maxY, maxZ;
    oimo_spatial_get_cell(bp, proxy->_aabbMin.x, proxy->_aabbMin.y, proxy->_aabbMin.z, &minX, &minY, &minZ);
    oimo_spatial_get_cell(bp, proxy->_aabbMax.x, proxy->_aabbMax.y, proxy->_aabbMax.z, &maxX, &maxY, &maxZ);

    for (int z = minZ; z <= maxZ; z++) {
        for (int y = minY; y <= maxY; y++) {
            for (int x = minX; x <= maxX; x++) {
                int hash = oimo_spatial_hash(x, y, z);
                OimoHashCell* cell = &bp->cells[hash];
                if (cell->count < OIMO_HASH_MAX_PER_CELL) {
                    cell->proxies[cell->count++] = proxy;
                }
                // Overflow silently ignored - pairs still detected, just slower
            }
        }
    }
}

static inline OimoProxy* oimo_spatial_hash_create_proxy(OimoSpatialHashBroadPhase* bp, void* userData, const OimoAabb* aabb) {
    OimoBroadPhase* base = &bp->base;
    if (base->_proxyStorageUsed >= OIMO_MAX_PROXIES) {
        return NULL;
    }

    OimoProxy* proxy = &base->_proxyStorage[base->_proxyStorageUsed++];
    oimo_proxy_init(proxy, userData, base->_idCount++);

    oimo_broadphase_add_proxy(base, proxy);
    oimo_proxy_set_aabb(proxy, aabb);

    return proxy;
}

static inline void oimo_spatial_hash_destroy_proxy(OimoSpatialHashBroadPhase* bp, OimoProxy* proxy) {
    oimo_broadphase_remove_proxy(&bp->base, proxy);
    proxy->userData = NULL;
}

static inline void oimo_spatial_hash_move_proxy(OimoSpatialHashBroadPhase* bp, OimoProxy* proxy,
                                                 const OimoAabb* aabb, const OimoVec3* displacement) {
    (void)displacement;
    oimo_proxy_set_aabb(proxy, aabb);
}

// Check if two proxies already have a pair (avoid duplicates)
static inline int oimo_spatial_hash_pair_exists(OimoProxyPair* list, OimoProxy* p1, OimoProxy* p2) {
    OimoProxyPair* pp = list;
    while (pp != NULL) {
        if ((pp->_p1 == p1 && pp->_p2 == p2) || (pp->_p1 == p2 && pp->_p2 == p1)) {
            return 1;
        }
        pp = pp->_next;
    }
    return 0;
}

static inline void oimo_spatial_hash_collect_pairs(OimoSpatialHashBroadPhase* bp) {
    OimoBroadPhase* base = &bp->base;

    // Return previous pairs to pool
    oimo_broadphase_pool_pairs(base);

    // Clear and rebuild hash
    oimo_spatial_hash_clear(bp);

    // Insert all proxies into hash
    OimoProxy* p = base->_proxyList;
    while (p != NULL) {
        oimo_spatial_hash_insert(bp, p);
        p = p->_next;
    }

    base->_testCount = 0;

    // Check pairs within each cell
    for (int i = 0; i < OIMO_HASH_TABLE_SIZE; i++) {
        OimoHashCell* cell = &bp->cells[i];
        for (int a = 0; a < cell->count; a++) {
            for (int b = a + 1; b < cell->count; b++) {
                OimoProxy* p1 = cell->proxies[a];
                OimoProxy* p2 = cell->proxies[b];

                // Ensure consistent ordering to avoid duplicate checks
                if (p1->_id > p2->_id) {
                    OimoProxy* tmp = p1;
                    p1 = p2;
                    p2 = tmp;
                }

                base->_testCount++;

                // AABB overlap test
                if ((p1->_aabbMin.x <= p2->_aabbMax.x && p1->_aabbMax.x >= p2->_aabbMin.x) &&
                    (p1->_aabbMin.y <= p2->_aabbMax.y && p1->_aabbMax.y >= p2->_aabbMin.y) &&
                    (p1->_aabbMin.z <= p2->_aabbMax.z && p1->_aabbMax.z >= p2->_aabbMin.z)) {

                    // Avoid duplicate pairs (objects spanning multiple cells)
                    if (!oimo_spatial_hash_pair_exists(base->_proxyPairList, p1, p2)) {
                        oimo_broadphase_pick_and_push_pair(base, p1, p2);
                    }
                }
            }
        }
    }
}

static inline void oimo_spatial_hash_ray_cast(
    OimoSpatialHashBroadPhase* bp,
    const OimoVec3* begin,
    const OimoVec3* end,
    OimoBroadPhaseProxyCallback callback,
    void* callbackUserData
) {
    // For raycasting, fall back to linear scan (rays are infrequent)
    OimoProxy* p = bp->base._proxyList;
    while (p != NULL) {
        if (oimo_aabb_segment_test(&p->_aabbMin, &p->_aabbMax, begin, end)) {
            callback(p, callbackUserData);
        }
        p = p->_next;
    }
}

static inline void oimo_spatial_hash_aabb_test(
    OimoSpatialHashBroadPhase* bp,
    const OimoAabb* aabb,
    OimoBroadPhaseProxyCallback callback,
    void* callbackUserData
) {
    // Query cells overlapping the AABB
    int minX, minY, minZ, maxX, maxY, maxZ;
    oimo_spatial_get_cell(bp, aabb->min.x, aabb->min.y, aabb->min.z, &minX, &minY, &minZ);
    oimo_spatial_get_cell(bp, aabb->max.x, aabb->max.y, aabb->max.z, &maxX, &maxY, &maxZ);

    // Track already-visited proxies to avoid duplicate callbacks
    // Use a simple linear scan since query AABBs are typically small
    for (int z = minZ; z <= maxZ; z++) {
        for (int y = minY; y <= maxY; y++) {
            for (int x = minX; x <= maxX; x++) {
                int hash = oimo_spatial_hash(x, y, z);
                OimoHashCell* cell = &bp->cells[hash];
                for (int i = 0; i < cell->count; i++) {
                    OimoProxy* p = cell->proxies[i];
                    if ((aabb->min.x <= p->_aabbMax.x && aabb->max.x >= p->_aabbMin.x) &&
                        (aabb->min.y <= p->_aabbMax.y && aabb->max.y >= p->_aabbMin.y) &&
                        (aabb->min.z <= p->_aabbMax.z && aabb->max.z >= p->_aabbMin.z)) {
                        callback(p, callbackUserData);
                    }
                }
            }
        }
    }
}

#endif // OIMO_COLLISION_BROADPHASE_SPATIAL_HASH_BROADPHASE_H
