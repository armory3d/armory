#pragma once

#include <btBulletCollisionCommon.h>
#include "LinearMath/btIDebugDraw.h"
#include "LinearMath/btVector3.h"

#define HL_NAME(n) bullet_##n
#include <hl.h>

// TODO: The Haxe side only assumes f32 at the moment...
#ifdef BT_USE_DOUBLE_PRECISION
	#define _HL_FFI_TYPE_btScalar _I64
	static hl_type hl_type_btScalar = hlt_f64;
#else
	#define _HL_FFI_TYPE_btScalar _I32
	static hl_type hl_type_btScalar = hlt_f32;
#endif

class DebugDrawer : public btIDebugDraw
{
	int m_debugMode = 0;

public:
	DebugDrawer() {};
	virtual ~DebugDrawer() {};

	virtual void drawLine(const btVector3& from, const btVector3& to, const btVector3& color);
	virtual void drawContactPoint(const btVector3& PointOnB, const btVector3& normalOnB, btScalar distance, int lifeTime, const btVector3& color);
	virtual void reportErrorWarning(const char* warningString);
	virtual void draw3dText(const btVector3& location, const char* textString);

	virtual void setDebugMode(int debugMode);
	virtual int getDebugMode() const;

	// Using vclosure* is not really type-safe unfortunately, but Haxe passes
	// closures as vclosure* and we need to use hl_dyn_call() to call them.
	// We cannot use proper function pointers here and wrap the call to hl_dyn_call() in a lambda
	// since the lambda would then need to capture the vclosure and in turn could not be converted
	// to a function pointer (this is not possible for capturing lambdas).
	vclosure* p_drawLine = nullptr;
	vclosure* p_drawContactPoint = nullptr;
	vclosure* p_reportErrorWarning = nullptr;
	vclosure* p_draw3dText = nullptr;
};

// To simplify the Haxe interop, we're using a global instance here
// instead of passing around an instance in all Haxe extern calls.
// Normally you don't need multiple drawer instances anyways...
static DebugDrawer* globalDebugDrawerInstance = new DebugDrawer();

extern "C"
{
	HL_PRIM void HL_NAME(debugDrawer_worldSetGlobalDebugDrawer)(vbyte* physicsWorld)
	{
		btCollisionWorld *p_world = (btCollisionWorld *)physicsWorld;
		p_world->setDebugDrawer(globalDebugDrawerInstance);
	}
	DEFINE_PRIM(_VOID, debugDrawer_worldSetGlobalDebugDrawer, _BYTES);

	HL_PRIM void HL_NAME(debugDrawer_setDebugMode)(int debugMode)
	{
		globalDebugDrawerInstance->setDebugMode(debugMode);
	}
	DEFINE_PRIM(_VOID, debugDrawer_setDebugMode, _I32);

	HL_PRIM int HL_NAME(debugDrawer_getDebugMode)()
	{
		return globalDebugDrawerInstance->getDebugMode();
	}
	DEFINE_PRIM(_I32, debugDrawer_getDebugMode, _VOID);

	HL_PRIM void HL_NAME(debugDrawer_setDrawLine)(vclosure* func)
	{
		// Don't allow to unset p_drawLine, otherwise we'd have to
		// deal with potential threaded-GC issues:
		// - The GC might not like if we set p_drawLine to null before removing the root 
		// - If we remove the root first, the GC might attempt to free memory that's still in use in this function
		if (!func) return;

		globalDebugDrawerInstance->p_drawLine = func;

		static bool once = true;
		if (once)
		{
			// Add root after value was assigned to prevent potential issues when registering nullptr to threaded GC
			hl_add_root(&globalDebugDrawerInstance->p_drawLine);
			once = false;
		}
	}
	DEFINE_PRIM(_VOID, debugDrawer_setDrawLine, _FUN(_VOID, _DYN _DYN _DYN));

	HL_PRIM void HL_NAME(debugDrawer_setDrawContactPoint)(vclosure* func)
	{
		if (!func) return;

		globalDebugDrawerInstance->p_drawContactPoint = func;

		static bool once = true;
		if (once)
		{
			hl_add_root(&globalDebugDrawerInstance->p_drawContactPoint);
			once = false;
		}
	}
	DEFINE_PRIM(_VOID, debugDrawer_setDrawContactPoint, _FUN(_VOID, _DYN _DYN _HL_FFI_TYPE_btScalar _I32 _DYN));

	HL_PRIM void HL_NAME(debugDrawer_setReportErrorWarning)(vclosure* func)
	{
		if (!func) return;

		globalDebugDrawerInstance->p_reportErrorWarning = func;

		static bool once = true;
		if (once)
		{
			hl_add_root(&globalDebugDrawerInstance->p_reportErrorWarning);
			once = false;
		}
	}
	DEFINE_PRIM(_VOID, debugDrawer_setReportErrorWarning, _FUN(_VOID, _STRING));

	HL_PRIM void HL_NAME(debugDrawer_setDraw3dText)(vclosure* func)
	{
		if (!func) return;

		globalDebugDrawerInstance->p_draw3dText = func;

		static bool once = true;
		if (once)
		{
			hl_add_root(&globalDebugDrawerInstance->p_draw3dText);
			once = false;
		}
	}
	DEFINE_PRIM(_VOID, debugDrawer_setDraw3dText, _FUN(_VOID, _DYN _STRING));
}