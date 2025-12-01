#ifndef OIMO_COMMON_SETTING_H
#define OIMO_COMMON_SETTING_H

// Using float with libdragon fastmath. Can be changed to fixed-point later.
typedef float OimoScalar;

#define OIMO_DEFAULT_FRICTION       0.2f
#define OIMO_DEFAULT_RESTITUTION    0.2f
#define OIMO_DEFAULT_DENSITY        1.0f
#define OIMO_DEFAULT_COLLISION_GROUP 1
#define OIMO_DEFAULT_COLLISION_MASK  1

#define OIMO_MAX_TRANSLATION_PER_STEP  20.0f
#define OIMO_MAX_ROTATION_PER_STEP     3.14159265358979f  // PI

#define OIMO_BVH_PROXY_PADDING                     0.1f
#define OIMO_BVH_INCREMENTAL_COLLISION_THRESHOLD   0.45f

#define OIMO_CONTACT_ENABLE_BOUNCE_THRESHOLD       0.5f
#define OIMO_VELOCITY_BAUMGARTE                    0.2f
#define OIMO_POSITION_SPLIT_IMPULSE_BAUMGARTE      0.4f
#define OIMO_POSITION_NGS_BAUMGARTE                1.0f

#define OIMO_CONTACT_USE_ALT_POS_CORRECTION_DEPTH_THRESHOLD  0.05f
#define OIMO_CONTACT_PERSISTENCE_THRESHOLD         0.05f
#define OIMO_MAX_MANIFOLD_POINTS                   4

#define OIMO_SLEEPING_VELOCITY_THRESHOLD           0.2f
#define OIMO_SLEEPING_ANGULAR_VELOCITY_THRESHOLD   0.5f
#define OIMO_SLEEPING_TIME_THRESHOLD               1.0f
#define OIMO_DISABLE_SLEEPING                      0  // 0 = false, 1 = true

#define OIMO_LINEAR_SLOP           0.005f
#define OIMO_ANGULAR_SLOP          0.01745329251f  // 1 degree in radians

#define OIMO_EPSILON               1e-6f
#define OIMO_POSITIVE_INFINITY     1e30f
#define OIMO_NEGATIVE_INFINITY     (-1e30f)

#define OIMO_DEFAULT_GRAVITY_X     0.0f
#define OIMO_DEFAULT_GRAVITY_Y     -9.80665f
#define OIMO_DEFAULT_GRAVITY_Z     0.0f

#endif // OIMO_COMMON_SETTING_H
