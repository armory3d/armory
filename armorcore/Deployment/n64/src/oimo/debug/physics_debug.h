/**
 * Physics Debug Drawing for N64
 * Hardware-accelerated debug visualization for OimoPhysics
 * Uses RDP triangles for line rendering via T3D viewport projection
 *
 * Features:
 * - Collider wireframes (box, sphere, capsule)
 * - AABBs (axis-aligned bounding boxes)
 * - Contact points and normals
 * - Body axes/gizmos
 */

#pragma once

#include <libdragon.h>
#include <stdint.h>
#include <t3d/t3d.h>
#include "../oimo.h"

#ifdef __cplusplus
extern "C" {
#endif

// Debug draw mode flags (can be combined with |)
// Values match Blender's arm_physics_dbg_draw_* settings exactly
typedef enum PhysicsDebugMode {
    PHYSICS_DEBUG_NONE              = 0,
    PHYSICS_DEBUG_WIREFRAME         = (1 << 0),   // Collider wireframes
    PHYSICS_DEBUG_AABB              = (1 << 1),   // Axis-aligned bounding boxes
    PHYSICS_DEBUG_CONTACTS          = (1 << 3),   // Contact points (Blender uses bit 3)
    PHYSICS_DEBUG_CONSTRAINTS       = (1 << 11),  // Constraints (not implemented on N64)
    PHYSICS_DEBUG_CONSTRAINT_LIMITS = (1 << 12),  // Constraint limits (not implemented)
    PHYSICS_DEBUG_NORMALS           = (1 << 14),  // Face normals
    PHYSICS_DEBUG_AXES              = (1 << 15),  // Body coordinate axes/gizmos
    PHYSICS_DEBUG_RAYCASTS          = (1 << 16),  // Raycasts (not implemented)
    PHYSICS_DEBUG_ALL               = 0x1C80B     // All implemented modes
} PhysicsDebugMode;

// Debug draw colors (RGBA5551 format, converted to color_t for RDP)
typedef struct PhysicsDebugColors {
    uint16_t wireframe_active;   // Active dynamic bodies (green)
    uint16_t wireframe_sleeping; // Sleeping bodies (gray)
    uint16_t wireframe_static;   // Static bodies (yellow)
    uint16_t aabb;               // AABB outlines (orange)
    uint16_t contact_point;      // Contact point markers (red)
    uint16_t contact_normal;     // Contact normal lines (magenta)
    uint16_t face_normal;        // Face normals (cyan)
    uint16_t axis_x;             // X axis (red)
    uint16_t axis_y;             // Y axis (green)
    uint16_t axis_z;             // Z axis (blue)
} PhysicsDebugColors;

// Debug draw state
typedef struct PhysicsDebugDraw {
    PhysicsDebugMode mode;
    PhysicsDebugColors colors;
    bool enabled;
} PhysicsDebugDraw;

// =============================================================================
// Public API
// =============================================================================

/**
 * Initialize debug draw system with default colors
 */
void physics_debug_init(void);

/**
 * Set which debug visualizations are active
 * @param mode Combination of PhysicsDebugMode flags
 */
void physics_debug_set_mode(PhysicsDebugMode mode);

/**
 * Enable or disable debug drawing entirely
 */
void physics_debug_enable(bool enabled);

/**
 * Check if debug drawing is enabled
 */
bool physics_debug_is_enabled(void);

/**
 * Get current debug mode
 */
PhysicsDebugMode physics_debug_get_mode(void);

/**
 * Main debug draw function - draws all enabled debug visualization
 *
 * Call this while RDP is attached (before rdpq_detach_show).
 * Uses RDP hardware triangles for line rendering.
 *
 * @param viewport  T3D viewport (for 3D->2D projection)
 * @param world     Physics world to visualize
 */
void physics_debug_draw(T3DViewport* viewport, OimoWorld* world);

#ifdef __cplusplus
}
#endif

