#pragma once

#include "../../common/vec3.h"
#include "../../common/mat3.h"
#include "../../common/setting.h"
#include "rigid_body_type.h"

typedef struct OimoRigidBodyConfig {
    OimoVec3 position;                        // World position
    OimoMat3 rotation;                        // Rotation matrix
    OimoVec3 linearVelocity;                  // Initial linear velocity
    OimoVec3 angularVelocity;                 // Initial angular velocity
    int type;                                 // DYNAMIC, STATIC, or KINEMATIC
    OimoScalar linearDamping;                 // Linear velocity damping
    OimoScalar angularDamping;                // Angular velocity damping
    int autoSleep;                            // Auto-sleep when stationary
    OimoScalar sleepingVelocityThreshold;     // Linear velocity threshold for sleep
    OimoScalar sleepingAngularVelocityThreshold; // Angular velocity threshold for sleep
    OimoScalar sleepingTimeThreshold;         // Time threshold for sleep
} OimoRigidBodyConfig;

static inline void oimo_rigid_body_config_init(OimoRigidBodyConfig* config) {
    config->position = oimo_vec3_zero();
    config->rotation = oimo_mat3_identity();
    config->linearVelocity = oimo_vec3_zero();
    config->angularVelocity = oimo_vec3_zero();
    config->type = OIMO_RIGID_BODY_DYNAMIC;
    config->linearDamping = 0;
    config->angularDamping = 0;
    config->autoSleep = !OIMO_DISABLE_SLEEPING;
    config->sleepingVelocityThreshold = OIMO_SLEEPING_VELOCITY_THRESHOLD;
    config->sleepingAngularVelocityThreshold = OIMO_SLEEPING_ANGULAR_VELOCITY_THRESHOLD;
    config->sleepingTimeThreshold = OIMO_SLEEPING_TIME_THRESHOLD;
}

static inline OimoRigidBodyConfig oimo_rigid_body_config(void) {
    OimoRigidBodyConfig config;
    oimo_rigid_body_config_init(&config);
    return config;
}

