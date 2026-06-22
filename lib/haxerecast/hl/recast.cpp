#ifdef EMSCRIPTEN

#include <emscripten.h>
#define HL_PRIM
#define HL_NAME(n)	EMSCRIPTEN_KEEPALIVE eb_##n
#define DEFINE_PRIM(ret, name, args)
#define _OPT(t) t*
#define _GET_OPT(value,t) *value
#define alloc_ref(r, _) r
#define alloc_ref_const(r,_) r
#define _ref(t)			t
#define _unref(v)		v
#define free_ref(v) delete (v)
#define HL_CONST const

#else

#define HL_NAME(x) recast_##x
#include <hl.h>
#define _IDL _BYTES
#define _OPT(t) vdynamic *
#define _GET_OPT(value,t) (value)->v.t
#define alloc_ref(r, _) r
#define alloc_ref_const(r,_) r
#define _ref(t)			t
#define _unref(v)		v
#define free_ref(v) delete (v)
#define HL_CONST const

#endif

#include "recastjs.h"

extern "C" {

static void finalize_rcConfig( _ref(rcConfig)* _this ) { free_ref(_this); }
HL_PRIM void HL_NAME(rcConfig_delete)( _ref(rcConfig)* _this ) {
	free_ref(_this);
}
DEFINE_PRIM(_VOID, rcConfig_delete, _IDL);
static void finalize_Vec3( _ref(Vec3)* _this ) { free_ref(_this); }
HL_PRIM void HL_NAME(Vec3_delete)( _ref(Vec3)* _this ) {
	free_ref(_this);
}
DEFINE_PRIM(_VOID, Vec3_delete, _IDL);
static void finalize_Triangle( _ref(Triangle)* _this ) { free_ref(_this); }
HL_PRIM void HL_NAME(Triangle_delete)( _ref(Triangle)* _this ) {
	free_ref(_this);
}
DEFINE_PRIM(_VOID, Triangle_delete, _IDL);
static void finalize_DebugNavMesh( _ref(DebugNavMesh)* _this ) { free_ref(_this); }
HL_PRIM void HL_NAME(DebugNavMesh_delete)( _ref(DebugNavMesh)* _this ) {
	free_ref(_this);
}
DEFINE_PRIM(_VOID, DebugNavMesh_delete, _IDL);
static void finalize_dtNavMesh( _ref(dtNavMesh)* _this ) { free_ref(_this); }
HL_PRIM void HL_NAME(dtNavMesh_delete)( _ref(dtNavMesh)* _this ) {
	free_ref(_this);
}
DEFINE_PRIM(_VOID, dtNavMesh_delete, _IDL);
static void finalize_NavmeshData( _ref(NavmeshData)* _this ) { free_ref(_this); }
HL_PRIM void HL_NAME(NavmeshData_delete)( _ref(NavmeshData)* _this ) {
	free_ref(_this);
}
DEFINE_PRIM(_VOID, NavmeshData_delete, _IDL);
static void finalize_NavPath( _ref(NavPath)* _this ) { free_ref(_this); }
HL_PRIM void HL_NAME(NavPath_delete)( _ref(NavPath)* _this ) {
	free_ref(_this);
}
DEFINE_PRIM(_VOID, NavPath_delete, _IDL);
static void finalize_dtObstacleRef( _ref(dtObstacleRef)* _this ) { free_ref(_this); }
HL_PRIM void HL_NAME(dtObstacleRef_delete)( _ref(dtObstacleRef)* _this ) {
	free_ref(_this);
}
DEFINE_PRIM(_VOID, dtObstacleRef_delete, _IDL);
static void finalize_dtCrowdAgentParams( _ref(dtCrowdAgentParams)* _this ) { free_ref(_this); }
HL_PRIM void HL_NAME(dtCrowdAgentParams_delete)( _ref(dtCrowdAgentParams)* _this ) {
	free_ref(_this);
}
DEFINE_PRIM(_VOID, dtCrowdAgentParams_delete, _IDL);
static void finalize_NavMesh( _ref(NavMesh)* _this ) { free_ref(_this); }
HL_PRIM void HL_NAME(NavMesh_delete)( _ref(NavMesh)* _this ) {
	free_ref(_this);
}
DEFINE_PRIM(_VOID, NavMesh_delete, _IDL);
static void finalize_Crowd( _ref(Crowd)* _this ) { free_ref(_this); }
HL_PRIM void HL_NAME(Crowd_delete)( _ref(Crowd)* _this ) {
	free_ref(_this);
}
DEFINE_PRIM(_VOID, Crowd_delete, _IDL);
static void finalize_RecastConfigHelper( _ref(RecastConfigHelper)* _this ) { free_ref(_this); }
HL_PRIM void HL_NAME(RecastConfigHelper_delete)( _ref(RecastConfigHelper)* _this ) {
	free_ref(_this);
}
DEFINE_PRIM(_VOID, RecastConfigHelper_delete, _IDL);
static void finalize_rcFloatArray( _ref(rcFloatArray)* _this ) { free_ref(_this); }
HL_PRIM void HL_NAME(rcFloatArray_delete)( _ref(rcFloatArray)* _this ) {
	free_ref(_this);
}
DEFINE_PRIM(_VOID, rcFloatArray_delete, _IDL);
static void finalize_rcIntArray( _ref(rcIntArray)* _this ) { free_ref(_this); }
HL_PRIM void HL_NAME(rcIntArray_delete)( _ref(rcIntArray)* _this ) {
	free_ref(_this);
}
DEFINE_PRIM(_VOID, rcIntArray_delete, _IDL);
HL_PRIM _ref(rcConfig)* HL_NAME(rcConfig_new0)() {
	return alloc_ref((new rcConfig()),rcConfig);
}
DEFINE_PRIM(_IDL, rcConfig_new0,);

HL_PRIM int HL_NAME(rcConfig_get_width)( _ref(rcConfig)* _this ) {
	return _unref(_this)->width;
}
HL_PRIM int HL_NAME(rcConfig_set_width)( _ref(rcConfig)* _this, int value ) {
	_unref(_this)->width = (value);
	return value;
}
DEFINE_PRIM(_I32,rcConfig_get_width,_IDL);
DEFINE_PRIM(_I32,rcConfig_set_width,_IDL _I32);

HL_PRIM int HL_NAME(rcConfig_get_height)( _ref(rcConfig)* _this ) {
	return _unref(_this)->height;
}
HL_PRIM int HL_NAME(rcConfig_set_height)( _ref(rcConfig)* _this, int value ) {
	_unref(_this)->height = (value);
	return value;
}
DEFINE_PRIM(_I32,rcConfig_get_height,_IDL);
DEFINE_PRIM(_I32,rcConfig_set_height,_IDL _I32);

HL_PRIM int HL_NAME(rcConfig_get_tileSize)( _ref(rcConfig)* _this ) {
	return _unref(_this)->tileSize;
}
HL_PRIM int HL_NAME(rcConfig_set_tileSize)( _ref(rcConfig)* _this, int value ) {
	_unref(_this)->tileSize = (value);
	return value;
}
DEFINE_PRIM(_I32,rcConfig_get_tileSize,_IDL);
DEFINE_PRIM(_I32,rcConfig_set_tileSize,_IDL _I32);

HL_PRIM int HL_NAME(rcConfig_get_borderSize)( _ref(rcConfig)* _this ) {
	return _unref(_this)->borderSize;
}
HL_PRIM int HL_NAME(rcConfig_set_borderSize)( _ref(rcConfig)* _this, int value ) {
	_unref(_this)->borderSize = (value);
	return value;
}
DEFINE_PRIM(_I32,rcConfig_get_borderSize,_IDL);
DEFINE_PRIM(_I32,rcConfig_set_borderSize,_IDL _I32);

HL_PRIM float HL_NAME(rcConfig_get_cs)( _ref(rcConfig)* _this ) {
	return _unref(_this)->cs;
}
HL_PRIM float HL_NAME(rcConfig_set_cs)( _ref(rcConfig)* _this, float value ) {
	_unref(_this)->cs = (value);
	return value;
}
DEFINE_PRIM(_F32,rcConfig_get_cs,_IDL);
DEFINE_PRIM(_F32,rcConfig_set_cs,_IDL _F32);

HL_PRIM float HL_NAME(rcConfig_get_ch)( _ref(rcConfig)* _this ) {
	return _unref(_this)->ch;
}
HL_PRIM float HL_NAME(rcConfig_set_ch)( _ref(rcConfig)* _this, float value ) {
	_unref(_this)->ch = (value);
	return value;
}
DEFINE_PRIM(_F32,rcConfig_get_ch,_IDL);
DEFINE_PRIM(_F32,rcConfig_set_ch,_IDL _F32);

HL_PRIM float HL_NAME(rcConfig_get_walkableSlopeAngle)( _ref(rcConfig)* _this ) {
	return _unref(_this)->walkableSlopeAngle;
}
HL_PRIM float HL_NAME(rcConfig_set_walkableSlopeAngle)( _ref(rcConfig)* _this, float value ) {
	_unref(_this)->walkableSlopeAngle = (value);
	return value;
}
DEFINE_PRIM(_F32,rcConfig_get_walkableSlopeAngle,_IDL);
DEFINE_PRIM(_F32,rcConfig_set_walkableSlopeAngle,_IDL _F32);

HL_PRIM int HL_NAME(rcConfig_get_walkableHeight)( _ref(rcConfig)* _this ) {
	return _unref(_this)->walkableHeight;
}
HL_PRIM int HL_NAME(rcConfig_set_walkableHeight)( _ref(rcConfig)* _this, int value ) {
	_unref(_this)->walkableHeight = (value);
	return value;
}
DEFINE_PRIM(_I32,rcConfig_get_walkableHeight,_IDL);
DEFINE_PRIM(_I32,rcConfig_set_walkableHeight,_IDL _I32);

HL_PRIM int HL_NAME(rcConfig_get_walkableClimb)( _ref(rcConfig)* _this ) {
	return _unref(_this)->walkableClimb;
}
HL_PRIM int HL_NAME(rcConfig_set_walkableClimb)( _ref(rcConfig)* _this, int value ) {
	_unref(_this)->walkableClimb = (value);
	return value;
}
DEFINE_PRIM(_I32,rcConfig_get_walkableClimb,_IDL);
DEFINE_PRIM(_I32,rcConfig_set_walkableClimb,_IDL _I32);

HL_PRIM int HL_NAME(rcConfig_get_walkableRadius)( _ref(rcConfig)* _this ) {
	return _unref(_this)->walkableRadius;
}
HL_PRIM int HL_NAME(rcConfig_set_walkableRadius)( _ref(rcConfig)* _this, int value ) {
	_unref(_this)->walkableRadius = (value);
	return value;
}
DEFINE_PRIM(_I32,rcConfig_get_walkableRadius,_IDL);
DEFINE_PRIM(_I32,rcConfig_set_walkableRadius,_IDL _I32);

HL_PRIM int HL_NAME(rcConfig_get_maxEdgeLen)( _ref(rcConfig)* _this ) {
	return _unref(_this)->maxEdgeLen;
}
HL_PRIM int HL_NAME(rcConfig_set_maxEdgeLen)( _ref(rcConfig)* _this, int value ) {
	_unref(_this)->maxEdgeLen = (value);
	return value;
}
DEFINE_PRIM(_I32,rcConfig_get_maxEdgeLen,_IDL);
DEFINE_PRIM(_I32,rcConfig_set_maxEdgeLen,_IDL _I32);

HL_PRIM float HL_NAME(rcConfig_get_maxSimplificationError)( _ref(rcConfig)* _this ) {
	return _unref(_this)->maxSimplificationError;
}
HL_PRIM float HL_NAME(rcConfig_set_maxSimplificationError)( _ref(rcConfig)* _this, float value ) {
	_unref(_this)->maxSimplificationError = (value);
	return value;
}
DEFINE_PRIM(_F32,rcConfig_get_maxSimplificationError,_IDL);
DEFINE_PRIM(_F32,rcConfig_set_maxSimplificationError,_IDL _F32);

HL_PRIM int HL_NAME(rcConfig_get_minRegionArea)( _ref(rcConfig)* _this ) {
	return _unref(_this)->minRegionArea;
}
HL_PRIM int HL_NAME(rcConfig_set_minRegionArea)( _ref(rcConfig)* _this, int value ) {
	_unref(_this)->minRegionArea = (value);
	return value;
}
DEFINE_PRIM(_I32,rcConfig_get_minRegionArea,_IDL);
DEFINE_PRIM(_I32,rcConfig_set_minRegionArea,_IDL _I32);

HL_PRIM int HL_NAME(rcConfig_get_mergeRegionArea)( _ref(rcConfig)* _this ) {
	return _unref(_this)->mergeRegionArea;
}
HL_PRIM int HL_NAME(rcConfig_set_mergeRegionArea)( _ref(rcConfig)* _this, int value ) {
	_unref(_this)->mergeRegionArea = (value);
	return value;
}
DEFINE_PRIM(_I32,rcConfig_get_mergeRegionArea,_IDL);
DEFINE_PRIM(_I32,rcConfig_set_mergeRegionArea,_IDL _I32);

HL_PRIM int HL_NAME(rcConfig_get_maxVertsPerPoly)( _ref(rcConfig)* _this ) {
	return _unref(_this)->maxVertsPerPoly;
}
HL_PRIM int HL_NAME(rcConfig_set_maxVertsPerPoly)( _ref(rcConfig)* _this, int value ) {
	_unref(_this)->maxVertsPerPoly = (value);
	return value;
}
DEFINE_PRIM(_I32,rcConfig_get_maxVertsPerPoly,_IDL);
DEFINE_PRIM(_I32,rcConfig_set_maxVertsPerPoly,_IDL _I32);

HL_PRIM float HL_NAME(rcConfig_get_detailSampleDist)( _ref(rcConfig)* _this ) {
	return _unref(_this)->detailSampleDist;
}
HL_PRIM float HL_NAME(rcConfig_set_detailSampleDist)( _ref(rcConfig)* _this, float value ) {
	_unref(_this)->detailSampleDist = (value);
	return value;
}
DEFINE_PRIM(_F32,rcConfig_get_detailSampleDist,_IDL);
DEFINE_PRIM(_F32,rcConfig_set_detailSampleDist,_IDL _F32);

HL_PRIM float HL_NAME(rcConfig_get_detailSampleMaxError)( _ref(rcConfig)* _this ) {
	return _unref(_this)->detailSampleMaxError;
}
HL_PRIM float HL_NAME(rcConfig_set_detailSampleMaxError)( _ref(rcConfig)* _this, float value ) {
	_unref(_this)->detailSampleMaxError = (value);
	return value;
}
DEFINE_PRIM(_F32,rcConfig_get_detailSampleMaxError,_IDL);
DEFINE_PRIM(_F32,rcConfig_set_detailSampleMaxError,_IDL _F32);

HL_PRIM _ref(Vec3)* HL_NAME(Vec3_new0)() {
	return alloc_ref((new Vec3()),Vec3);
}
DEFINE_PRIM(_IDL, Vec3_new0,);

HL_PRIM _ref(Vec3)* HL_NAME(Vec3_new3)(float x, float y, float z) {
	return alloc_ref((new Vec3(x, y, z)),Vec3);
}
DEFINE_PRIM(_IDL, Vec3_new3, _F32 _F32 _F32);

HL_PRIM float HL_NAME(Vec3_get_x)( _ref(Vec3)* _this ) {
	return _unref(_this)->x;
}
HL_PRIM float HL_NAME(Vec3_set_x)( _ref(Vec3)* _this, float value ) {
	_unref(_this)->x = (value);
	return value;
}
DEFINE_PRIM(_F32,Vec3_get_x,_IDL);
DEFINE_PRIM(_F32,Vec3_set_x,_IDL _F32);

HL_PRIM float HL_NAME(Vec3_get_y)( _ref(Vec3)* _this ) {
	return _unref(_this)->y;
}
HL_PRIM float HL_NAME(Vec3_set_y)( _ref(Vec3)* _this, float value ) {
	_unref(_this)->y = (value);
	return value;
}
DEFINE_PRIM(_F32,Vec3_get_y,_IDL);
DEFINE_PRIM(_F32,Vec3_set_y,_IDL _F32);

HL_PRIM float HL_NAME(Vec3_get_z)( _ref(Vec3)* _this ) {
	return _unref(_this)->z;
}
HL_PRIM float HL_NAME(Vec3_set_z)( _ref(Vec3)* _this, float value ) {
	_unref(_this)->z = (value);
	return value;
}
DEFINE_PRIM(_F32,Vec3_get_z,_IDL);
DEFINE_PRIM(_F32,Vec3_set_z,_IDL _F32);

HL_PRIM _ref(Triangle)* HL_NAME(Triangle_new0)() {
	return alloc_ref((new Triangle()),Triangle);
}
DEFINE_PRIM(_IDL, Triangle_new0,);

HL_PRIM HL_CONST _ref(Vec3)* HL_NAME(Triangle_getPoint1)(_ref(Triangle)* _this, int n) {
	return alloc_ref_const(&(_unref(_this)->getPoint(n)),Vec3);
}
DEFINE_PRIM(_IDL, Triangle_getPoint1, _IDL _I32);

HL_PRIM _ref(DebugNavMesh)* HL_NAME(DebugNavMesh_new0)() {
	return alloc_ref((new DebugNavMesh()),DebugNavMesh);
}
DEFINE_PRIM(_IDL, DebugNavMesh_new0,);

HL_PRIM int HL_NAME(DebugNavMesh_getTriangleCount0)(_ref(DebugNavMesh)* _this) {
	return _unref(_this)->getTriangleCount();
}
DEFINE_PRIM(_I32, DebugNavMesh_getTriangleCount0, _IDL);

HL_PRIM HL_CONST _ref(Triangle)* HL_NAME(DebugNavMesh_getTriangle1)(_ref(DebugNavMesh)* _this, int n) {
	return alloc_ref_const(&(_unref(_this)->getTriangle(n)),Triangle);
}
DEFINE_PRIM(_IDL, DebugNavMesh_getTriangle1, _IDL _I32);

HL_PRIM _ref(NavmeshData)* HL_NAME(NavmeshData_new0)() {
	return alloc_ref((new NavmeshData()),NavmeshData);
}
DEFINE_PRIM(_IDL, NavmeshData_new0,);

HL_PRIM void* HL_NAME(NavmeshData_get_dataPointer)( _ref(NavmeshData)* _this ) {
	return _unref(_this)->dataPointer;
}
HL_PRIM void* HL_NAME(NavmeshData_set_dataPointer)( _ref(NavmeshData)* _this, void* value ) {
	_unref(_this)->dataPointer = (value);
	return value;
}
DEFINE_PRIM(_BYTES,NavmeshData_get_dataPointer,_IDL);
DEFINE_PRIM(_BYTES,NavmeshData_set_dataPointer,_IDL _BYTES);

HL_PRIM int HL_NAME(NavmeshData_get_size)( _ref(NavmeshData)* _this ) {
	return _unref(_this)->size;
}
HL_PRIM int HL_NAME(NavmeshData_set_size)( _ref(NavmeshData)* _this, int value ) {
	_unref(_this)->size = (value);
	return value;
}
DEFINE_PRIM(_I32,NavmeshData_get_size,_IDL);
DEFINE_PRIM(_I32,NavmeshData_set_size,_IDL _I32);

HL_PRIM int HL_NAME(NavPath_getPointCount0)(_ref(NavPath)* _this) {
	return _unref(_this)->getPointCount();
}
DEFINE_PRIM(_I32, NavPath_getPointCount0, _IDL);

HL_PRIM HL_CONST _ref(Vec3)* HL_NAME(NavPath_getPoint1)(_ref(NavPath)* _this, int n) {
	return alloc_ref_const(&(_unref(_this)->getPoint(n)),Vec3);
}
DEFINE_PRIM(_IDL, NavPath_getPoint1, _IDL _I32);

HL_PRIM _ref(dtCrowdAgentParams)* HL_NAME(dtCrowdAgentParams_new0)() {
	return alloc_ref((new dtCrowdAgentParams()),dtCrowdAgentParams);
}
DEFINE_PRIM(_IDL, dtCrowdAgentParams_new0,);

HL_PRIM float HL_NAME(dtCrowdAgentParams_get_radius)( _ref(dtCrowdAgentParams)* _this ) {
	return _unref(_this)->radius;
}
HL_PRIM float HL_NAME(dtCrowdAgentParams_set_radius)( _ref(dtCrowdAgentParams)* _this, float value ) {
	_unref(_this)->radius = (value);
	return value;
}
DEFINE_PRIM(_F32,dtCrowdAgentParams_get_radius,_IDL);
DEFINE_PRIM(_F32,dtCrowdAgentParams_set_radius,_IDL _F32);

HL_PRIM float HL_NAME(dtCrowdAgentParams_get_height)( _ref(dtCrowdAgentParams)* _this ) {
	return _unref(_this)->height;
}
HL_PRIM float HL_NAME(dtCrowdAgentParams_set_height)( _ref(dtCrowdAgentParams)* _this, float value ) {
	_unref(_this)->height = (value);
	return value;
}
DEFINE_PRIM(_F32,dtCrowdAgentParams_get_height,_IDL);
DEFINE_PRIM(_F32,dtCrowdAgentParams_set_height,_IDL _F32);

HL_PRIM float HL_NAME(dtCrowdAgentParams_get_maxAcceleration)( _ref(dtCrowdAgentParams)* _this ) {
	return _unref(_this)->maxAcceleration;
}
HL_PRIM float HL_NAME(dtCrowdAgentParams_set_maxAcceleration)( _ref(dtCrowdAgentParams)* _this, float value ) {
	_unref(_this)->maxAcceleration = (value);
	return value;
}
DEFINE_PRIM(_F32,dtCrowdAgentParams_get_maxAcceleration,_IDL);
DEFINE_PRIM(_F32,dtCrowdAgentParams_set_maxAcceleration,_IDL _F32);

HL_PRIM float HL_NAME(dtCrowdAgentParams_get_maxSpeed)( _ref(dtCrowdAgentParams)* _this ) {
	return _unref(_this)->maxSpeed;
}
HL_PRIM float HL_NAME(dtCrowdAgentParams_set_maxSpeed)( _ref(dtCrowdAgentParams)* _this, float value ) {
	_unref(_this)->maxSpeed = (value);
	return value;
}
DEFINE_PRIM(_F32,dtCrowdAgentParams_get_maxSpeed,_IDL);
DEFINE_PRIM(_F32,dtCrowdAgentParams_set_maxSpeed,_IDL _F32);

HL_PRIM float HL_NAME(dtCrowdAgentParams_get_collisionQueryRange)( _ref(dtCrowdAgentParams)* _this ) {
	return _unref(_this)->collisionQueryRange;
}
HL_PRIM float HL_NAME(dtCrowdAgentParams_set_collisionQueryRange)( _ref(dtCrowdAgentParams)* _this, float value ) {
	_unref(_this)->collisionQueryRange = (value);
	return value;
}
DEFINE_PRIM(_F32,dtCrowdAgentParams_get_collisionQueryRange,_IDL);
DEFINE_PRIM(_F32,dtCrowdAgentParams_set_collisionQueryRange,_IDL _F32);

HL_PRIM float HL_NAME(dtCrowdAgentParams_get_pathOptimizationRange)( _ref(dtCrowdAgentParams)* _this ) {
	return _unref(_this)->pathOptimizationRange;
}
HL_PRIM float HL_NAME(dtCrowdAgentParams_set_pathOptimizationRange)( _ref(dtCrowdAgentParams)* _this, float value ) {
	_unref(_this)->pathOptimizationRange = (value);
	return value;
}
DEFINE_PRIM(_F32,dtCrowdAgentParams_get_pathOptimizationRange,_IDL);
DEFINE_PRIM(_F32,dtCrowdAgentParams_set_pathOptimizationRange,_IDL _F32);

HL_PRIM float HL_NAME(dtCrowdAgentParams_get_separationWeight)( _ref(dtCrowdAgentParams)* _this ) {
	return _unref(_this)->separationWeight;
}
HL_PRIM float HL_NAME(dtCrowdAgentParams_set_separationWeight)( _ref(dtCrowdAgentParams)* _this, float value ) {
	_unref(_this)->separationWeight = (value);
	return value;
}
DEFINE_PRIM(_F32,dtCrowdAgentParams_get_separationWeight,_IDL);
DEFINE_PRIM(_F32,dtCrowdAgentParams_set_separationWeight,_IDL _F32);

HL_PRIM int HL_NAME(dtCrowdAgentParams_get_updateFlags)( _ref(dtCrowdAgentParams)* _this ) {
	return _unref(_this)->updateFlags;
}
HL_PRIM int HL_NAME(dtCrowdAgentParams_set_updateFlags)( _ref(dtCrowdAgentParams)* _this, int value ) {
	_unref(_this)->updateFlags = (value);
	return value;
}
DEFINE_PRIM(_I32,dtCrowdAgentParams_get_updateFlags,_IDL);
DEFINE_PRIM(_I32,dtCrowdAgentParams_set_updateFlags,_IDL _I32);

HL_PRIM int HL_NAME(dtCrowdAgentParams_get_obstacleAvoidanceType)( _ref(dtCrowdAgentParams)* _this ) {
	return _unref(_this)->obstacleAvoidanceType;
}
HL_PRIM int HL_NAME(dtCrowdAgentParams_set_obstacleAvoidanceType)( _ref(dtCrowdAgentParams)* _this, int value ) {
	_unref(_this)->obstacleAvoidanceType = (value);
	return value;
}
DEFINE_PRIM(_I32,dtCrowdAgentParams_get_obstacleAvoidanceType,_IDL);
DEFINE_PRIM(_I32,dtCrowdAgentParams_set_obstacleAvoidanceType,_IDL _I32);

HL_PRIM int HL_NAME(dtCrowdAgentParams_get_queryFilterType)( _ref(dtCrowdAgentParams)* _this ) {
	return _unref(_this)->queryFilterType;
}
HL_PRIM int HL_NAME(dtCrowdAgentParams_set_queryFilterType)( _ref(dtCrowdAgentParams)* _this, int value ) {
	_unref(_this)->queryFilterType = (value);
	return value;
}
DEFINE_PRIM(_I32,dtCrowdAgentParams_get_queryFilterType,_IDL);
DEFINE_PRIM(_I32,dtCrowdAgentParams_set_queryFilterType,_IDL _I32);

HL_PRIM _ref(NavMesh)* HL_NAME(NavMesh_new0)() {
	return alloc_ref((new NavMesh()),NavMesh);
}
DEFINE_PRIM(_IDL, NavMesh_new0,);

HL_PRIM void HL_NAME(NavMesh_destroy0)(_ref(NavMesh)* _this) {
	_unref(_this)->destroy();
}
DEFINE_PRIM(_VOID, NavMesh_destroy0, _IDL);

HL_PRIM void HL_NAME(NavMesh_build5)(_ref(NavMesh)* _this, float* positions, int positionCount, int* indices, int indexCount, _ref(rcConfig)* config) {
	_unref(_this)->build(positions, positionCount, indices, indexCount, *_unref(config));
}
DEFINE_PRIM(_VOID, NavMesh_build5, _IDL _BYTES _I32 _BYTES _I32 _IDL);

HL_PRIM void HL_NAME(NavMesh_buildFromNavmeshData1)(_ref(NavMesh)* _this, _ref(NavmeshData)* data) {
	_unref(_this)->buildFromNavmeshData(_unref(data));
}
DEFINE_PRIM(_VOID, NavMesh_buildFromNavmeshData1, _IDL _IDL);

HL_PRIM _ref(NavmeshData)* HL_NAME(NavMesh_getNavmeshData0)(_ref(NavMesh)* _this) {
	return alloc_ref(new NavmeshData(_unref(_this)->getNavmeshData()),NavmeshData);
}
DEFINE_PRIM(_IDL, NavMesh_getNavmeshData0, _IDL);

HL_PRIM void HL_NAME(NavMesh_freeNavmeshData1)(_ref(NavMesh)* _this, _ref(NavmeshData)* data) {
	_unref(_this)->freeNavmeshData(_unref(data));
}
DEFINE_PRIM(_VOID, NavMesh_freeNavmeshData1, _IDL _IDL);

HL_PRIM _ref(DebugNavMesh)* HL_NAME(NavMesh_getDebugNavMesh0)(_ref(NavMesh)* _this) {
	return alloc_ref(new DebugNavMesh(_unref(_this)->getDebugNavMesh()),DebugNavMesh);
}
DEFINE_PRIM(_IDL, NavMesh_getDebugNavMesh0, _IDL);

HL_PRIM _ref(Vec3)* HL_NAME(NavMesh_getClosestPoint1)(_ref(NavMesh)* _this, _ref(Vec3)* position) {
	return alloc_ref(new Vec3(_unref(_this)->getClosestPoint(*_unref(position))),Vec3);
}
DEFINE_PRIM(_IDL, NavMesh_getClosestPoint1, _IDL _IDL);

HL_PRIM _ref(Vec3)* HL_NAME(NavMesh_getRandomPointAround2)(_ref(NavMesh)* _this, _ref(Vec3)* position, float maxRadius) {
	return alloc_ref(new Vec3(_unref(_this)->getRandomPointAround(*_unref(position), maxRadius)),Vec3);
}
DEFINE_PRIM(_IDL, NavMesh_getRandomPointAround2, _IDL _IDL _F32);

HL_PRIM _ref(Vec3)* HL_NAME(NavMesh_moveAlong2)(_ref(NavMesh)* _this, _ref(Vec3)* position, _ref(Vec3)* destination) {
	return alloc_ref(new Vec3(_unref(_this)->moveAlong(*_unref(position), *_unref(destination))),Vec3);
}
DEFINE_PRIM(_IDL, NavMesh_moveAlong2, _IDL _IDL _IDL);

HL_PRIM _ref(dtNavMesh)* HL_NAME(NavMesh_getNavMesh0)(_ref(NavMesh)* _this) {
	return alloc_ref((_unref(_this)->getNavMesh()),dtNavMesh);
}
DEFINE_PRIM(_IDL, NavMesh_getNavMesh0, _IDL);

HL_PRIM _ref(NavPath)* HL_NAME(NavMesh_computePath2)(_ref(NavMesh)* _this, _ref(Vec3)* start, _ref(Vec3)* end) {
	return alloc_ref(new NavPath(_unref(_this)->computePath(*_unref(start), *_unref(end))),NavPath);
}
DEFINE_PRIM(_IDL, NavMesh_computePath2, _IDL _IDL _IDL);

HL_PRIM void HL_NAME(NavMesh_setDefaultQueryExtent1)(_ref(NavMesh)* _this, _ref(Vec3)* extent) {
	_unref(_this)->setDefaultQueryExtent(*_unref(extent));
}
DEFINE_PRIM(_VOID, NavMesh_setDefaultQueryExtent1, _IDL _IDL);

HL_PRIM _ref(Vec3)* HL_NAME(NavMesh_getDefaultQueryExtent0)(_ref(NavMesh)* _this) {
	return alloc_ref(new Vec3(_unref(_this)->getDefaultQueryExtent()),Vec3);
}
DEFINE_PRIM(_IDL, NavMesh_getDefaultQueryExtent0, _IDL);

HL_PRIM _ref(dtObstacleRef)* HL_NAME(NavMesh_addCylinderObstacle3)(_ref(NavMesh)* _this, _ref(Vec3)* position, float radius, float height) {
	return alloc_ref((_unref(_this)->addCylinderObstacle(*_unref(position), radius, height)),dtObstacleRef);
}
DEFINE_PRIM(_IDL, NavMesh_addCylinderObstacle3, _IDL _IDL _F32 _F32);

HL_PRIM _ref(dtObstacleRef)* HL_NAME(NavMesh_addBoxObstacle3)(_ref(NavMesh)* _this, _ref(Vec3)* position, _ref(Vec3)* extent, float angle) {
	return alloc_ref((_unref(_this)->addBoxObstacle(*_unref(position), *_unref(extent), angle)),dtObstacleRef);
}
DEFINE_PRIM(_IDL, NavMesh_addBoxObstacle3, _IDL _IDL _IDL _F32);

HL_PRIM void HL_NAME(NavMesh_removeObstacle1)(_ref(NavMesh)* _this, _ref(dtObstacleRef)* obstacle) {
	_unref(_this)->removeObstacle(_unref(obstacle));
}
DEFINE_PRIM(_VOID, NavMesh_removeObstacle1, _IDL _IDL);

HL_PRIM void HL_NAME(NavMesh_update0)(_ref(NavMesh)* _this) {
	_unref(_this)->update();
}
DEFINE_PRIM(_VOID, NavMesh_update0, _IDL);

HL_PRIM _ref(Crowd)* HL_NAME(Crowd_new3)(int maxAgents, float maxAgentRadius, _ref(dtNavMesh)* nav) {
	return alloc_ref((new Crowd(maxAgents, maxAgentRadius, _unref(nav))),Crowd);
}
DEFINE_PRIM(_IDL, Crowd_new3, _I32 _F32 _IDL);

HL_PRIM void HL_NAME(Crowd_destroy0)(_ref(Crowd)* _this) {
	_unref(_this)->destroy();
}
DEFINE_PRIM(_VOID, Crowd_destroy0, _IDL);

HL_PRIM int HL_NAME(Crowd_addAgent2)(_ref(Crowd)* _this, _ref(Vec3)* position, _ref(dtCrowdAgentParams)* params) {
	return _unref(_this)->addAgent(*_unref(position), _unref(params));
}
DEFINE_PRIM(_I32, Crowd_addAgent2, _IDL _IDL _IDL);

HL_PRIM void HL_NAME(Crowd_removeAgent1)(_ref(Crowd)* _this, int idx) {
	_unref(_this)->removeAgent(idx);
}
DEFINE_PRIM(_VOID, Crowd_removeAgent1, _IDL _I32);

HL_PRIM void HL_NAME(Crowd_update1)(_ref(Crowd)* _this, float dt) {
	_unref(_this)->update(dt);
}
DEFINE_PRIM(_VOID, Crowd_update1, _IDL _F32);

HL_PRIM _ref(Vec3)* HL_NAME(Crowd_getAgentPosition1)(_ref(Crowd)* _this, int idx) {
	return alloc_ref(new Vec3(_unref(_this)->getAgentPosition(idx)),Vec3);
}
DEFINE_PRIM(_IDL, Crowd_getAgentPosition1, _IDL _I32);

HL_PRIM _ref(Vec3)* HL_NAME(Crowd_getAgentVelocity1)(_ref(Crowd)* _this, int idx) {
	return alloc_ref(new Vec3(_unref(_this)->getAgentVelocity(idx)),Vec3);
}
DEFINE_PRIM(_IDL, Crowd_getAgentVelocity1, _IDL _I32);

HL_PRIM _ref(Vec3)* HL_NAME(Crowd_getAgentNextTargetPath1)(_ref(Crowd)* _this, int idx) {
	return alloc_ref(new Vec3(_unref(_this)->getAgentNextTargetPath(idx)),Vec3);
}
DEFINE_PRIM(_IDL, Crowd_getAgentNextTargetPath1, _IDL _I32);

HL_PRIM int HL_NAME(Crowd_getAgentState1)(_ref(Crowd)* _this, int idx) {
	return _unref(_this)->getAgentState(idx);
}
DEFINE_PRIM(_I32, Crowd_getAgentState1, _IDL _I32);

HL_PRIM bool HL_NAME(Crowd_overOffmeshConnection1)(_ref(Crowd)* _this, int idx) {
	return _unref(_this)->overOffmeshConnection(idx);
}
DEFINE_PRIM(_BOOL, Crowd_overOffmeshConnection1, _IDL _I32);

HL_PRIM void HL_NAME(Crowd_agentGoto2)(_ref(Crowd)* _this, int idx, _ref(Vec3)* destination) {
	_unref(_this)->agentGoto(idx, *_unref(destination));
}
DEFINE_PRIM(_VOID, Crowd_agentGoto2, _IDL _I32 _IDL);

HL_PRIM void HL_NAME(Crowd_agentTeleport2)(_ref(Crowd)* _this, int idx, _ref(Vec3)* destination) {
	_unref(_this)->agentTeleport(idx, *_unref(destination));
}
DEFINE_PRIM(_VOID, Crowd_agentTeleport2, _IDL _I32 _IDL);

HL_PRIM _ref(dtCrowdAgentParams)* HL_NAME(Crowd_getAgentParameters1)(_ref(Crowd)* _this, int idx) {
	return alloc_ref(new dtCrowdAgentParams(_unref(_this)->getAgentParameters(idx)),dtCrowdAgentParams);
}
DEFINE_PRIM(_IDL, Crowd_getAgentParameters1, _IDL _I32);

HL_PRIM void HL_NAME(Crowd_setAgentParameters2)(_ref(Crowd)* _this, int idx, _ref(dtCrowdAgentParams)* params) {
	_unref(_this)->setAgentParameters(idx, _unref(params));
}
DEFINE_PRIM(_VOID, Crowd_setAgentParameters2, _IDL _I32 _IDL);

HL_PRIM void HL_NAME(Crowd_setDefaultQueryExtent1)(_ref(Crowd)* _this, _ref(Vec3)* extent) {
	_unref(_this)->setDefaultQueryExtent(*_unref(extent));
}
DEFINE_PRIM(_VOID, Crowd_setDefaultQueryExtent1, _IDL _IDL);

HL_PRIM _ref(Vec3)* HL_NAME(Crowd_getDefaultQueryExtent0)(_ref(Crowd)* _this) {
	return alloc_ref(new Vec3(_unref(_this)->getDefaultQueryExtent()),Vec3);
}
DEFINE_PRIM(_IDL, Crowd_getDefaultQueryExtent0, _IDL);

HL_PRIM _ref(NavPath)* HL_NAME(Crowd_getCorners1)(_ref(Crowd)* _this, int idx) {
	return alloc_ref(new NavPath(_unref(_this)->getCorners(idx)),NavPath);
}
DEFINE_PRIM(_IDL, Crowd_getCorners1, _IDL _I32);

HL_PRIM _ref(RecastConfigHelper)* HL_NAME(RecastConfigHelper_new0)() {
	return alloc_ref((new RecastConfigHelper()),RecastConfigHelper);
}
DEFINE_PRIM(_IDL, RecastConfigHelper_new0,);

HL_PRIM void HL_NAME(RecastConfigHelper_setBMAX4)(_ref(RecastConfigHelper)* _this, _ref(rcConfig)* config, float x, float y, float z) {
	_unref(_this)->setBMAX(*_unref(config), x, y, z);
}
DEFINE_PRIM(_VOID, RecastConfigHelper_setBMAX4, _IDL _IDL _F32 _F32 _F32);

HL_PRIM void HL_NAME(RecastConfigHelper_setBMIN4)(_ref(RecastConfigHelper)* _this, _ref(rcConfig)* config, float x, float y, float z) {
	_unref(_this)->setBMIN(*_unref(config), x, y, z);
}
DEFINE_PRIM(_VOID, RecastConfigHelper_setBMIN4, _IDL _IDL _F32 _F32 _F32);

HL_PRIM _ref(Vec3)* HL_NAME(RecastConfigHelper_getBMAX1)(_ref(RecastConfigHelper)* _this, _ref(rcConfig)* config) {
	return alloc_ref(new Vec3(_unref(_this)->getBMAX(*_unref(config))),Vec3);
}
DEFINE_PRIM(_IDL, RecastConfigHelper_getBMAX1, _IDL _IDL);

HL_PRIM _ref(Vec3)* HL_NAME(RecastConfigHelper_getBMIN1)(_ref(RecastConfigHelper)* _this, _ref(rcConfig)* config) {
	return alloc_ref(new Vec3(_unref(_this)->getBMIN(*_unref(config))),Vec3);
}
DEFINE_PRIM(_IDL, RecastConfigHelper_getBMIN1, _IDL _IDL);

HL_PRIM float* HL_NAME(rcFloatArray_get_raw)( _ref(rcFloatArray)* _this ) {
	return _unref(_this)->raw;
}
HL_PRIM float* HL_NAME(rcFloatArray_set_raw)( _ref(rcFloatArray)* _this, float* value ) {
	_unref(_this)->raw = (value);
	return value;
}
DEFINE_PRIM(_BYTES,rcFloatArray_get_raw,_IDL);
DEFINE_PRIM(_BYTES,rcFloatArray_set_raw,_IDL _BYTES);

HL_PRIM _ref(rcFloatArray)* HL_NAME(rcFloatArray_new1)(int num) {
	return alloc_ref((new rcFloatArray(num)),rcFloatArray);
}
DEFINE_PRIM(_IDL, rcFloatArray_new1, _I32);

HL_PRIM HL_CONST int HL_NAME(rcFloatArray_size0)(_ref(rcFloatArray)* _this) {
	return _unref(_this)->size();
}
DEFINE_PRIM(_I32, rcFloatArray_size0, _IDL);

HL_PRIM HL_CONST float HL_NAME(rcFloatArray_at1)(_ref(rcFloatArray)* _this, int n) {
	return _unref(_this)->at(n);
}
DEFINE_PRIM(_F32, rcFloatArray_at1, _IDL _I32);

HL_PRIM HL_CONST int HL_NAME(rcFloatArray_set2)(_ref(rcFloatArray)* _this, int n, float value) {
	return _unref(_this)->set(n, value);
}
DEFINE_PRIM(_I32, rcFloatArray_set2, _IDL _I32 _F32);

HL_PRIM int* HL_NAME(rcIntArray_get_raw)( _ref(rcIntArray)* _this ) {
	return _unref(_this)->raw;
}
HL_PRIM int* HL_NAME(rcIntArray_set_raw)( _ref(rcIntArray)* _this, int* value ) {
	_unref(_this)->raw = (value);
	return value;
}
DEFINE_PRIM(_BYTES,rcIntArray_get_raw,_IDL);
DEFINE_PRIM(_BYTES,rcIntArray_set_raw,_IDL _BYTES);

HL_PRIM _ref(rcIntArray)* HL_NAME(rcIntArray_new1)(int num) {
	return alloc_ref((new rcIntArray(num)),rcIntArray);
}
DEFINE_PRIM(_IDL, rcIntArray_new1, _I32);

HL_PRIM HL_CONST int HL_NAME(rcIntArray_size0)(_ref(rcIntArray)* _this) {
	return _unref(_this)->size();
}
DEFINE_PRIM(_I32, rcIntArray_size0, _IDL);

HL_PRIM HL_CONST int HL_NAME(rcIntArray_at1)(_ref(rcIntArray)* _this, int n) {
	return _unref(_this)->at(n);
}
DEFINE_PRIM(_I32, rcIntArray_at1, _IDL _I32);

HL_PRIM HL_CONST int HL_NAME(rcIntArray_set2)(_ref(rcIntArray)* _this, int n, int value) {
	return _unref(_this)->set(n, value);
}
DEFINE_PRIM(_I32, rcIntArray_set2, _IDL _I32 _I32);

}
