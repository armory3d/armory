#pragma once

#include "../../common/vec3.h"
#include "../../common/mat3.h"
#include "../../common/setting.h"
#include "../../collision/geometry/geometry.h"

typedef struct OimoShapeConfig {
    OimoVec3 position;         // Local position relative to rigid body
    OimoMat3 rotation;         // Local rotation relative to rigid body
    OimoScalar friction;       // Coefficient of friction
    OimoScalar restitution;    // Coefficient of restitution
    OimoScalar density;        // Density in Kg/m^3
    OimoGeometry* geometry;    // Collision geometry
    int collisionGroup;        // Collision group bits
    int collisionMask;         // Collision mask bits
} OimoShapeConfig;

// Snake_case compatibility aliases for Armory code generator
#define collision_group collisionGroup
#define collision_mask collisionMask

static inline void oimo_shape_config_init(OimoShapeConfig* config) {
    config->position = oimo_vec3_zero();
    config->rotation = oimo_mat3_identity();
    config->friction = OIMO_DEFAULT_FRICTION;
    config->restitution = OIMO_DEFAULT_RESTITUTION;
    config->density = OIMO_DEFAULT_DENSITY;
    config->geometry = NULL;
    config->collisionGroup = OIMO_DEFAULT_COLLISION_GROUP;
    config->collisionMask = OIMO_DEFAULT_COLLISION_MASK;
}

static inline OimoShapeConfig oimo_shape_config(void) {
    OimoShapeConfig config;
    oimo_shape_config_init(&config);
    return config;
}

