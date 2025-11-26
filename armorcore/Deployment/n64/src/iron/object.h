#pragma once

#include "../types.h"

#ifdef __cplusplus
extern "C" {
#endif

void set_visible(ArmObject *obj, bool visible);
bool get_visible(ArmObject *obj);

#define OBJECT(entity) (&(entity)->object)

#ifdef __cplusplus
}
#endif