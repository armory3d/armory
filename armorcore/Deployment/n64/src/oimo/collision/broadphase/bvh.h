// bvh.h - Simple BVH for static mesh triangle queries (N64 optimized)
#ifndef OIMO_COLLISION_BROADPHASE_BVH_H
#define OIMO_COLLISION_BROADPHASE_BVH_H

#include "../geometry/aabb.h"
#include "../../common/vec3.h"
#include <stdbool.h>
#include <stdint.h>
#include <stdlib.h>

#ifdef __cplusplus
extern "C" {
#endif

// Maximum triangles in a static mesh (N64 memory constraint)
#define OIMO_BVH_MAX_TRIANGLES 256

// Maximum depth of BVH tree (log2(256) + some margin)
#define OIMO_BVH_MAX_DEPTH 12

// Maximum triangles per leaf before splitting
#define OIMO_BVH_LEAF_THRESHOLD 4

// BVH Node - compact for N64
// If left_child == -1, it's a leaf node
typedef struct OimoBvhNode {
    OimoAabb aabb;           // Node bounding box
    int16_t left_child;      // Index of left child (-1 if leaf)
    int16_t right_child;     // Index of right child
    int16_t first_triangle;  // First index into sorted_indices array (for leaves)
    int16_t triangle_count;  // Number of triangles (for leaves)
} OimoBvhNode;

// BVH Tree for static mesh
typedef struct OimoBvhTree {
    OimoBvhNode* nodes;      // Node array (allocated)
    int16_t* sorted_indices; // Sorted triangle indices for leaf nodes
    int16_t node_count;      // Number of nodes used
    int16_t max_nodes;       // Maximum nodes allocated
    int16_t root;            // Root node index
    int16_t triangle_count;  // Total triangles
} OimoBvhTree;

// Triangle data for building BVH
typedef struct OimoBvhTriangle {
    OimoVec3 centroid;       // Triangle center (for partitioning)
    OimoAabb aabb;           // Triangle AABB
    int16_t original_index;  // Original triangle index in mesh
} OimoBvhTriangle;

// Query result - indices of triangles that overlap query AABB
typedef struct OimoBvhQueryResult {
    int16_t triangles[OIMO_BVH_MAX_TRIANGLES];
    int16_t count;
} OimoBvhQueryResult;

// Initialize BVH tree (allocate memory)
static inline bool oimo_bvh_tree_init(OimoBvhTree* tree, int max_triangles) {
    // Estimate max nodes: worst case is 2*n-1 for n leaves
    tree->max_nodes = (int16_t)(max_triangles * 2);
    tree->nodes = (OimoBvhNode*)malloc(sizeof(OimoBvhNode) * tree->max_nodes);
    if (!tree->nodes) return false;
    tree->sorted_indices = (int16_t*)malloc(sizeof(int16_t) * max_triangles);
    if (!tree->sorted_indices) {
        free(tree->nodes);
        tree->nodes = NULL;
        return false;
    }
    tree->node_count = 0;
    tree->root = -1;
    tree->triangle_count = 0;
    return true;
}

// Free BVH tree
static inline void oimo_bvh_tree_free(OimoBvhTree* tree) {
    if (tree->nodes) {
        free(tree->nodes);
        tree->nodes = NULL;
    }
    if (tree->sorted_indices) {
        free(tree->sorted_indices);
        tree->sorted_indices = NULL;
    }
    tree->node_count = 0;
    tree->root = -1;
    tree->triangle_count = 0;
}

// Allocate a new node
static inline int16_t oimo_bvh_alloc_node(OimoBvhTree* tree) {
    if (tree->node_count >= tree->max_nodes) return -1;
    int16_t idx = tree->node_count++;
    OimoBvhNode* node = &tree->nodes[idx];
    node->left_child = -1;
    node->right_child = -1;
    node->first_triangle = 0;
    node->triangle_count = 0;
    oimo_aabb_init(&node->aabb);
    return idx;
}

// Compute AABB enclosing all triangles in range
static inline void oimo_bvh_compute_bounds(
    const OimoBvhTriangle* triangles,
    const int16_t* indices,
    int count,
    OimoAabb* out_aabb
) {
    oimo_aabb_init(out_aabb);
    for (int i = 0; i < count; i++) {
        const OimoBvhTriangle* tri = &triangles[indices[i]];
        oimo_aabb_merge(out_aabb, out_aabb, &tri->aabb);
    }
}

// Partition triangles along the longest axis (simple median split)
static inline int oimo_bvh_partition(
    OimoBvhTriangle* triangles,
    int16_t* indices,
    int count,
    int axis
) {
    if (count <= 1) return 0;

    // Find median value along axis
    float min_val = 1e30f, max_val = -1e30f;
    for (int i = 0; i < count; i++) {
        float val;
        switch (axis) {
            case 0: val = triangles[indices[i]].centroid.x; break;
            case 1: val = triangles[indices[i]].centroid.y; break;
            default: val = triangles[indices[i]].centroid.z; break;
        }
        if (val < min_val) min_val = val;
        if (val > max_val) max_val = val;
    }
    float mid = (min_val + max_val) * 0.5f;

    // Partition around median
    int left = 0;
    int right = count - 1;
    while (left <= right) {
        float left_val;
        switch (axis) {
            case 0: left_val = triangles[indices[left]].centroid.x; break;
            case 1: left_val = triangles[indices[left]].centroid.y; break;
            default: left_val = triangles[indices[left]].centroid.z; break;
        }

        if (left_val < mid) {
            left++;
        } else {
            // Swap
            int16_t tmp = indices[left];
            indices[left] = indices[right];
            indices[right] = tmp;
            right--;
        }
    }

    // Ensure we don't have empty partitions
    if (left == 0) left = 1;
    if (left == count) left = count - 1;

    return left;
}

// Build BVH recursively - returns node index
// sorted_pos tracks current position in sorted_indices array
static inline int16_t oimo_bvh_build_recursive(
    OimoBvhTree* tree,
    OimoBvhTriangle* triangles,
    int16_t* indices,
    int count,
    int depth,
    int16_t* sorted_pos
) {
    if (count == 0 || depth > OIMO_BVH_MAX_DEPTH) return -1;

    int16_t node_idx = oimo_bvh_alloc_node(tree);
    if (node_idx < 0) return -1;

    OimoBvhNode* node = &tree->nodes[node_idx];
    oimo_bvh_compute_bounds(triangles, indices, count, &node->aabb);

    // Make leaf if few enough triangles
    if (count <= OIMO_BVH_LEAF_THRESHOLD) {
        node->left_child = -1;
        node->right_child = -1;
        node->first_triangle = *sorted_pos;
        node->triangle_count = (int16_t)count;
        // Copy triangle indices to sorted array
        for (int i = 0; i < count; i++) {
            tree->sorted_indices[(*sorted_pos)++] = triangles[indices[i]].original_index;
        }
        return node_idx;
    }

    // Find longest axis
    OimoVec3 size = oimo_vec3_sub(node->aabb.max, node->aabb.min);
    int axis = 0;
    if (size.y > size.x) axis = 1;
    if (size.z > (axis == 0 ? size.x : size.y)) axis = 2;

    // Partition
    int mid = oimo_bvh_partition(triangles, indices, count, axis);

    // Build children
    node->left_child = oimo_bvh_build_recursive(tree, triangles, indices, mid, depth + 1, sorted_pos);
    node->right_child = oimo_bvh_build_recursive(tree, triangles, indices + mid, count - mid, depth + 1, sorted_pos);

    return node_idx;
}

// Build BVH from triangle data
static inline bool oimo_bvh_tree_build(
    OimoBvhTree* tree,
    OimoBvhTriangle* triangles,
    int triangle_count
) {
    if (triangle_count == 0 || triangle_count > OIMO_BVH_MAX_TRIANGLES) return false;

    tree->triangle_count = (int16_t)triangle_count;

    // Create index array
    int16_t* indices = (int16_t*)malloc(sizeof(int16_t) * triangle_count);
    if (!indices) return false;

    for (int i = 0; i < triangle_count; i++) {
        indices[i] = (int16_t)i;
        triangles[i].original_index = (int16_t)i;
    }

    // Build tree
    int16_t sorted_pos = 0;
    tree->root = oimo_bvh_build_recursive(tree, triangles, indices, triangle_count, 0, &sorted_pos);

    free(indices);
    return tree->root >= 0;
}

// Query BVH for triangles overlapping an AABB
static inline void oimo_bvh_query_recursive(
    const OimoBvhTree* tree,
    int16_t node_idx,
    const OimoAabb* query_aabb,
    OimoBvhQueryResult* result
) {
    if (node_idx < 0 || result->count >= OIMO_BVH_MAX_TRIANGLES) return;

    const OimoBvhNode* node = &tree->nodes[node_idx];

    // Check if query overlaps this node
    if (!oimo_aabb_overlap(&node->aabb, query_aabb)) return;

    // Leaf node - add triangles from sorted_indices
    if (node->left_child < 0) {
        for (int i = 0; i < node->triangle_count && result->count < OIMO_BVH_MAX_TRIANGLES; i++) {
            int16_t tri_idx = tree->sorted_indices[node->first_triangle + i];
            result->triangles[result->count++] = tri_idx;
        }
        return;
    }

    // Internal node - recurse
    oimo_bvh_query_recursive(tree, node->left_child, query_aabb, result);
    oimo_bvh_query_recursive(tree, node->right_child, query_aabb, result);
}

// Query BVH for triangles overlapping an AABB
static inline void oimo_bvh_query(
    const OimoBvhTree* tree,
    const OimoAabb* query_aabb,
    OimoBvhQueryResult* result
) {
    result->count = 0;
    oimo_bvh_query_recursive(tree, tree->root, query_aabb, result);
}

#ifdef __cplusplus
}
#endif

#endif // OIMO_COLLISION_BROADPHASE_BVH_H
