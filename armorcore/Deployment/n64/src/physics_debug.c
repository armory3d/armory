/**
 * Physics Debug Drawing for N64
 * Uses T3D's viewport projection and CPU software line drawing
 * Based on tiny3d's debugDraw.h example approach
 */

#include "physics_debug.h"
#include <libdragon.h>
#include <t3d/t3d.h>
#include <math.h>

// Include geometry headers for type casts
#include "oimo/collision/geometry/box_geometry.h"
#include "oimo/collision/geometry/sphere_geometry.h"
#include "oimo/collision/geometry/capsule_geometry.h"
#include "oimo/collision/geometry/static_mesh_geometry.h"

// Global debug state
static PhysicsDebugDraw g_debug = {0};

// Pre-computed unit circle points for wireframe spheres/capsules
#define CIRCLE_SEGMENTS 8
static float circle_sin[CIRCLE_SEGMENTS + 1];
static float circle_cos[CIRCLE_SEGMENTS + 1];
static bool circle_lut_initialized = false;

// RGBA5551 color helpers
#define RGBA5551(r, g, b) (((r) << 11) | ((g) << 6) | ((b) << 1) | 1)

/**
 * Initialize circle lookup tables
 */
static void init_circle_lut(void) {
    if (circle_lut_initialized) return;

    for (int i = 0; i <= CIRCLE_SEGMENTS; i++) {
        float angle = (float)i / CIRCLE_SEGMENTS * 2.0f * 3.14159265f;
        circle_sin[i] = sinf(angle);
        circle_cos[i] = cosf(angle);
    }
    circle_lut_initialized = true;
}

/**
 * Draw a 2D line directly to framebuffer (Bresenham-style)
 * Based on tiny3d's debugDrawLine
 */
static void draw_line_2d(uint16_t* fb, int px0, int py0, int px1, int py1, uint16_t color) {
    uint32_t width = display_get_width();
    uint32_t height = display_get_height();

    // Reject lines way off screen
    if ((px0 < -200 || px0 > (int)width + 200) && (px1 < -200 || px1 > (int)width + 200)) return;
    if ((py0 < -200 || py0 > (int)height + 200) && (py1 < -200 || py1 > (int)height + 200)) return;

    float pos[2] = {(float)px0, (float)py0};
    int dx = px1 - px0;
    int dy = py1 - py0;
    int steps = abs(dx) > abs(dy) ? abs(dx) : abs(dy);
    if (steps <= 0) return;

    float xInc = (float)dx / (float)steps;
    float yInc = (float)dy / (float)steps;

    for (int i = 0; i < steps; ++i) {
        int x = (int)pos[0];
        int y = (int)pos[1];
        if (y >= 0 && y < (int)height && x >= 0 && x < (int)width) {
            fb[y * width + x] = color;
        }
        pos[0] += xInc;
        pos[1] += yInc;
    }
}

/**
 * Draw a 3D line using T3D viewport projection
 */
static void draw_line_3d(uint16_t* fb, T3DViewport* vp,
                         float x0, float y0, float z0,
                         float x1, float y1, float z1, uint16_t color) {
    T3DVec3 p0_world = {{x0, y0, z0}};
    T3DVec3 p1_world = {{x1, y1, z1}};
    T3DVec3 p0_screen, p1_screen;

    t3d_viewport_calc_viewspace_pos(vp, &p0_screen, &p0_world);
    t3d_viewport_calc_viewspace_pos(vp, &p1_screen, &p1_world);

    // Z component is depth - reject if both points behind camera
    if (p0_screen.v[2] < 1.0f && p1_screen.v[2] < 1.0f) {
        draw_line_2d(fb, (int)p0_screen.v[0], (int)p0_screen.v[1],
                     (int)p1_screen.v[0], (int)p1_screen.v[1], color);
    }
}

/**
 * Draw a box wireframe
 */
static void draw_box_wireframe(uint16_t* fb, T3DViewport* vp,
                               const OimoVec3* center, const OimoMat3* rot,
                               float hx, float hy, float hz, uint16_t color) {
    // 8 corners in local space
    float corners[8][3] = {
        {-hx, -hy, -hz}, {+hx, -hy, -hz}, {+hx, +hy, -hz}, {-hx, +hy, -hz},
        {-hx, -hy, +hz}, {+hx, -hy, +hz}, {+hx, +hy, +hz}, {-hx, +hy, +hz}
    };

    // Transform to world space
    float world[8][3];
    for (int i = 0; i < 8; i++) {
        float lx = corners[i][0], ly = corners[i][1], lz = corners[i][2];
        world[i][0] = center->x + rot->e00*lx + rot->e01*ly + rot->e02*lz;
        world[i][1] = center->y + rot->e10*lx + rot->e11*ly + rot->e12*lz;
        world[i][2] = center->z + rot->e20*lx + rot->e21*ly + rot->e22*lz;
    }

    // 12 edges
    int edges[12][2] = {
        {0,1}, {1,2}, {2,3}, {3,0},  // bottom
        {4,5}, {5,6}, {6,7}, {7,4},  // top
        {0,4}, {1,5}, {2,6}, {3,7}   // verticals
    };

    for (int i = 0; i < 12; i++) {
        int a = edges[i][0], b = edges[i][1];
        draw_line_3d(fb, vp, world[a][0], world[a][1], world[a][2],
                     world[b][0], world[b][1], world[b][2], color);
    }
}

/**
 * Draw a sphere wireframe (3 orthogonal circles aligned to body rotation)
 */
static void draw_sphere_wireframe(uint16_t* fb, T3DViewport* vp,
                                  const OimoVec3* center, const OimoMat3* rot,
                                  float radius, uint16_t color) {
    init_circle_lut();

    // Get rotation axes
    OimoVec3 axisX = { rot->e00, rot->e10, rot->e20 };  // Local X axis (right)
    OimoVec3 axisY = { rot->e01, rot->e11, rot->e21 };  // Local Y axis (up)
    OimoVec3 axisZ = { rot->e02, rot->e12, rot->e22 };  // Local Z axis (forward)

    // XY plane circle (around Z axis)
    for (int i = 0; i < CIRCLE_SEGMENTS; i++) {
        float c0 = circle_cos[i], s0 = circle_sin[i];
        float c1 = circle_cos[i+1], s1 = circle_sin[i+1];
        float x0 = center->x + radius * (c0 * axisX.x + s0 * axisY.x);
        float y0 = center->y + radius * (c0 * axisX.y + s0 * axisY.y);
        float z0 = center->z + radius * (c0 * axisX.z + s0 * axisY.z);
        float x1 = center->x + radius * (c1 * axisX.x + s1 * axisY.x);
        float y1 = center->y + radius * (c1 * axisX.y + s1 * axisY.y);
        float z1 = center->z + radius * (c1 * axisX.z + s1 * axisY.z);
        draw_line_3d(fb, vp, x0, y0, z0, x1, y1, z1, color);
    }

    // XZ plane circle (around Y axis)
    for (int i = 0; i < CIRCLE_SEGMENTS; i++) {
        float c0 = circle_cos[i], s0 = circle_sin[i];
        float c1 = circle_cos[i+1], s1 = circle_sin[i+1];
        float x0 = center->x + radius * (c0 * axisX.x + s0 * axisZ.x);
        float y0 = center->y + radius * (c0 * axisX.y + s0 * axisZ.y);
        float z0 = center->z + radius * (c0 * axisX.z + s0 * axisZ.z);
        float x1 = center->x + radius * (c1 * axisX.x + s1 * axisZ.x);
        float y1 = center->y + radius * (c1 * axisX.y + s1 * axisZ.y);
        float z1 = center->z + radius * (c1 * axisX.z + s1 * axisZ.z);
        draw_line_3d(fb, vp, x0, y0, z0, x1, y1, z1, color);
    }

    // YZ plane circle (around X axis)
    for (int i = 0; i < CIRCLE_SEGMENTS; i++) {
        float c0 = circle_cos[i], s0 = circle_sin[i];
        float c1 = circle_cos[i+1], s1 = circle_sin[i+1];
        float x0 = center->x + radius * (c0 * axisY.x + s0 * axisZ.x);
        float y0 = center->y + radius * (c0 * axisY.y + s0 * axisZ.y);
        float z0 = center->z + radius * (c0 * axisY.z + s0 * axisZ.z);
        float x1 = center->x + radius * (c1 * axisY.x + s1 * axisZ.x);
        float y1 = center->y + radius * (c1 * axisY.y + s1 * axisZ.y);
        float z1 = center->z + radius * (c1 * axisY.z + s1 * axisZ.z);
        draw_line_3d(fb, vp, x0, y0, z0, x1, y1, z1, color);
    }
}

/**
 * Draw a capsule wireframe
 */
static void draw_capsule_wireframe(uint16_t* fb, T3DViewport* vp,
                                   const OimoVec3* center, const OimoMat3* rot,
                                   float radius, float halfHeight, uint16_t color) {
    init_circle_lut();

    // Get capsule axes (Y-aligned in local space)
    OimoVec3 up = { rot->e01, rot->e11, rot->e21 };
    OimoVec3 right = { rot->e00, rot->e10, rot->e20 };
    OimoVec3 forward = { rot->e02, rot->e12, rot->e22 };

    // Top and bottom cap centers
    OimoVec3 top = {
        center->x + up.x * halfHeight,
        center->y + up.y * halfHeight,
        center->z + up.z * halfHeight
    };
    OimoVec3 bottom = {
        center->x - up.x * halfHeight,
        center->y - up.y * halfHeight,
        center->z - up.z * halfHeight
    };

    // Draw circles at top and bottom
    for (int i = 0; i < CIRCLE_SEGMENTS; i++) {
        float c0 = circle_cos[i], s0 = circle_sin[i];
        float c1 = circle_cos[i+1], s1 = circle_sin[i+1];

        // Top circle
        float tx0 = top.x + radius * (right.x * c0 + forward.x * s0);
        float ty0 = top.y + radius * (right.y * c0 + forward.y * s0);
        float tz0 = top.z + radius * (right.z * c0 + forward.z * s0);
        float tx1 = top.x + radius * (right.x * c1 + forward.x * s1);
        float ty1 = top.y + radius * (right.y * c1 + forward.y * s1);
        float tz1 = top.z + radius * (right.z * c1 + forward.z * s1);
        draw_line_3d(fb, vp, tx0, ty0, tz0, tx1, ty1, tz1, color);

        // Bottom circle
        float bx0 = bottom.x + radius * (right.x * c0 + forward.x * s0);
        float by0 = bottom.y + radius * (right.y * c0 + forward.y * s0);
        float bz0 = bottom.z + radius * (right.z * c0 + forward.z * s0);
        float bx1 = bottom.x + radius * (right.x * c1 + forward.x * s1);
        float by1 = bottom.y + radius * (right.y * c1 + forward.y * s1);
        float bz1 = bottom.z + radius * (right.z * c1 + forward.z * s1);
        draw_line_3d(fb, vp, bx0, by0, bz0, bx1, by1, bz1, color);
    }

    // Draw 4 vertical lines
    for (int i = 0; i < 4; i++) {
        int idx = i * (CIRCLE_SEGMENTS / 4);
        float c = circle_cos[idx], s = circle_sin[idx];
        float px = radius * (right.x * c + forward.x * s);
        float py = radius * (right.y * c + forward.y * s);
        float pz = radius * (right.z * c + forward.z * s);
        draw_line_3d(fb, vp, top.x + px, top.y + py, top.z + pz,
                     bottom.x + px, bottom.y + py, bottom.z + pz, color);
    }
}

/**
 * Draw a static mesh wireframe (all triangle edges)
 */
static void draw_mesh_wireframe(uint16_t* fb, T3DViewport* vp,
                                const OimoVec3* pos, const OimoMat3* rot,
                                OimoStaticMeshGeometry* mesh, uint16_t color) {
    // Transform and draw each triangle's edges
    for (int i = 0; i < mesh->triangle_count; i++) {
        OimoTriangle* tri = &mesh->triangles[i];

        // Transform vertices to world space
        // v_world = pos + rot * v_local
        OimoVec3 v0_local = tri->v0;
        OimoVec3 v1_local = tri->v1;
        OimoVec3 v2_local = tri->v2;

        // Apply rotation (row-major multiply)
        OimoVec3 v0_rot = {
            rot->e00 * v0_local.x + rot->e01 * v0_local.y + rot->e02 * v0_local.z,
            rot->e10 * v0_local.x + rot->e11 * v0_local.y + rot->e12 * v0_local.z,
            rot->e20 * v0_local.x + rot->e21 * v0_local.y + rot->e22 * v0_local.z
        };
        OimoVec3 v1_rot = {
            rot->e00 * v1_local.x + rot->e01 * v1_local.y + rot->e02 * v1_local.z,
            rot->e10 * v1_local.x + rot->e11 * v1_local.y + rot->e12 * v1_local.z,
            rot->e20 * v1_local.x + rot->e21 * v1_local.y + rot->e22 * v1_local.z
        };
        OimoVec3 v2_rot = {
            rot->e00 * v2_local.x + rot->e01 * v2_local.y + rot->e02 * v2_local.z,
            rot->e10 * v2_local.x + rot->e11 * v2_local.y + rot->e12 * v2_local.z,
            rot->e20 * v2_local.x + rot->e21 * v2_local.y + rot->e22 * v2_local.z
        };

        // Translate to world position
        OimoVec3 v0 = { pos->x + v0_rot.x, pos->y + v0_rot.y, pos->z + v0_rot.z };
        OimoVec3 v1 = { pos->x + v1_rot.x, pos->y + v1_rot.y, pos->z + v1_rot.z };
        OimoVec3 v2 = { pos->x + v2_rot.x, pos->y + v2_rot.y, pos->z + v2_rot.z };

        // Draw the 3 edges of the triangle
        draw_line_3d(fb, vp, v0.x, v0.y, v0.z, v1.x, v1.y, v1.z, color);
        draw_line_3d(fb, vp, v1.x, v1.y, v1.z, v2.x, v2.y, v2.z, color);
        draw_line_3d(fb, vp, v2.x, v2.y, v2.z, v0.x, v0.y, v0.z, color);
    }
}

/**
 * Draw an AABB wireframe
 */
static void draw_aabb(uint16_t* fb, T3DViewport* vp, const OimoAabb* aabb, uint16_t color) {
    float minX = aabb->min.x, minY = aabb->min.y, minZ = aabb->min.z;
    float maxX = aabb->max.x, maxY = aabb->max.y, maxZ = aabb->max.z;

    // Bottom face
    draw_line_3d(fb, vp, minX, minY, minZ, maxX, minY, minZ, color);
    draw_line_3d(fb, vp, maxX, minY, minZ, maxX, minY, maxZ, color);
    draw_line_3d(fb, vp, maxX, minY, maxZ, minX, minY, maxZ, color);
    draw_line_3d(fb, vp, minX, minY, maxZ, minX, minY, minZ, color);

    // Top face
    draw_line_3d(fb, vp, minX, maxY, minZ, maxX, maxY, minZ, color);
    draw_line_3d(fb, vp, maxX, maxY, minZ, maxX, maxY, maxZ, color);
    draw_line_3d(fb, vp, maxX, maxY, maxZ, minX, maxY, maxZ, color);
    draw_line_3d(fb, vp, minX, maxY, maxZ, minX, maxY, minZ, color);

    // Vertical edges
    draw_line_3d(fb, vp, minX, minY, minZ, minX, maxY, minZ, color);
    draw_line_3d(fb, vp, maxX, minY, minZ, maxX, maxY, minZ, color);
    draw_line_3d(fb, vp, maxX, minY, maxZ, maxX, maxY, maxZ, color);
    draw_line_3d(fb, vp, minX, minY, maxZ, minX, maxY, maxZ, color);
}

/**
 * Draw body coordinate axes
 */
static void draw_body_axes(uint16_t* fb, T3DViewport* vp,
                           const OimoVec3* center, const OimoMat3* rot, float length) {
    // X axis (red)
    draw_line_3d(fb, vp, center->x, center->y, center->z,
                 center->x + rot->e00 * length,
                 center->y + rot->e10 * length,
                 center->z + rot->e20 * length, g_debug.colors.axis_x);

    // Y axis (green)
    draw_line_3d(fb, vp, center->x, center->y, center->z,
                 center->x + rot->e01 * length,
                 center->y + rot->e11 * length,
                 center->z + rot->e21 * length, g_debug.colors.axis_y);

    // Z axis (blue)
    draw_line_3d(fb, vp, center->x, center->y, center->z,
                 center->x + rot->e02 * length,
                 center->y + rot->e12 * length,
                 center->z + rot->e22 * length, g_debug.colors.axis_z);
}

/**
 * Draw a contact point marker (small cross)
 */
static void draw_contact_point(uint16_t* fb, T3DViewport* vp, const OimoVec3* pos, uint16_t color) {
    T3DVec3 world = {{pos->x, pos->y, pos->z}};
    T3DVec3 screen;
    t3d_viewport_calc_viewspace_pos(vp, &screen, &world);

    if (screen.v[2] < 1.0f) {
        int sx = (int)screen.v[0];
        int sy = (int)screen.v[1];
        uint32_t width = display_get_width();
        uint32_t height = display_get_height();

        // Draw a small cross
        for (int i = -2; i <= 2; i++) {
            if (sy >= 0 && sy < (int)height) {
                if (sx + i >= 0 && sx + i < (int)width) fb[sy * width + sx + i] = color;
            }
            if (sy + i >= 0 && sy + i < (int)height) {
                if (sx >= 0 && sx < (int)width) fb[(sy + i) * width + sx] = color;
            }
        }
    }
}

// =============================================================================
// Public API
// =============================================================================

void physics_debug_init(void) {
    g_debug.mode = PHYSICS_DEBUG_NONE;
    g_debug.enabled = false;

    // Default colors (RGBA5551)
    g_debug.colors.wireframe_active = RGBA5551(0, 31, 0);     // Green
    g_debug.colors.wireframe_sleeping = RGBA5551(16, 16, 16); // Gray
    g_debug.colors.wireframe_static = RGBA5551(31, 31, 0);    // Yellow
    g_debug.colors.aabb = RGBA5551(31, 16, 0);                // Orange
    g_debug.colors.contact_point = RGBA5551(31, 0, 0);        // Red
    g_debug.colors.contact_normal = RGBA5551(31, 0, 31);      // Magenta
    g_debug.colors.axis_x = RGBA5551(31, 0, 0);               // Red
    g_debug.colors.axis_y = RGBA5551(0, 31, 0);               // Green
    g_debug.colors.axis_z = RGBA5551(0, 0, 31);               // Blue

    init_circle_lut();
}

void physics_debug_set_mode(PhysicsDebugMode mode) {
    g_debug.mode = mode;
}

void physics_debug_enable(bool enabled) {
    g_debug.enabled = enabled;
}

bool physics_debug_is_enabled(void) {
    return g_debug.enabled;
}

PhysicsDebugMode physics_debug_get_mode(void) {
    return g_debug.mode;
}

/**
 * Draw debug visualization for a single rigid body
 */
static void draw_body(uint16_t* fb, T3DViewport* vp, OimoRigidBody* body) {
    // Determine color based on body state
    uint16_t color;
    if (body->_type == OIMO_RIGID_BODY_STATIC) {
        color = g_debug.colors.wireframe_static;
    } else if (body->_sleeping) {
        color = g_debug.colors.wireframe_sleeping;
    } else {
        color = g_debug.colors.wireframe_active;
    }

    // Draw each shape
    OimoShape* shape = body->_shapeList;
    while (shape) {
        // AABB
        if (g_debug.mode & PHYSICS_DEBUG_AABB) {
            draw_aabb(fb, vp, &shape->_aabb, g_debug.colors.aabb);
        }

        // Wireframe
        if (g_debug.mode & PHYSICS_DEBUG_WIREFRAME) {
            OimoVec3 pos = shape->_transform.position;
            OimoMat3 rot = shape->_transform.rotation;

            switch (shape->_geom->type) {
                case OIMO_GEOMETRY_BOX: {
                    OimoBoxGeometry* box = (OimoBoxGeometry*)shape->_geom;
                    draw_box_wireframe(fb, vp, &pos, &rot,
                                       box->half_extents.x, box->half_extents.y, box->half_extents.z,
                                       color);
                    break;
                }
                case OIMO_GEOMETRY_SPHERE: {
                    OimoSphereGeometry* sphere = (OimoSphereGeometry*)shape->_geom;
                    draw_sphere_wireframe(fb, vp, &pos, &rot, sphere->radius, color);
                    break;
                }
                case OIMO_GEOMETRY_CAPSULE: {
                    OimoCapsuleGeometry* capsule = (OimoCapsuleGeometry*)shape->_geom;
                    draw_capsule_wireframe(fb, vp, &pos, &rot,
                                           capsule->radius, capsule->halfHeight, color);
                    break;
                }
                case OIMO_GEOMETRY_STATIC_MESH: {
                    OimoStaticMeshGeometry* mesh = (OimoStaticMeshGeometry*)shape->_geom;
                    draw_mesh_wireframe(fb, vp, &pos, &rot, mesh, color);
                    break;
                }
                default:
                    break;
            }
        }

        // Body axes
        if (g_debug.mode & PHYSICS_DEBUG_AXES) {
            OimoVec3 pos = body->_transform.position;
            OimoMat3 rot = body->_transform.rotation;
            draw_body_axes(fb, vp, &pos, &rot, 0.5f);
        }

        shape = shape->_next;
    }
}

/**
 * Draw contact points and normals
 */
static void draw_contacts(uint16_t* fb, T3DViewport* vp, OimoWorld* world) {
    if (!(g_debug.mode & PHYSICS_DEBUG_CONTACTS)) return;

    OimoContact* contact = world->_contactManager._contactList;
    while (contact) {
        if (contact->_touching) {
            OimoManifold* manifold = &contact->_manifold;

            for (int i = 0; i < manifold->_numPoints; i++) {
                OimoManifoldPoint* mp = &manifold->_points[i];

                // Draw contact point (average of two positions)
                OimoVec3 pos = {
                    (mp->_pos1.x + mp->_pos2.x) * 0.5f,
                    (mp->_pos1.y + mp->_pos2.y) * 0.5f,
                    (mp->_pos1.z + mp->_pos2.z) * 0.5f
                };
                draw_contact_point(fb, vp, &pos, g_debug.colors.contact_point);

                // Draw contact normal
                draw_line_3d(fb, vp, pos.x, pos.y, pos.z,
                             pos.x + manifold->_normal.x * 0.3f,
                             pos.y + manifold->_normal.y * 0.3f,
                             pos.z + manifold->_normal.z * 0.3f,
                             g_debug.colors.contact_normal);
            }
        }
        contact = contact->_next;
    }
}

void physics_debug_draw(surface_t* surface, T3DViewport* viewport, OimoWorld* world) {
    if (!surface || !surface->buffer) return;
    if (!g_debug.enabled || g_debug.mode == PHYSICS_DEBUG_NONE) return;

    uint16_t* fb = (uint16_t*)surface->buffer;

    // Draw all bodies
    OimoRigidBody* body = world->_rigidBodyList;
    while (body) {
        draw_body(fb, viewport, body);
        body = body->_next;
    }

    // Draw contacts
    draw_contacts(fb, viewport, world);
}
