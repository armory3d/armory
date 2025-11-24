#pragma once

#include <stdint.h>
#include <t3d/t3dmath.h>
#include <t3d/t3dmodel.h>
#include "objects.h"

#ifdef __cplusplus
extern "C" {
#endif

#define FB_COUNT 3
#define MAX_TRAITS 4

typedef struct {
	uint8_t id;
    float pos[3];
    float rot[3];
    float scale[3];
	uint8_t traitCount;
	ArmTraitId traits[MAX_TRAITS];
    T3DModel *model;
    T3DMat4FP *modelMat;
} ArmObject;

typedef struct {
    uint8_t color[4];
    T3DVec3 dir;
} ArmLight;

typedef struct {
    T3DVec3 pos;
    T3DVec3 target;
    float fov;
    float near;
    float far;
} ArmCamera;

typedef struct {
    uint8_t clearColor[4];
    uint8_t ambientColor[4];
} ArmWorld;

typedef struct {
    ArmWorld world;
    ArmCamera camera;

    uint16_t objectCount;
    ArmObject *objects;

    uint8_t lightCount;
    ArmLight *lights;
} ArmScene;

#ifdef __cplusplus
}
#endif
