/**
 * Physics Debug Drawing for N64
 * Hardware rendering version - uses RDP triangles for line drawing
 *
 * Uses rdpq_triangle() with degenerate triangles for line rendering.
 * This provides hardware acceleration while staying within the RDP pipeline.
 */

#include "physics_debug.h"
#include <libdragon.h>
#include <rdpq.h>
#include <rdpq_mode.h>
#include <rdpq_tri.h>
#include <t3d/t3d.h>
#include <math.h>
#include <stdint.h>
#include <stdbool.h>

// Geometry headers
#include "../collision/geometry/box_geometry.h"
#include "../collision/geometry/sphere_geometry.h"
#include "../collision/geometry/capsule_geometry.h"
#include "../collision/geometry/static_mesh_geometry.h"

// =============================================================================
// Configuration Constants
// =============================================================================

#define CIRCLE_SEGMENTS 8
#define RGBA5551(r, g, b) (((r) << 11) | ((g) << 6) | ((b) << 1) | 1)

// Safety limits to prevent crashes and RDP command buffer overflow
#define MAX_BODIES_PER_FRAME      256
#define MAX_SHAPES_PER_BODY       16
#define MAX_CONTACTS_PER_FRAME    128
#define MAX_CONTACT_POINTS        4
#define MAX_LINES_PER_FRAME       2000
#define MAX_MESH_TRIANGLES        400
#define MAX_NORMAL_TRIANGLES      100

// Screen bounds for clipping (with margin for off-screen rejection)
#define SCREEN_MARGIN             100
#define MAX_SCREEN_WIDTH          640
#define MAX_SCREEN_HEIGHT         480

// Precomputed step for capsule vertical lines (avoids division in loop)
#define CAPSULE_VERT_STEP         (CIRCLE_SEGMENTS / 4)

// =============================================================================
// Global State
// =============================================================================

static PhysicsDebugDraw g_debug = {0};

// Pre-computed circle LUT for sphere/capsule rendering
static float g_circle_sin[CIRCLE_SEGMENTS + 1];
static float g_circle_cos[CIRCLE_SEGMENTS + 1];
static bool g_circle_lut_ready = false;

// Per-frame state
static int g_lines_this_frame = 0;
static uint32_t g_screen_w = 0;
static uint32_t g_screen_h = 0;
static T3DViewport *g_viewport = NULL;

// Cached frustum pointer for per-shape culling
static const T3DFrustum *g_frustum = NULL;

// RDP mode initialized flag
static bool g_rdp_mode_set = false;

// =============================================================================
// Initialization
// =============================================================================

/**
 * Initialize circle lookup tables for sphere/capsule rendering
 */
static void init_circle_lut(void)
{
    if (g_circle_lut_ready) return;

    const float PI2 = 6.28318530718f;
    for (int i = 0; i <= CIRCLE_SEGMENTS; i++) {
        float angle = (float)i / CIRCLE_SEGMENTS * PI2;
        g_circle_sin[i] = sinf(angle);
        g_circle_cos[i] = cosf(angle);
    }
    g_circle_lut_ready = true;
}

// =============================================================================
// Low-level Drawing Utilities
// =============================================================================

/**
 * Convert RGBA5551 to color_t for RDP
 */
static inline color_t rgba5551_to_color(uint16_t c)
{
    uint8_t r = ((c >> 11) & 0x1F) << 3;
    uint8_t g = ((c >> 6) & 0x1F) << 3;
    uint8_t b = ((c >> 1) & 0x1F) << 3;
    return RGBA32(r, g, b, 255);
}

/**
 * Check if float is valid (not NaN, not Inf, within reasonable range)
 * Uses isfinite() which is the proper C99 way to check for valid floats.
 */
static inline bool is_valid_float(float f)
{
    // isfinite() returns true if f is not NaN and not Inf
    if (!isfinite(f)) return false;

    // Reject extreme values that could cause projection issues
    if (f > 1e6f || f < -1e6f) return false;

    return true;
}

/**
 * Draw 2D line using RDP hardware (degenerate triangle)
 * Uses rdpq_triangle for hardware-accelerated line rendering
 */
static void debugDrawLine(int x0, int y0, int x1, int y1, uint16_t color)
{
    // Enforce per-frame line budget to prevent slowdown/crashes
    if (g_lines_this_frame >= MAX_LINES_PER_FRAME) return;

    g_lines_this_frame++;

    // Early reject lines completely off screen (with margin)
    int w = (int)g_screen_w;
    int h = (int)g_screen_h;

    if ((x0 > w + SCREEN_MARGIN && x1 > w + SCREEN_MARGIN) ||
        (y0 > h + SCREEN_MARGIN && y1 > h + SCREEN_MARGIN) ||
        (x0 < -SCREEN_MARGIN && x1 < -SCREEN_MARGIN) ||
        (y0 < -SCREEN_MARGIN && y1 < -SCREEN_MARGIN)) {
        return;
    }

    // Set color for this line
    rdpq_set_prim_color(rgba5551_to_color(color));

    // Draw line as a thin triangle (degenerate triangle with 1 pixel offset)
    // Create a perpendicular offset for line thickness
    float dx = (float)(x1 - x0);
    float dy = (float)(y1 - y0);
    float len = sqrtf(dx * dx + dy * dy);
    if (len < 0.001f) return;  // Skip zero-length lines

    // Perpendicular unit vector scaled by half line width (0.5 pixel)
    float px = -dy / len * 0.5f;
    float py = dx / len * 0.5f;

    // Two triangles forming a thin quad (line)
    float v0[] = { (float)x0 - px, (float)y0 - py };
    float v1[] = { (float)x0 + px, (float)y0 + py };
    float v2[] = { (float)x1 + px, (float)y1 + py };
    float v3[] = { (float)x1 - px, (float)y1 - py };

    rdpq_triangle(&TRIFMT_FILL, v0, v1, v2);
    rdpq_triangle(&TRIFMT_FILL, v0, v2, v3);
}

/**
 * Draw 3D line projected to screen space via T3D viewport
 */
static void debugDrawLineVec3(float x0, float y0, float z0,
                              float x1, float y1, float z1, uint16_t color)
{
    // Validate input coordinates
    if (!is_valid_float(x0) || !is_valid_float(y0) || !is_valid_float(z0) ||
        !is_valid_float(x1) || !is_valid_float(y1) || !is_valid_float(z1)) {
        return;
    }

    if (!g_viewport) return;

    T3DVec3 p0 = {{x0, y0, z0}};
    T3DVec3 p1 = {{x1, y1, z1}};
    T3DVec3 s0, s1;

    t3d_viewport_calc_viewspace_pos(g_viewport, &s0, &p0);
    t3d_viewport_calc_viewspace_pos(g_viewport, &s1, &p1);

    // Validate projected coordinates
    if (!is_valid_float(s0.v[0]) || !is_valid_float(s0.v[1]) || !is_valid_float(s0.v[2]) ||
        !is_valid_float(s1.v[0]) || !is_valid_float(s1.v[1]) || !is_valid_float(s1.v[2])) {
        return;
    }

    // Near-plane clipping: reject lines that cross or are behind the near plane.
    // z values close to 0 or negative indicate the point is at or behind camera.
    // Using 0.01f as minimum depth to avoid division issues in projection.
    const float MIN_DEPTH = 0.01f;
    if (s0.v[2] < MIN_DEPTH || s1.v[2] < MIN_DEPTH) {
        return;
    }

    // Only draw if both points in front of camera (z < 1.0 means in view frustum)
    if (s0.v[2] < 1.0f && s1.v[2] < 1.0f) {
        debugDrawLine((int)s0.v[0], (int)s0.v[1], (int)s1.v[0], (int)s1.v[1], color);
    }
}

// =============================================================================
// Shape Drawing Functions
// =============================================================================

// Box edge indices (const - never changes)
static const int box_edges[12][2] = {
    {0,1}, {1,2}, {2,3}, {3,0},  // Bottom face
    {4,5}, {5,6}, {6,7}, {7,4},  // Top face
    {0,4}, {1,5}, {2,6}, {3,7}   // Vertical edges
};

/**
 * Draw box wireframe (12 edges)
 * Uses static arrays to avoid N64 stack overflow
 */
static void draw_box(const OimoVec3 *center,
                     const OimoMat3 *rot, float hx, float hy, float hz, uint16_t color)
{
    if (!center || !rot) return;

    // Static to avoid stack allocation
    static float world[8][3];

    // 8 corners - compute directly into world space
    const float signs[8][3] = {
        {-1, -1, -1}, {+1, -1, -1}, {+1, +1, -1}, {-1, +1, -1},
        {-1, -1, +1}, {+1, -1, +1}, {+1, +1, +1}, {-1, +1, +1}
    };

    for (int i = 0; i < 8; i++) {
        float lx = signs[i][0] * hx;
        float ly = signs[i][1] * hy;
        float lz = signs[i][2] * hz;
        world[i][0] = center->x + rot->e00*lx + rot->e01*ly + rot->e02*lz;
        world[i][1] = center->y + rot->e10*lx + rot->e11*ly + rot->e12*lz;
        world[i][2] = center->z + rot->e20*lx + rot->e21*ly + rot->e22*lz;
    }

    for (int i = 0; i < 12; i++) {
        int a = box_edges[i][0], b = box_edges[i][1];
        debugDrawLineVec3(world[a][0], world[a][1], world[a][2],
                          world[b][0], world[b][1], world[b][2], color);
    }
}

/**
 * Draw sphere wireframe (3 orthogonal circles)
 * Precomputes scaled axes to reduce FPU operations in loops
 */
static void draw_sphere(const OimoVec3 *center,
                        const OimoMat3 *rot, float radius, uint16_t color)
{
    if (!center || !rot || radius <= 0.0f) return;
    init_circle_lut();

    // Precompute scaled axes (axis * radius) - reduces multiplications in loop
    const float axXx = rot->e00 * radius, axXy = rot->e10 * radius, axXz = rot->e20 * radius;
    const float axYx = rot->e01 * radius, axYy = rot->e11 * radius, axYz = rot->e21 * radius;
    const float axZx = rot->e02 * radius, axZy = rot->e12 * radius, axZz = rot->e22 * radius;
    const float cx = center->x, cy = center->y, cz = center->z;

    // XY circle
    for (int i = 0; i < CIRCLE_SEGMENTS; i++) {
        float c0 = g_circle_cos[i], s0 = g_circle_sin[i];
        float c1 = g_circle_cos[i+1], s1 = g_circle_sin[i+1];
        debugDrawLineVec3(cx + c0*axXx + s0*axYx, cy + c0*axXy + s0*axYy, cz + c0*axXz + s0*axYz,
                          cx + c1*axXx + s1*axYx, cy + c1*axXy + s1*axYy, cz + c1*axXz + s1*axYz, color);
    }

    // XZ circle
    for (int i = 0; i < CIRCLE_SEGMENTS; i++) {
        float c0 = g_circle_cos[i], s0 = g_circle_sin[i];
        float c1 = g_circle_cos[i+1], s1 = g_circle_sin[i+1];
        debugDrawLineVec3(cx + c0*axXx + s0*axZx, cy + c0*axXy + s0*axZy, cz + c0*axXz + s0*axZz,
                          cx + c1*axXx + s1*axZx, cy + c1*axXy + s1*axZy, cz + c1*axXz + s1*axZz, color);
    }

    // YZ circle
    for (int i = 0; i < CIRCLE_SEGMENTS; i++) {
        float c0 = g_circle_cos[i], s0 = g_circle_sin[i];
        float c1 = g_circle_cos[i+1], s1 = g_circle_sin[i+1];
        debugDrawLineVec3(cx + c0*axYx + s0*axZx, cy + c0*axYy + s0*axZy, cz + c0*axYz + s0*axZz,
                          cx + c1*axYx + s1*axZx, cy + c1*axYy + s1*axZy, cz + c1*axYz + s1*axZz, color);
    }
}

/**
 * Draw capsule wireframe with hemisphere caps
 * Precomputes scaled axes to reduce FPU operations
 */
static void draw_capsule(const OimoVec3 *center,
                         const OimoMat3 *rot, float radius, float halfHeight, uint16_t color)
{
    if (!center || !rot || radius <= 0.0f) return;
    init_circle_lut();

    // Precompute scaled axes (axis * radius)
    const float rx = rot->e00 * radius, ry = rot->e10 * radius, rz = rot->e20 * radius;
    const float ux = rot->e01 * radius, uy = rot->e11 * radius, uz = rot->e21 * radius;
    const float fx = rot->e02 * radius, fy = rot->e12 * radius, fz = rot->e22 * radius;

    // Precompute top and bottom centers
    const float upx = rot->e01 * halfHeight, upy = rot->e11 * halfHeight, upz = rot->e21 * halfHeight;
    const float tx = center->x + upx, ty = center->y + upy, tz = center->z + upz;
    const float bx = center->x - upx, by = center->y - upy, bz = center->z - upz;

    // Top and bottom circles (at cylinder ends)
    for (int i = 0; i < CIRCLE_SEGMENTS; i++) {
        float c0 = g_circle_cos[i], s0 = g_circle_sin[i];
        float c1 = g_circle_cos[i+1], s1 = g_circle_sin[i+1];

        // Top circle
        debugDrawLineVec3(tx + rx*c0 + fx*s0, ty + ry*c0 + fy*s0, tz + rz*c0 + fz*s0,
                          tx + rx*c1 + fx*s1, ty + ry*c1 + fy*s1, tz + rz*c1 + fz*s1, color);
        // Bottom circle
        debugDrawLineVec3(bx + rx*c0 + fx*s0, by + ry*c0 + fy*s0, bz + rz*c0 + fz*s0,
                          bx + rx*c1 + fx*s1, by + ry*c1 + fy*s1, bz + rz*c1 + fz*s1, color);
    }

    // 4 vertical lines connecting top and bottom circles
    // Using precomputed step constant instead of division
    int idx = 0;
    for (int i = 0; i < 4; i++) {
        float c = g_circle_cos[idx], s = g_circle_sin[idx];
        float px = rx*c + fx*s, py = ry*c + fy*s, pz = rz*c + fz*s;
        debugDrawLineVec3(tx + px, ty + py, tz + pz, bx + px, by + py, bz + pz, color);
        idx += CAPSULE_VERT_STEP;
    }

    // Top hemisphere cap arcs (upper half of circle)
    const int halfSeg = CIRCLE_SEGMENTS / 2;
    for (int i = 0; i < halfSeg; i++) {
        float c0 = g_circle_cos[i], s0 = g_circle_sin[i];
        float c1 = g_circle_cos[i+1], s1 = g_circle_sin[i+1];
        // Right-up arc
        debugDrawLineVec3(tx + rx*c0 + ux*s0, ty + ry*c0 + uy*s0, tz + rz*c0 + uz*s0,
                          tx + rx*c1 + ux*s1, ty + ry*c1 + uy*s1, tz + rz*c1 + uz*s1, color);
        // Forward-up arc
        debugDrawLineVec3(tx + fx*c0 + ux*s0, ty + fy*c0 + uy*s0, tz + fz*c0 + uz*s0,
                          tx + fx*c1 + ux*s1, ty + fy*c1 + uy*s1, tz + fz*c1 + uz*s1, color);
    }

    // Bottom hemisphere cap arcs (lower half of circle)
    for (int i = halfSeg; i < CIRCLE_SEGMENTS; i++) {
        float c0 = g_circle_cos[i], s0 = g_circle_sin[i];
        float c1 = g_circle_cos[i+1], s1 = g_circle_sin[i+1];
        // Right-up arc
        debugDrawLineVec3(bx + rx*c0 + ux*s0, by + ry*c0 + uy*s0, bz + rz*c0 + uz*s0,
                          bx + rx*c1 + ux*s1, by + ry*c1 + uy*s1, bz + rz*c1 + uz*s1, color);
        // Forward-up arc
        debugDrawLineVec3(bx + fx*c0 + ux*s0, by + fy*c0 + uy*s0, bz + fz*c0 + uz*s0,
                          bx + fx*c1 + ux*s1, by + fy*c1 + uy*s1, bz + fz*c1 + uz*s1, color);
    }
}

/**
 * Draw AABB wireframe (12 edges)
 */
static void draw_aabb(const OimoAabb *aabb, uint16_t color)
{
    if (!aabb) return;

    float minX = aabb->min.x, minY = aabb->min.y, minZ = aabb->min.z;
    float maxX = aabb->max.x, maxY = aabb->max.y, maxZ = aabb->max.z;

    // Validate AABB bounds
    if (!is_valid_float(minX) || !is_valid_float(minY) || !is_valid_float(minZ) ||
        !is_valid_float(maxX) || !is_valid_float(maxY) || !is_valid_float(maxZ)) {
        return;
    }

    // Bottom face
    debugDrawLineVec3(minX, minY, minZ, maxX, minY, minZ, color);
    debugDrawLineVec3(maxX, minY, minZ, maxX, minY, maxZ, color);
    debugDrawLineVec3(maxX, minY, maxZ, minX, minY, maxZ, color);
    debugDrawLineVec3(minX, minY, maxZ, minX, minY, minZ, color);

    // Top face
    debugDrawLineVec3(minX, maxY, minZ, maxX, maxY, minZ, color);
    debugDrawLineVec3(maxX, maxY, minZ, maxX, maxY, maxZ, color);
    debugDrawLineVec3(maxX, maxY, maxZ, minX, maxY, maxZ, color);
    debugDrawLineVec3(minX, maxY, maxZ, minX, maxY, minZ, color);

    // Vertical edges
    debugDrawLineVec3(minX, minY, minZ, minX, maxY, minZ, color);
    debugDrawLineVec3(maxX, minY, minZ, maxX, maxY, minZ, color);
    debugDrawLineVec3(maxX, minY, maxZ, maxX, maxY, maxZ, color);
    debugDrawLineVec3(minX, minY, maxZ, minX, maxY, maxZ, color);
}

/**
 * Draw body coordinate axes gizmo (XYZ colored arrows)
 */
static void draw_axes(const OimoVec3 *center,
                      const OimoMat3 *rot, float length)
{
    if (!center || !rot || length <= 0.0f) return;
    // X axis (red)
    debugDrawLineVec3(center->x, center->y, center->z,
                      center->x + rot->e00 * length,
                      center->y + rot->e10 * length,
                      center->z + rot->e20 * length,
                      g_debug.colors.axis_x);
    // Y axis (green)
    debugDrawLineVec3(center->x, center->y, center->z,
                      center->x + rot->e01 * length,
                      center->y + rot->e11 * length,
                      center->z + rot->e21 * length,
                      g_debug.colors.axis_y);
    // Z axis (blue)
    debugDrawLineVec3(center->x, center->y, center->z,
                      center->x + rot->e02 * length,
                      center->y + rot->e12 * length,
                      center->z + rot->e22 * length,
                      g_debug.colors.axis_z);
}

/**
 * Draw static mesh wireframe (triangle edges)
 * Limited to prevent frame time overflow
 */
static void draw_static_mesh(const OimoVec3 *pos, const OimoMat3 *rot,
                             OimoStaticMeshGeometry *mesh, uint16_t color)
{
    if (!pos || !rot || !mesh || !mesh->triangles || mesh->triangle_count <= 0) return;

    // Limit triangles to prevent slowdown (each triangle = 3 lines)
    int max_tris = mesh->triangle_count;
    if (max_tris > MAX_MESH_TRIANGLES) max_tris = MAX_MESH_TRIANGLES;

    for (int i = 0; i < max_tris; i++) {
        // Check line budget before drawing (each triangle = 3 lines)
        if (g_lines_this_frame >= MAX_LINES_PER_FRAME - 3) return;

        OimoTriangle *tri = &mesh->triangles[i];

        // Transform vertices to world space
        float wx0 = pos->x + rot->e00*tri->v0.x + rot->e01*tri->v0.y + rot->e02*tri->v0.z;
        float wy0 = pos->y + rot->e10*tri->v0.x + rot->e11*tri->v0.y + rot->e12*tri->v0.z;
        float wz0 = pos->z + rot->e20*tri->v0.x + rot->e21*tri->v0.y + rot->e22*tri->v0.z;

        float wx1 = pos->x + rot->e00*tri->v1.x + rot->e01*tri->v1.y + rot->e02*tri->v1.z;
        float wy1 = pos->y + rot->e10*tri->v1.x + rot->e11*tri->v1.y + rot->e12*tri->v1.z;
        float wz1 = pos->z + rot->e20*tri->v1.x + rot->e21*tri->v1.y + rot->e22*tri->v1.z;

        float wx2 = pos->x + rot->e00*tri->v2.x + rot->e01*tri->v2.y + rot->e02*tri->v2.z;
        float wy2 = pos->y + rot->e10*tri->v2.x + rot->e11*tri->v2.y + rot->e12*tri->v2.z;
        float wz2 = pos->z + rot->e20*tri->v2.x + rot->e21*tri->v2.y + rot->e22*tri->v2.z;

        // Draw the 3 edges of the triangle
        debugDrawLineVec3(wx0, wy0, wz0, wx1, wy1, wz1, color);
        debugDrawLineVec3(wx1, wy1, wz1, wx2, wy2, wz2, color);
        debugDrawLineVec3(wx2, wy2, wz2, wx0, wy0, wz0, color);
    }
}

/**
 * Draw face normals for static mesh geometry
 */
static void draw_mesh_normals(const OimoVec3 *pos, const OimoMat3 *rot,
                              OimoStaticMeshGeometry *mesh, uint16_t color)
{
    if (!pos || !rot || !mesh || !mesh->triangles || mesh->triangle_count <= 0) return;

    // Limit triangles to prevent slowdown
    int max_tris = mesh->triangle_count;
    if (max_tris > MAX_NORMAL_TRIANGLES) max_tris = MAX_NORMAL_TRIANGLES;

    for (int i = 0; i < max_tris; i++) {
        OimoTriangle *tri = &mesh->triangles[i];

        // Compute triangle center
        float cx = (tri->v0.x + tri->v1.x + tri->v2.x) / 3.0f;
        float cy = (tri->v0.y + tri->v1.y + tri->v2.y) / 3.0f;
        float cz = (tri->v0.z + tri->v1.z + tri->v2.z) / 3.0f;

        // Transform center to world space
        float wcx = pos->x + rot->e00*cx + rot->e01*cy + rot->e02*cz;
        float wcy = pos->y + rot->e10*cx + rot->e11*cy + rot->e12*cz;
        float wcz = pos->z + rot->e20*cx + rot->e21*cy + rot->e22*cz;

        // Transform normal to world space (rotation only)
        float wnx = rot->e00*tri->normal.x + rot->e01*tri->normal.y + rot->e02*tri->normal.z;
        float wny = rot->e10*tri->normal.x + rot->e11*tri->normal.y + rot->e12*tri->normal.z;
        float wnz = rot->e20*tri->normal.x + rot->e21*tri->normal.y + rot->e22*tri->normal.z;

        // Draw normal line (0.3 units long)
        float len = 0.3f;
        debugDrawLineVec3(wcx, wcy, wcz,
                          wcx + wnx * len, wcy + wny * len, wcz + wnz * len, color);
    }
}

// =============================================================================
// Body Drawing
// =============================================================================

/**
 * Quick frustum cull check using shape's AABB center and approximate radius.
 * Returns true if shape is potentially visible, false if definitely outside frustum.
 */
static inline bool shape_in_frustum(const OimoShape *shape)
{
    if (!g_frustum) return true;  // No frustum = draw everything

    // Use AABB center as sphere center
    const OimoAabb *aabb = &shape->_aabb;
    T3DVec3 center = {{
        (aabb->min.x + aabb->max.x) * 0.5f,
        (aabb->min.y + aabb->max.y) * 0.5f,
        (aabb->min.z + aabb->max.z) * 0.5f
    }};

    // Compute bounding sphere radius from AABB half-extents
    float hx = (aabb->max.x - aabb->min.x) * 0.5f;
    float hy = (aabb->max.y - aabb->min.y) * 0.5f;
    float hz = (aabb->max.z - aabb->min.z) * 0.5f;
    // Approximate: use max half-extent * sqrt(3) ≈ 1.73, but 2.0 is safer
    float maxH = hx;
    if (hy > maxH) maxH = hy;
    if (hz > maxH) maxH = hz;
    float radius = maxH * 1.8f;

    return t3d_frustum_vs_sphere(g_frustum, &center, radius);
}

/**
 * Draw one physics body with all shapes
 */
static void draw_body(OimoRigidBody *body)
{
    if (!body) return;

    uint16_t color;
    if (body->_type == OIMO_RIGID_BODY_STATIC) {
        color = g_debug.colors.wireframe_static;
    } else if (body->_sleeping) {
        color = g_debug.colors.wireframe_sleeping;
    } else {
        color = g_debug.colors.wireframe_active;
    }

    // Iterate shapes with strict safety limit
    OimoShape *shape = body->_shapeList;
    int shape_count = 0;
    while (shape && shape_count < MAX_SHAPES_PER_BODY) {
        if (!shape->_geom) {
            shape = shape->_next;
            shape_count++;
            continue;
        }

        // Frustum cull: skip shapes outside view frustum
        if (!shape_in_frustum(shape)) {
            shape = shape->_next;
            shape_count++;
            continue;
        }

        OimoVec3 pos = shape->_transform.position;
        OimoMat3 rot = shape->_transform.rotation;

        // Draw AABB if enabled
        if (g_debug.mode & PHYSICS_DEBUG_AABB) {
            draw_aabb(&shape->_aabb, g_debug.colors.aabb);
        }

        // Draw wireframe if enabled
        if (g_debug.mode & PHYSICS_DEBUG_WIREFRAME) {
            switch (shape->_geom->type) {
                case OIMO_GEOMETRY_BOX: {
                    OimoBoxGeometry *box = (OimoBoxGeometry*)shape->_geom;
                    draw_box(&pos, &rot,
                             box->half_extents.x, box->half_extents.y, box->half_extents.z, color);
                    break;
                }
                case OIMO_GEOMETRY_SPHERE: {
                    OimoSphereGeometry *sphere = (OimoSphereGeometry*)shape->_geom;
                    draw_sphere(&pos, &rot, sphere->radius, color);
                    break;
                }
                case OIMO_GEOMETRY_CAPSULE: {
                    OimoCapsuleGeometry *capsule = (OimoCapsuleGeometry*)shape->_geom;
                    draw_capsule(&pos, &rot, capsule->radius, capsule->halfHeight, color);
                    break;
                }
                case OIMO_GEOMETRY_STATIC_MESH: {
                    OimoStaticMeshGeometry *mesh = (OimoStaticMeshGeometry*)shape->_geom;
                    draw_static_mesh(&pos, &rot, mesh, color);
                    break;
                }
                default:
                    break;
            }
        }

        // Draw face normals if enabled
        if (g_debug.mode & PHYSICS_DEBUG_NORMALS) {
            uint16_t normal_color = g_debug.colors.face_normal;
            switch (shape->_geom->type) {
                case OIMO_GEOMETRY_BOX: {
                    // Draw 6 face normals for box
                    OimoBoxGeometry *box = (OimoBoxGeometry*)shape->_geom;
                    float len = 0.3f;
                    // +X face
                    float fx = pos.x + rot.e00 * box->half_extents.x;
                    float fy = pos.y + rot.e10 * box->half_extents.x;
                    float fz = pos.z + rot.e20 * box->half_extents.x;
                    debugDrawLineVec3(fx, fy, fz, fx + rot.e00 * len, fy + rot.e10 * len, fz + rot.e20 * len, normal_color);
                    // -X face
                    fx = pos.x - rot.e00 * box->half_extents.x;
                    fy = pos.y - rot.e10 * box->half_extents.x;
                    fz = pos.z - rot.e20 * box->half_extents.x;
                    debugDrawLineVec3(fx, fy, fz, fx - rot.e00 * len, fy - rot.e10 * len, fz - rot.e20 * len, normal_color);
                    // +Y face
                    fx = pos.x + rot.e01 * box->half_extents.y;
                    fy = pos.y + rot.e11 * box->half_extents.y;
                    fz = pos.z + rot.e21 * box->half_extents.y;
                    debugDrawLineVec3(fx, fy, fz, fx + rot.e01 * len, fy + rot.e11 * len, fz + rot.e21 * len, normal_color);
                    // -Y face
                    fx = pos.x - rot.e01 * box->half_extents.y;
                    fy = pos.y - rot.e11 * box->half_extents.y;
                    fz = pos.z - rot.e21 * box->half_extents.y;
                    debugDrawLineVec3(fx, fy, fz, fx - rot.e01 * len, fy - rot.e11 * len, fz - rot.e21 * len, normal_color);
                    // +Z face
                    fx = pos.x + rot.e02 * box->half_extents.z;
                    fy = pos.y + rot.e12 * box->half_extents.z;
                    fz = pos.z + rot.e22 * box->half_extents.z;
                    debugDrawLineVec3(fx, fy, fz, fx + rot.e02 * len, fy + rot.e12 * len, fz + rot.e22 * len, normal_color);
                    // -Z face
                    fx = pos.x - rot.e02 * box->half_extents.z;
                    fy = pos.y - rot.e12 * box->half_extents.z;
                    fz = pos.z - rot.e22 * box->half_extents.z;
                    debugDrawLineVec3(fx, fy, fz, fx - rot.e02 * len, fy - rot.e12 * len, fz - rot.e22 * len, normal_color);
                    break;
                }
                case OIMO_GEOMETRY_SPHERE: {
                    // Draw 6 surface normals for sphere (along rotated local axes)
                    OimoSphereGeometry *sphere = (OimoSphereGeometry*)shape->_geom;
                    float r = sphere->radius;
                    float len = 0.3f;
                    // +X axis (rotated)
                    float sx = pos.x + rot.e00 * r;
                    float sy = pos.y + rot.e10 * r;
                    float sz = pos.z + rot.e20 * r;
                    debugDrawLineVec3(sx, sy, sz, sx + rot.e00 * len, sy + rot.e10 * len, sz + rot.e20 * len, normal_color);
                    // -X axis (rotated)
                    sx = pos.x - rot.e00 * r;
                    sy = pos.y - rot.e10 * r;
                    sz = pos.z - rot.e20 * r;
                    debugDrawLineVec3(sx, sy, sz, sx - rot.e00 * len, sy - rot.e10 * len, sz - rot.e20 * len, normal_color);
                    // +Y axis (rotated)
                    sx = pos.x + rot.e01 * r;
                    sy = pos.y + rot.e11 * r;
                    sz = pos.z + rot.e21 * r;
                    debugDrawLineVec3(sx, sy, sz, sx + rot.e01 * len, sy + rot.e11 * len, sz + rot.e21 * len, normal_color);
                    // -Y axis (rotated)
                    sx = pos.x - rot.e01 * r;
                    sy = pos.y - rot.e11 * r;
                    sz = pos.z - rot.e21 * r;
                    debugDrawLineVec3(sx, sy, sz, sx - rot.e01 * len, sy - rot.e11 * len, sz - rot.e21 * len, normal_color);
                    // +Z axis (rotated)
                    sx = pos.x + rot.e02 * r;
                    sy = pos.y + rot.e12 * r;
                    sz = pos.z + rot.e22 * r;
                    debugDrawLineVec3(sx, sy, sz, sx + rot.e02 * len, sy + rot.e12 * len, sz + rot.e22 * len, normal_color);
                    // -Z axis (rotated)
                    sx = pos.x - rot.e02 * r;
                    sy = pos.y - rot.e12 * r;
                    sz = pos.z - rot.e22 * r;
                    debugDrawLineVec3(sx, sy, sz, sx - rot.e02 * len, sy - rot.e12 * len, sz - rot.e22 * len, normal_color);
                    break;
                }
                case OIMO_GEOMETRY_CAPSULE: {
                    // Draw normals at top/bottom caps and around cylinder
                    OimoCapsuleGeometry *capsule = (OimoCapsuleGeometry*)shape->_geom;
                    float r = capsule->radius;
                    float hh = capsule->halfHeight;
                    float len = 0.3f;
                    // Top cap normal (up direction)
                    float tx = pos.x + rot.e01 * (hh + r);
                    float ty = pos.y + rot.e11 * (hh + r);
                    float tz = pos.z + rot.e21 * (hh + r);
                    debugDrawLineVec3(tx, ty, tz, tx + rot.e01 * len, ty + rot.e11 * len, tz + rot.e21 * len, normal_color);
                    // Bottom cap normal (-up direction)
                    float bx = pos.x - rot.e01 * (hh + r);
                    float by = pos.y - rot.e11 * (hh + r);
                    float bz = pos.z - rot.e21 * (hh + r);
                    debugDrawLineVec3(bx, by, bz, bx - rot.e01 * len, by - rot.e11 * len, bz - rot.e21 * len, normal_color);
                    // Side normals (+X, -X, +Z, -Z in local space)
                    debugDrawLineVec3(pos.x + rot.e00 * r, pos.y + rot.e10 * r, pos.z + rot.e20 * r,
                                      pos.x + rot.e00 * (r + len), pos.y + rot.e10 * (r + len), pos.z + rot.e20 * (r + len), normal_color);
                    debugDrawLineVec3(pos.x - rot.e00 * r, pos.y - rot.e10 * r, pos.z - rot.e20 * r,
                                      pos.x - rot.e00 * (r + len), pos.y - rot.e10 * (r + len), pos.z - rot.e20 * (r + len), normal_color);
                    debugDrawLineVec3(pos.x + rot.e02 * r, pos.y + rot.e12 * r, pos.z + rot.e22 * r,
                                      pos.x + rot.e02 * (r + len), pos.y + rot.e12 * (r + len), pos.z + rot.e22 * (r + len), normal_color);
                    debugDrawLineVec3(pos.x - rot.e02 * r, pos.y - rot.e12 * r, pos.z - rot.e22 * r,
                                      pos.x - rot.e02 * (r + len), pos.y - rot.e12 * (r + len), pos.z - rot.e22 * (r + len), normal_color);
                    break;
                }
                case OIMO_GEOMETRY_STATIC_MESH: {
                    OimoStaticMeshGeometry *mesh = (OimoStaticMeshGeometry*)shape->_geom;
                    draw_mesh_normals(&pos, &rot, mesh, normal_color);
                    break;
                }
                default:
                    break;
            }
        }

        // Draw axes gizmo if enabled (per-shape)
        if (g_debug.mode & PHYSICS_DEBUG_AXES) {
            draw_axes(&pos, &rot, 0.5f);
        }

        shape = shape->_next;
        shape_count++;
    }
}

// =============================================================================
// Public API
// =============================================================================

void physics_debug_init(void)
{
    // Clear all state
    g_debug.mode = PHYSICS_DEBUG_NONE;
    g_debug.enabled = false;
    g_lines_this_frame = 0;
    g_screen_w = 0;
    g_screen_h = 0;
    g_viewport = NULL;
    g_frustum = NULL;
    g_rdp_mode_set = false;

    // Default colors (bright, easily visible)
    g_debug.colors.wireframe_active   = RGBA5551(0, 31, 0);   // Green
    g_debug.colors.wireframe_sleeping = RGBA5551(16, 16, 16); // Gray
    g_debug.colors.wireframe_static   = RGBA5551(31, 31, 0);  // Yellow
    g_debug.colors.aabb               = RGBA5551(31, 16, 0);  // Orange
    g_debug.colors.contact_point      = RGBA5551(31, 0, 0);   // Red
    g_debug.colors.contact_normal     = RGBA5551(31, 0, 31);  // Magenta
    g_debug.colors.face_normal        = RGBA5551(0, 31, 31);  // Cyan
    g_debug.colors.axis_x             = RGBA5551(31, 0, 0);   // Red
    g_debug.colors.axis_y             = RGBA5551(0, 31, 0);   // Green
    g_debug.colors.axis_z             = RGBA5551(0, 0, 31);   // Blue

    // Pre-compute circle LUT
    init_circle_lut();
}

void physics_debug_set_mode(PhysicsDebugMode mode)
{
    g_debug.mode = mode;
}

void physics_debug_enable(bool enabled)
{
    g_debug.enabled = enabled;
}

bool physics_debug_is_enabled(void)
{
    return g_debug.enabled;
}

PhysicsDebugMode physics_debug_get_mode(void)
{
    return g_debug.mode;
}

void physics_debug_draw(T3DViewport *viewport, OimoWorld *world)
{
    // Early out checks
    if (!g_debug.enabled || g_debug.mode == PHYSICS_DEBUG_NONE) return;
    if (!viewport || !world) return;

    // Reset per-frame state
    g_lines_this_frame = 0;
    g_viewport = viewport;
    g_frustum = &viewport->viewFrustum;  // Cache frustum for shape culling
    g_screen_w = display_get_width();
    g_screen_h = display_get_height();

    // Validate screen dimensions (sanity check)
    if (g_screen_w == 0 || g_screen_h == 0 ||
        g_screen_w > MAX_SCREEN_WIDTH || g_screen_h > MAX_SCREEN_HEIGHT) {
        g_viewport = NULL;
        g_frustum = NULL;
        return;
    }

    // Set up RDP mode for flat-colored triangle drawing
    rdpq_sync_pipe();
    rdpq_set_mode_standard();
    rdpq_mode_combiner(RDPQ_COMBINER_FLAT);
    rdpq_mode_blender(0);  // Disable blending for solid lines

    // Draw bodies with strict limit
    OimoRigidBody *body = world->_rigidBodyList;
    int body_count = 0;
    while (body && body_count < MAX_BODIES_PER_FRAME) {
        draw_body(body);
        body = body->_next;
        body_count++;
    }

    // Draw contact points if enabled
    if (g_debug.mode & PHYSICS_DEBUG_CONTACTS) {
        OimoContact *contact = world->_contactManager._contactList;
        int contact_count = 0;

        while (contact && contact_count < MAX_CONTACTS_PER_FRAME) {
            if (contact->_touching) {
                OimoManifold *manifold = &contact->_manifold;
                if (manifold) {
                    int numPoints = manifold->_numPoints;
                    if (numPoints < 0) numPoints = 0;
                    if (numPoints > MAX_CONTACT_POINTS) numPoints = MAX_CONTACT_POINTS;

                    for (int i = 0; i < numPoints; i++) {
                        OimoManifoldPoint *mp = &manifold->_points[i];
                        if (!mp) continue;

                        // Average contact position
                        float px = (mp->_pos1.x + mp->_pos2.x) * 0.5f;
                        float py = (mp->_pos1.y + mp->_pos2.y) * 0.5f;
                        float pz = (mp->_pos1.z + mp->_pos2.z) * 0.5f;

                        // Skip invalid positions
                        if (!is_valid_float(px) || !is_valid_float(py) || !is_valid_float(pz)) {
                            continue;
                        }

                        // Draw contact normal
                        float nx = manifold->_normal.x;
                        float ny = manifold->_normal.y;
                        float nz = manifold->_normal.z;
                        float len = 0.3f;
                        debugDrawLineVec3(px, py, pz,
                                          px + nx * len, py + ny * len, pz + nz * len,
                                          g_debug.colors.contact_normal);

                        // Draw small cross at contact point
                        float cross = 0.05f;
                        debugDrawLineVec3(px - cross, py, pz, px + cross, py, pz, g_debug.colors.contact_point);
                        debugDrawLineVec3(px, py - cross, pz, px, py + cross, pz, g_debug.colors.contact_point);
                        debugDrawLineVec3(px, py, pz - cross, px, py, pz + cross, g_debug.colors.contact_point);
                    }
                }
            }
            contact = contact->_next;
            contact_count++;
        }
    }

    // Sync before finishing debug drawing
    rdpq_sync_pipe();

    // Clear per-frame pointers
    g_viewport = NULL;
    g_frustum = NULL;
}
