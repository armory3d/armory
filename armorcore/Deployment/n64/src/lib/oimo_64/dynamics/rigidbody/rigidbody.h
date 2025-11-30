#ifndef RIGIDBODY_H
#define RIGIDBODY_H

#include "../../common/Transform.h"
#include <stdbool.h>
#include <stdint.h>

// Forward declarations
typedef struct RigidBody RigidBody;
typedef struct Shape Shape;
typedef struct World World;

// =============================================================================
// Shape Types
// =============================================================================

typedef enum {
    SHAPE_SPHERE = 0,
    SHAPE_BOX = 1
} ShapeType;

// =============================================================================
// Rigid Body Types (matches Oimo)
// =============================================================================

typedef enum {
    RIGIDBODY_DYNAMIC = 0,   // Affected by forces and collisions
    RIGIDBODY_STATIC = 1,    // Never moves, infinite mass
    RIGIDBODY_KINEMATIC = 2  // Moves via setPosition, not forces
} RigidBodyType;

// =============================================================================
// Geometry Structures
// =============================================================================

typedef struct {
    float radius;
} SphereGeom;

typedef struct {
    Vec3 halfExtents;  // Half-widths along each axis
} BoxGeom;

typedef union {
    SphereGeom sphere;
    BoxGeom box;
} GeomData;

// =============================================================================
// Shape - Collision shape attached to a rigid body
// =============================================================================

struct Shape {
    ShapeType type;
    GeomData geom;

    // Local transform relative to body center
    Vec3 localPosition;
    Mat3 localRotation;

    // Computed world-space AABB (updated each frame)
    Vec3 aabbMin;
    Vec3 aabbMax;

    // Collision filtering
    uint16_t collisionGroup;  // What group this shape belongs to
    uint16_t collisionMask;   // What groups this shape collides with

    // Owner body
    RigidBody* body;

    // Linked list within body
    Shape* next;

    // User data
    void* userData;
};

// =============================================================================
// Mass Data
// =============================================================================

typedef struct {
    float mass;
    Vec3 localCenterOfMass;
    Mat3 localInertia;  // Inertia tensor in local space
} MassData;

// =============================================================================
// Contact Point
// =============================================================================

typedef struct {
    Vec3 position;       // Contact point in world space
    Vec3 normal;         // Contact normal (from body1 to body2)
    float penetration;   // Penetration depth (positive = overlapping)
} ContactPoint;

// =============================================================================
// Contact - Information about a collision between two bodies
// =============================================================================

typedef struct Contact {
    RigidBody* body1;
    RigidBody* body2;
    Shape* shape1;
    Shape* shape2;

    ContactPoint points[4];  // Up to 4 contact points (usually 1 for sphere)
    int numPoints;

    // For linked list in world
    struct Contact* next;
    struct Contact* prev;

    // State tracking
    bool isTouching;
    bool wasTouching;  // Previous frame
} Contact;

// =============================================================================
// Rigid Body
// =============================================================================

struct RigidBody {
    // Transform
    Transform transform;

    // Velocities
    Vec3 linearVel;
    Vec3 angularVel;

    // Forces accumulated this frame (cleared after integration)
    Vec3 force;
    Vec3 torque;

    // Mass properties
    float mass;
    float invMass;           // 1/mass (0 for static)
    Mat3 localInertia;       // Inertia tensor in local space
    Mat3 invLocalInertia;    // Inverse inertia in local space
    Mat3 invWorldInertia;    // Inverse inertia in world space (updated each step)

    // Damping (0-1, applied each step)
    float linearDamping;
    float angularDamping;

    // Gravity scale (0 = no gravity, 1 = normal, 2 = double, etc.)
    float gravityScale;

    // Rotation factor (scales angular velocity changes per axis)
    Vec3 rotationFactor;

    // Body type
    RigidBodyType type;

    // Shapes (linked list)
    Shape* shapeList;
    int numShapes;

    // Sleeping
    bool sleeping;
    bool autoSleep;
    float sleepTime;         // How long velocity has been below threshold

    // World linkage
    World* world;
    RigidBody* prev;
    RigidBody* next;

    // Contact list (contacts involving this body)
    Contact* contactList;
    int numContacts;

    // User data
    void* userData;
};

// =============================================================================
// Shape Functions
// =============================================================================

// Create shapes
Shape* shape_create_sphere(float radius);
Shape* shape_create_box(float halfX, float halfY, float halfZ);
Shape* shape_create_box_vec(const Vec3* halfExtents);

// Destroy shape
void shape_destroy(Shape* shape);

// Set collision filtering
void shape_set_collision_group(Shape* shape, uint16_t group);
void shape_set_collision_mask(Shape* shape, uint16_t mask);

// Set local transform
void shape_set_local_position(Shape* shape, const Vec3* pos);
void shape_set_local_rotation(Shape* shape, const Mat3* rot);

// Update world-space AABB
void shape_update_aabb(Shape* shape);

// Compute mass data for shape (density = mass per unit volume)
void shape_compute_mass(const Shape* shape, float density, MassData* out);

// =============================================================================
// RigidBody Functions
// =============================================================================

// Create/destroy
RigidBody* rigidbody_create(void);
void rigidbody_destroy(RigidBody* body);

// Type
void rigidbody_set_type(RigidBody* body, RigidBodyType type);
RigidBodyType rigidbody_get_type(const RigidBody* body);

// Transform
void rigidbody_get_position(const RigidBody* body, Vec3* out);
void rigidbody_set_position(RigidBody* body, const Vec3* pos);
void rigidbody_translate(RigidBody* body, const Vec3* translation);

void rigidbody_get_rotation(const RigidBody* body, Mat3* out);
void rigidbody_set_rotation(RigidBody* body, const Mat3* rot);
void rigidbody_set_rotation_xyz(RigidBody* body, const Vec3* euler);
void rigidbody_rotate(RigidBody* body, const Mat3* rot);
void rigidbody_rotate_xyz(RigidBody* body, const Vec3* euler);

void rigidbody_get_orientation(const RigidBody* body, Quat* out);
void rigidbody_set_orientation(RigidBody* body, const Quat* q);

void rigidbody_get_transform(const RigidBody* body, Transform* out);
void rigidbody_set_transform(RigidBody* body, const Transform* t);

// Velocities
void rigidbody_get_linear_velocity(const RigidBody* body, Vec3* out);
void rigidbody_set_linear_velocity(RigidBody* body, const Vec3* vel);
void rigidbody_add_linear_velocity(RigidBody* body, const Vec3* vel);

void rigidbody_get_angular_velocity(const RigidBody* body, Vec3* out);
void rigidbody_set_angular_velocity(RigidBody* body, const Vec3* vel);
void rigidbody_add_angular_velocity(RigidBody* body, const Vec3* vel);

// Forces and impulses
void rigidbody_apply_force(RigidBody* body, const Vec3* force, const Vec3* worldPoint);
void rigidbody_apply_force_to_center(RigidBody* body, const Vec3* force);
void rigidbody_apply_torque(RigidBody* body, const Vec3* torque);
void rigidbody_apply_impulse(RigidBody* body, const Vec3* impulse, const Vec3* worldPoint);
void rigidbody_apply_linear_impulse(RigidBody* body, const Vec3* impulse);
void rigidbody_apply_angular_impulse(RigidBody* body, const Vec3* impulse);

// Mass
float rigidbody_get_mass(const RigidBody* body);
void rigidbody_set_mass_data(RigidBody* body, const MassData* data);
void rigidbody_get_mass_data(const RigidBody* body, MassData* out);
void rigidbody_get_local_inertia(const RigidBody* body, Mat3* out);

// Shapes
void rigidbody_add_shape(RigidBody* body, Shape* shape);
void rigidbody_remove_shape(RigidBody* body, Shape* shape);
Shape* rigidbody_get_shape_list(const RigidBody* body);
int rigidbody_get_num_shapes(const RigidBody* body);

// Recompute mass from all shapes (called automatically when shapes change)
void rigidbody_update_mass(RigidBody* body);

// Damping
void rigidbody_set_linear_damping(RigidBody* body, float damping);
float rigidbody_get_linear_damping(const RigidBody* body);
void rigidbody_set_angular_damping(RigidBody* body, float damping);
float rigidbody_get_angular_damping(const RigidBody* body);

// Gravity
void rigidbody_set_gravity_scale(RigidBody* body, float scale);
float rigidbody_get_gravity_scale(const RigidBody* body);

// Rotation factor
void rigidbody_set_rotation_factor(RigidBody* body, const Vec3* factor);
void rigidbody_get_rotation_factor(const RigidBody* body, Vec3* out);

// Sleeping
void rigidbody_sleep(RigidBody* body);
void rigidbody_wake_up(RigidBody* body);
bool rigidbody_is_sleeping(const RigidBody* body);
void rigidbody_set_auto_sleep(RigidBody* body, bool enabled);
float rigidbody_get_sleep_time(const RigidBody* body);

// Coordinate conversion
void rigidbody_get_world_point(const RigidBody* body, const Vec3* localPoint, Vec3* worldPoint);
void rigidbody_get_local_point(const RigidBody* body, const Vec3* worldPoint, Vec3* localPoint);
void rigidbody_get_world_vector(const RigidBody* body, const Vec3* localVec, Vec3* worldVec);
void rigidbody_get_local_vector(const RigidBody* body, const Vec3* worldVec, Vec3* localVec);

// Linked list navigation
RigidBody* rigidbody_get_next(const RigidBody* body);
RigidBody* rigidbody_get_prev(const RigidBody* body);

// Internal: update world-space inertia tensor
void rigidbody_update_world_inertia(RigidBody* body);

// Internal: integrate velocities
void rigidbody_integrate_velocity(RigidBody* body, float dt, const Vec3* gravity);

// Internal: integrate position
void rigidbody_integrate_position(RigidBody* body, float dt);

// Internal: update shape AABBs
void rigidbody_update_shapes(RigidBody* body);

#endif