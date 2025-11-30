#pragma once

#include <libdragon.h>
#include <t3d/t3d.h>
#include <t3d/t3dmodel.h>

#include "types.h"

#ifdef __cplusplus
extern "C" {
#endif

#ifndef ENGINE_ENABLE_PHYSICS
#define ENGINE_ENABLE_PHYSICS 0
#endif

void engine_init(void);
void engine_shutdown(void);

#ifdef __cplusplus
}
#endif
