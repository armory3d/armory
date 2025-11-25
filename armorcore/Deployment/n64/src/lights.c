#include "lights.h"

void light_on_ready(ArmLight *light)
{
	for (uint8_t i = 0; i < light->trait_count; i++) {
		if (light->traits[i].on_ready) {
			light->traits[i].on_ready(light);
		}
	}
}

void light_on_update(ArmLight *light, float dt)
{
	for (uint8_t i = 0; i < light->trait_count; i++) {
		if (light->traits[i].on_update) {
			light->traits[i].on_update(light, dt);
		}
	}
}

void light_on_remove(ArmLight *light)
{
	for (uint8_t i = 0; i < light->trait_count; i++) {
		if (light->traits[i].on_remove) {
			light->traits[i].on_remove(light);
		}
	}
}
