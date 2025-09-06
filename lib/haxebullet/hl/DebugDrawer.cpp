#include "DebugDrawer.h"

void DebugDrawer::drawLine(const btVector3& from, const btVector3& to, const btVector3& color)
{
	if (p_drawLine)
	{
		// hl_make_dyn() expects a double pointer for hlt_bytes types
		// despite the function signature suggesting otherwise
		const btVector3* p_from = &from;
		const btVector3* p_to = &to;
		const btVector3* p_color = &color;

		vdynamic* args[3] = {
			hl_make_dyn((void*)&p_from, &hlt_bytes),
			hl_make_dyn((void*)&p_to, &hlt_bytes),
			hl_make_dyn((void*)&p_color, &hlt_bytes)
		};
		hl_dyn_call(p_drawLine, args, 3);
	}
}

void DebugDrawer::drawContactPoint(const btVector3& PointOnB, const btVector3& normalOnB, btScalar distance, int lifeTime, const btVector3& color)
{
	if (p_drawContactPoint)
	{
		const btVector3* p_PointOnB = &PointOnB;
		const btVector3* p_normalOnB = &normalOnB;
		const btVector3* p_color = &color;

		vdynamic* args[5] = {
			hl_make_dyn((void*)&p_PointOnB, &hlt_bytes),
			hl_make_dyn((void*)&p_normalOnB, &hlt_bytes),
			hl_make_dyn((void*)&distance, &hl_type_btScalar),
			hl_make_dyn((void*)&lifeTime, &hlt_i32),
			hl_make_dyn((void*)&p_color, &hlt_bytes)
		};
		hl_dyn_call(p_drawContactPoint, args, 5);
	}
}

void DebugDrawer::reportErrorWarning(const char* warningString)
{
	if (p_reportErrorWarning)
	{
		vdynamic* args[1] = {
			hl_make_dyn((void*)&warningString, &hlt_bytes)
		};
		hl_dyn_call(p_reportErrorWarning, args, 1);
	}
}

void DebugDrawer::draw3dText(const btVector3& location, const char* textString)
{
	if (p_draw3dText)
	{
		const btVector3* p_location = &location;

		vdynamic* args[2] = {
			hl_make_dyn((void*)&p_location, &hlt_bytes),
			hl_make_dyn((void*)&textString, &hlt_bytes),
		};
		hl_dyn_call(p_draw3dText, args, 2);
	}
}

void DebugDrawer::setDebugMode(int debugMode)
{
	m_debugMode = debugMode;
}

int DebugDrawer::getDebugMode() const
{
	return m_debugMode;
}
