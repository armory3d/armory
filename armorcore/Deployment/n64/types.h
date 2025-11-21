#pragma once

#include <stdint.h>
#include <t3d/t3dmath.h>
#include <t3d/t3dmodel.h>

#ifdef __cplusplus
extern "C" {
#endif

#define FB_COUNT 3

typedef struct {
	int id;
    float pos[3];
    float rot[3];
    float scale[3];
    T3DModel *model;
    T3DMat4FP *modelMat; // array [FB_COUNT]
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

    int objectCount;
    ArmObject *objects;

    int lightCount;
    ArmLight *lights;
} ArmScene;

#ifdef __cplusplus
}
#endif
