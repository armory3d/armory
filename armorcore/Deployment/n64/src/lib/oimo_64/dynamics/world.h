#ifndef WORLD_H
#define WORLD_H

#include "../common/Transform.h"
#include "rigidbody/rigidbody.h"
#include <stdbool.h>

// =============================================================================
// Forward Declarations
// =============================================================================

typedef struct World World;
// Note: Contact and ContactPoint are defined in rigidbody.h

// =============================================================================
// Raycast Callback
// =============================================================================

typedef struct {
    RigidBody* body;
    Shape* shape;
    Vec3 position;    // Hit point in world space
    Vec3 normal;      // Surface normal at hit point
    float fraction;   // Distance along ray (0-1)
} RaycastHit;

// Callback function type: return true to continue, false to stop
typedef bool (*RaycastCallback)(const RaycastHit* hit, void* userData);

// =============================================================================
// Contact Callback
// =============================================================================

typedef void (*ContactBeginCallback)(Contact* contact, void* userData);
typedef void (*ContactEndCallback)(Contact* contact, void* userData);
typedef void (*ContactPreSolveCallback)(Contact* contact, void* userData);
typedef void (*ContactPostSolveCallback)(Contact* contact, void* userData);

// =============================================================================
// World Configuration
// =============================================================================

typedef struct {
    Vec3 gravity;
    int velocityIterations;   // Constraint solver iterations
    int positionIterations;   // Position correction iterations
    bool allowSleep;
} WorldConfig;

// =============================================================================
// World
// =============================================================================

struct World {
    // Gravity
    Vec3 gravity;

    // Rigid bodies (doubly-linked list)
    RigidBody* bodyList;
    int numBodies;

    // Active contacts (doubly-linked list)
    Contact* contactList;
    int numContacts;

    // Contact pool for reuse
    Contact* contactPool;
    int contactPoolSize;

    // Solver settings
    int velocityIterations;
    int positionIterations;

    // Callbacks
    ContactBeginCallback onContactBegin;
    ContactEndCallback onContactEnd;
    ContactPreSolveCallback onContactPreSolve;
    ContactPostSolveCallback onContactPostSolve;
    void* callbackUserData;

    // Settings
    bool allowSleep;
};

// =============================================================================
// World Functions
// =============================================================================

// Create/destroy
World* world_create(const WorldConfig* config);
World* world_create_default(void);
void world_destroy(World* world);

// Gravity
void world_set_gravity(World* world, const Vec3* gravity);
void world_get_gravity(const World* world, Vec3* out);

// Body management
void world_add_body(World* world, RigidBody* body);
void world_remove_body(World* world, RigidBody* body);
RigidBody* world_get_body_list(const World* world);
int world_get_num_bodies(const World* world);

// Simulation
void world_step(World* world, float dt);

// Solver settings
void world_set_velocity_iterations(World* world, int iterations);
int world_get_velocity_iterations(const World* world);
void world_set_position_iterations(World* world, int iterations);
int world_get_position_iterations(const World* world);

// Raycasting
// Cast a ray and call callback for each hit shape
void world_raycast(World* world, const Vec3* from, const Vec3* to,
                   RaycastCallback callback, void* userData);

// Cast a ray and return closest hit (returns true if hit)
bool world_raycast_closest(World* world, const Vec3* from, const Vec3* to,
                           RaycastHit* outHit);

// Contact callbacks
void world_set_contact_callbacks(World* world,
                                 ContactBeginCallback onBegin,
                                 ContactEndCallback onEnd,
                                 ContactPreSolveCallback onPreSolve,
                                 ContactPostSolveCallback onPostSolve,
                                 void* userData);

// Contact access
Contact* world_get_contact_list(const World* world);
int world_get_num_contacts(const World* world);

// Sleep settings
void world_set_allow_sleep(World* world, bool allow);
bool world_get_allow_sleep(const World* world);

// Clear all bodies and contacts
void world_clear(World* world);

// =============================================================================
// Collision Detection (Internal)
// =============================================================================

// Test if two shapes' collision masks allow collision
bool collision_should_collide(const Shape* a, const Shape* b);

// Test AABB overlap
bool collision_test_aabb(const Shape* a, const Shape* b);

// Narrow-phase collision detection between two shapes
// Returns true if collision occurred, fills contact info
bool collision_test_shapes(Shape* a, Shape* b, ContactPoint* outPoints, int* outNumPoints);

// Specific collision tests
bool collision_sphere_sphere(const Shape* a, const Shape* b, ContactPoint* out);
bool collision_sphere_box(const Shape* sphere, const Shape* box, ContactPoint* out);
bool collision_box_box(const Shape* a, const Shape* b, ContactPoint* outPoints, int* outNumPoints);

// Ray-shape intersection
bool collision_ray_sphere(const Vec3* from, const Vec3* dir, float maxDist,
                          const Shape* sphere, float* outDist, Vec3* outNormal);
bool collision_ray_box(const Vec3* from, const Vec3* dir, float maxDist,
                       const Shape* box, float* outDist, Vec3* outNormal);

#endif
