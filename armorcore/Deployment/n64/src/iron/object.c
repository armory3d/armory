#include "object.h"

void set_visible(ArmObject *obj, bool visible)
{
	obj->visible = visible;
}

bool get_visible(ArmObject *obj)
{
	return obj->visible;
}