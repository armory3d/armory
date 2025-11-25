#include "cameras.h"

void camera_on_ready(ArmCamera *camera)
{
	for (uint8_t i = 0; i < camera->trait_count; i++) {
		if (camera->traits[i].on_ready) {
			camera->traits[i].on_ready(camera);
		}
	}
}

void camera_on_update(ArmCamera *camera, float dt)
{
	for (uint8_t i = 0; i < camera->trait_count; i++) {
		if (camera->traits[i].on_update) {
			camera->traits[i].on_update(camera, dt);
		}
	}
}

void camera_on_remove(ArmCamera *camera)
{
	for (uint8_t i = 0; i < camera->trait_count; i++) {
		if (camera->traits[i].on_remove) {
			camera->traits[i].on_remove(camera);
		}
	}
}
