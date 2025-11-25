#include "objects.h"

void object_on_ready(ArmObject *obj)
{
	for (uint8_t i = 0; i < obj->trait_count; i++) {
		if (obj->traits[i].on_ready) {
			obj->traits[i].on_ready(obj);
		}
	}
}

void object_on_update(ArmObject *obj, float dt)
{
	for (uint8_t i = 0; i < obj->trait_count; i++) {
		if (obj->traits[i].on_update) {
			obj->traits[i].on_update(obj, dt);
		}
	}
}

void object_on_remove(ArmObject *obj)
{
	for (uint8_t i = 0; i < obj->trait_count; i++) {
		if (obj->traits[i].on_remove) {
			obj->traits[i].on_remove(obj);
		}
	}
}
