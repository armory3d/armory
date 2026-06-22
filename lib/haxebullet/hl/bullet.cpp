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

#define HL_NAME(x) bullet_##x
#include <hl.h>
#define _IDL _BYTES
#define _OPT(t) vdynamic *
#define _GET_OPT(value,t) (value)->v.t

// template <typename T> struct pref {
// 	void *finalize;
// 	T *value;
// };

// #define _ref(t) pref<t>
// #define _unref(v) v->value
// #define alloc_ref(r,t) _alloc_ref(r,finalize_##t)
// #define alloc_ref_const(r, _) _alloc_const(r)
// #define HL_CONST

// template<typename T> void free_ref( pref<T> *r ) {
// 	if( !r->finalize ) return;
// 	delete r->value;
// 	r->value = NULL;
// 	r->finalize = NULL;
// }

// template<typename T> pref<T> *_alloc_ref( T *value, void (*finalize)( pref<T> * ) ) {
// 	pref<T> *r = (pref<T>*)hl_gc_alloc_finalizer(sizeof(r));
// 	r->finalize = finalize;
// 	r->value = value;
// 	return r;
// }

// template<typename T> pref<T> *_alloc_const( const T *value ) {
// 	pref<T> *r = (pref<T>*)hl_gc_alloc_noptr(sizeof(r));
// 	r->finalize = NULL;
// 	r->value = (T*)value;
// 	return r;
// }
#define alloc_ref(r, _) r
#define alloc_ref_const(r,_) r
#define _ref(t)			t
#define _unref(v)		v
#define free_ref(v) delete (v)
#define HL_CONST const

#endif

#ifdef _WIN32
#pragma warning(disable:4305)
#pragma warning(disable:4244)
#pragma warning(disable:4316)
#endif
#include <btBulletDynamicsCommon.h>
#include <BulletSoftBody/btSoftBody.h>
#include <BulletSoftBody/btSoftBodyRigidBodyCollisionConfiguration.h>
#include <BulletSoftBody/btDefaultSoftBodySolver.h>
#include <BulletSoftBody/btSoftBodyHelpers.h>
#include <BulletSoftBody/btSoftRigidDynamicsWorld.h>
#include <BulletCollision/CollisionShapes/btHeightfieldTerrainShape.h>
#include <BulletCollision/CollisionDispatch/btGhostObject.h>
#include <BulletDynamics/Character/btKinematicCharacterController.h>
#include <BulletCollision/Gimpact/btGImpactShape.h>
#include <BulletCollision/Gimpact/btGImpactCollisionAlgorithm.h>

#include <btCustomArray.h>

extern "C" {

static void finalize_btVector3( _ref(btVector3)* _this ) { free_ref(_this); }
HL_PRIM void HL_NAME(btVector3_delete)( _ref(btVector3)* _this ) {
	free_ref(_this);
}
DEFINE_PRIM(_VOID, btVector3_delete, _IDL);
static void finalize_btVector4( _ref(btVector4)* _this ) { free_ref(_this); }
HL_PRIM void HL_NAME(btVector4_delete)( _ref(btVector4)* _this ) {
	free_ref(_this);
}
DEFINE_PRIM(_VOID, btVector4_delete, _IDL);
static void finalize_btQuadWord( _ref(btQuadWord)* _this ) { free_ref(_this); }
HL_PRIM void HL_NAME(btQuadWord_delete)( _ref(btQuadWord)* _this ) {
	free_ref(_this);
}
DEFINE_PRIM(_VOID, btQuadWord_delete, _IDL);
static void finalize_btQuaternion( _ref(btQuaternion)* _this ) { free_ref(_this); }
HL_PRIM void HL_NAME(btQuaternion_delete)( _ref(btQuaternion)* _this ) {
	free_ref(_this);
}
DEFINE_PRIM(_VOID, btQuaternion_delete, _IDL);
static void finalize_btMatrix3x3( _ref(btMatrix3x3)* _this ) { free_ref(_this); }
HL_PRIM void HL_NAME(btMatrix3x3_delete)( _ref(btMatrix3x3)* _this ) {
	free_ref(_this);
}
DEFINE_PRIM(_VOID, btMatrix3x3_delete, _IDL);
static void finalize_btTransform( _ref(btTransform)* _this ) { free_ref(_this); }
HL_PRIM void HL_NAME(btTransform_delete)( _ref(btTransform)* _this ) {
	free_ref(_this);
}
DEFINE_PRIM(_VOID, btTransform_delete, _IDL);
static void finalize_btMotionState( _ref(btMotionState)* _this ) { free_ref(_this); }
HL_PRIM void HL_NAME(btMotionState_delete)( _ref(btMotionState)* _this ) {
	free_ref(_this);
}
DEFINE_PRIM(_VOID, btMotionState_delete, _IDL);
static void finalize_btDefaultMotionState( _ref(btDefaultMotionState)* _this ) { free_ref(_this); }
HL_PRIM void HL_NAME(btDefaultMotionState_delete)( _ref(btDefaultMotionState)* _this ) {
	free_ref(_this);
}
DEFINE_PRIM(_VOID, btDefaultMotionState_delete, _IDL);
static void finalize_btCollisionObject( _ref(btCollisionObject)* _this ) { free_ref(_this); }
HL_PRIM void HL_NAME(btCollisionObject_delete)( _ref(btCollisionObject)* _this ) {
	free_ref(_this);
}
DEFINE_PRIM(_VOID, btCollisionObject_delete, _IDL);
static void finalize_RayResultCallback( _ref(btCollisionWorld::RayResultCallback)* _this ) { free_ref(_this); }
HL_PRIM void HL_NAME(RayResultCallback_delete)( _ref(btCollisionWorld::RayResultCallback)* _this ) {
	free_ref(_this);
}
DEFINE_PRIM(_VOID, RayResultCallback_delete, _IDL);
static void finalize_ClosestRayResultCallback( _ref(btCollisionWorld::ClosestRayResultCallback)* _this ) { free_ref(_this); }
HL_PRIM void HL_NAME(ClosestRayResultCallback_delete)( _ref(btCollisionWorld::ClosestRayResultCallback)* _this ) {
	free_ref(_this);
}
DEFINE_PRIM(_VOID, ClosestRayResultCallback_delete, _IDL);
static void finalize_btManifoldPoint( _ref(btManifoldPoint)* _this ) { free_ref(_this); }
HL_PRIM void HL_NAME(btManifoldPoint_delete)( _ref(btManifoldPoint)* _this ) {
	free_ref(_this);
}
DEFINE_PRIM(_VOID, btManifoldPoint_delete, _IDL);
static void finalize_ContactResultCallback( _ref(btCollisionWorld::ContactResultCallback)* _this ) { free_ref(_this); }
HL_PRIM void HL_NAME(ContactResultCallback_delete)( _ref(btCollisionWorld::ContactResultCallback)* _this ) {
	free_ref(_this);
}
DEFINE_PRIM(_VOID, ContactResultCallback_delete, _IDL);
static void finalize_LocalShapeInfo( _ref(btCollisionWorld::LocalShapeInfo)* _this ) { free_ref(_this); }
HL_PRIM void HL_NAME(LocalShapeInfo_delete)( _ref(btCollisionWorld::LocalShapeInfo)* _this ) {
	free_ref(_this);
}
DEFINE_PRIM(_VOID, LocalShapeInfo_delete, _IDL);
static void finalize_LocalConvexResult( _ref(btCollisionWorld::LocalConvexResult)* _this ) { free_ref(_this); }
HL_PRIM void HL_NAME(LocalConvexResult_delete)( _ref(btCollisionWorld::LocalConvexResult)* _this ) {
	free_ref(_this);
}
DEFINE_PRIM(_VOID, LocalConvexResult_delete, _IDL);
static void finalize_ConvexResultCallback( _ref(btCollisionWorld::ConvexResultCallback)* _this ) { free_ref(_this); }
HL_PRIM void HL_NAME(ConvexResultCallback_delete)( _ref(btCollisionWorld::ConvexResultCallback)* _this ) {
	free_ref(_this);
}
DEFINE_PRIM(_VOID, ConvexResultCallback_delete, _IDL);
static void finalize_ClosestConvexResultCallback( _ref(btCollisionWorld::ClosestConvexResultCallback)* _this ) { free_ref(_this); }
HL_PRIM void HL_NAME(ClosestConvexResultCallback_delete)( _ref(btCollisionWorld::ClosestConvexResultCallback)* _this ) {
	free_ref(_this);
}
DEFINE_PRIM(_VOID, ClosestConvexResultCallback_delete, _IDL);
static void finalize_btCollisionShape( _ref(btCollisionShape)* _this ) { free_ref(_this); }
HL_PRIM void HL_NAME(btCollisionShape_delete)( _ref(btCollisionShape)* _this ) {
	free_ref(_this);
}
DEFINE_PRIM(_VOID, btCollisionShape_delete, _IDL);
static void finalize_btConvexShape( _ref(btConvexShape)* _this ) { free_ref(_this); }
HL_PRIM void HL_NAME(btConvexShape_delete)( _ref(btConvexShape)* _this ) {
	free_ref(_this);
}
DEFINE_PRIM(_VOID, btConvexShape_delete, _IDL);
static void finalize_btConvexTriangleMeshShape( _ref(btConvexTriangleMeshShape)* _this ) { free_ref(_this); }
HL_PRIM void HL_NAME(btConvexTriangleMeshShape_delete)( _ref(btConvexTriangleMeshShape)* _this ) {
	free_ref(_this);
}
DEFINE_PRIM(_VOID, btConvexTriangleMeshShape_delete, _IDL);
static void finalize_btBoxShape( _ref(btBoxShape)* _this ) { free_ref(_this); }
HL_PRIM void HL_NAME(btBoxShape_delete)( _ref(btBoxShape)* _this ) {
	free_ref(_this);
}
DEFINE_PRIM(_VOID, btBoxShape_delete, _IDL);
static void finalize_btCapsuleShape( _ref(btCapsuleShape)* _this ) { free_ref(_this); }
HL_PRIM void HL_NAME(btCapsuleShape_delete)( _ref(btCapsuleShape)* _this ) {
	free_ref(_this);
}
DEFINE_PRIM(_VOID, btCapsuleShape_delete, _IDL);
static void finalize_btCapsuleShapeX( _ref(btCapsuleShapeX)* _this ) { free_ref(_this); }
HL_PRIM void HL_NAME(btCapsuleShapeX_delete)( _ref(btCapsuleShapeX)* _this ) {
	free_ref(_this);
}
DEFINE_PRIM(_VOID, btCapsuleShapeX_delete, _IDL);
static void finalize_btCapsuleShapeZ( _ref(btCapsuleShapeZ)* _this ) { free_ref(_this); }
HL_PRIM void HL_NAME(btCapsuleShapeZ_delete)( _ref(btCapsuleShapeZ)* _this ) {
	free_ref(_this);
}
DEFINE_PRIM(_VOID, btCapsuleShapeZ_delete, _IDL);
static void finalize_btCylinderShape( _ref(btCylinderShape)* _this ) { free_ref(_this); }
HL_PRIM void HL_NAME(btCylinderShape_delete)( _ref(btCylinderShape)* _this ) {
	free_ref(_this);
}
DEFINE_PRIM(_VOID, btCylinderShape_delete, _IDL);
static void finalize_btCylinderShapeX( _ref(btCylinderShapeX)* _this ) { free_ref(_this); }
HL_PRIM void HL_NAME(btCylinderShapeX_delete)( _ref(btCylinderShapeX)* _this ) {
	free_ref(_this);
}
DEFINE_PRIM(_VOID, btCylinderShapeX_delete, _IDL);
static void finalize_btCylinderShapeZ( _ref(btCylinderShapeZ)* _this ) { free_ref(_this); }
HL_PRIM void HL_NAME(btCylinderShapeZ_delete)( _ref(btCylinderShapeZ)* _this ) {
	free_ref(_this);
}
DEFINE_PRIM(_VOID, btCylinderShapeZ_delete, _IDL);
static void finalize_btSphereShape( _ref(btSphereShape)* _this ) { free_ref(_this); }
HL_PRIM void HL_NAME(btSphereShape_delete)( _ref(btSphereShape)* _this ) {
	free_ref(_this);
}
DEFINE_PRIM(_VOID, btSphereShape_delete, _IDL);
static void finalize_btConeShape( _ref(btConeShape)* _this ) { free_ref(_this); }
HL_PRIM void HL_NAME(btConeShape_delete)( _ref(btConeShape)* _this ) {
	free_ref(_this);
}
DEFINE_PRIM(_VOID, btConeShape_delete, _IDL);
static void finalize_btConvexHullShape( _ref(btConvexHullShape)* _this ) { free_ref(_this); }
HL_PRIM void HL_NAME(btConvexHullShape_delete)( _ref(btConvexHullShape)* _this ) {
	free_ref(_this);
}
DEFINE_PRIM(_VOID, btConvexHullShape_delete, _IDL);
static void finalize_btConeShapeX( _ref(btConeShapeX)* _this ) { free_ref(_this); }
HL_PRIM void HL_NAME(btConeShapeX_delete)( _ref(btConeShapeX)* _this ) {
	free_ref(_this);
}
DEFINE_PRIM(_VOID, btConeShapeX_delete, _IDL);
static void finalize_btConeShapeZ( _ref(btConeShapeZ)* _this ) { free_ref(_this); }
HL_PRIM void HL_NAME(btConeShapeZ_delete)( _ref(btConeShapeZ)* _this ) {
	free_ref(_this);
}
DEFINE_PRIM(_VOID, btConeShapeZ_delete, _IDL);
static void finalize_btCompoundShape( _ref(btCompoundShape)* _this ) { free_ref(_this); }
HL_PRIM void HL_NAME(btCompoundShape_delete)( _ref(btCompoundShape)* _this ) {
	free_ref(_this);
}
DEFINE_PRIM(_VOID, btCompoundShape_delete, _IDL);
static void finalize_btStridingMeshInterface( _ref(btStridingMeshInterface)* _this ) { free_ref(_this); }
HL_PRIM void HL_NAME(btStridingMeshInterface_delete)( _ref(btStridingMeshInterface)* _this ) {
	free_ref(_this);
}
DEFINE_PRIM(_VOID, btStridingMeshInterface_delete, _IDL);
static void finalize_btTriangleMesh( _ref(btTriangleMesh)* _this ) { free_ref(_this); }
HL_PRIM void HL_NAME(btTriangleMesh_delete)( _ref(btTriangleMesh)* _this ) {
	free_ref(_this);
}
DEFINE_PRIM(_VOID, btTriangleMesh_delete, _IDL);
static PHY_ScalarType PHY_ScalarType__values[] = { PHY_FLOAT,PHY_DOUBLE,PHY_INTEGER,PHY_SHORT,PHY_FIXEDPOINT88,PHY_UCHAR };
static void finalize_btConcaveShape( _ref(btConcaveShape)* _this ) { free_ref(_this); }
HL_PRIM void HL_NAME(btConcaveShape_delete)( _ref(btConcaveShape)* _this ) {
	free_ref(_this);
}
DEFINE_PRIM(_VOID, btConcaveShape_delete, _IDL);
static void finalize_btStaticPlaneShape( _ref(btStaticPlaneShape)* _this ) { free_ref(_this); }
HL_PRIM void HL_NAME(btStaticPlaneShape_delete)( _ref(btStaticPlaneShape)* _this ) {
	free_ref(_this);
}
DEFINE_PRIM(_VOID, btStaticPlaneShape_delete, _IDL);
static void finalize_btTriangleMeshShape( _ref(btTriangleMeshShape)* _this ) { free_ref(_this); }
HL_PRIM void HL_NAME(btTriangleMeshShape_delete)( _ref(btTriangleMeshShape)* _this ) {
	free_ref(_this);
}
DEFINE_PRIM(_VOID, btTriangleMeshShape_delete, _IDL);
static void finalize_btBvhTriangleMeshShape( _ref(btBvhTriangleMeshShape)* _this ) { free_ref(_this); }
HL_PRIM void HL_NAME(btBvhTriangleMeshShape_delete)( _ref(btBvhTriangleMeshShape)* _this ) {
	free_ref(_this);
}
DEFINE_PRIM(_VOID, btBvhTriangleMeshShape_delete, _IDL);
static void finalize_btHeightfieldTerrainShape( _ref(btHeightfieldTerrainShape)* _this ) { free_ref(_this); }
HL_PRIM void HL_NAME(btHeightfieldTerrainShape_delete)( _ref(btHeightfieldTerrainShape)* _this ) {
	free_ref(_this);
}
DEFINE_PRIM(_VOID, btHeightfieldTerrainShape_delete, _IDL);
static void finalize_btGImpactMeshShape( _ref(btGImpactMeshShape)* _this ) { free_ref(_this); }
HL_PRIM void HL_NAME(btGImpactMeshShape_delete)( _ref(btGImpactMeshShape)* _this ) {
	free_ref(_this);
}
DEFINE_PRIM(_VOID, btGImpactMeshShape_delete, _IDL);
static void finalize_btDefaultCollisionConstructionInfo( _ref(btDefaultCollisionConstructionInfo)* _this ) { free_ref(_this); }
HL_PRIM void HL_NAME(btDefaultCollisionConstructionInfo_delete)( _ref(btDefaultCollisionConstructionInfo)* _this ) {
	free_ref(_this);
}
DEFINE_PRIM(_VOID, btDefaultCollisionConstructionInfo_delete, _IDL);
static void finalize_btDefaultCollisionConfiguration( _ref(btDefaultCollisionConfiguration)* _this ) { free_ref(_this); }
HL_PRIM void HL_NAME(btDefaultCollisionConfiguration_delete)( _ref(btDefaultCollisionConfiguration)* _this ) {
	free_ref(_this);
}
DEFINE_PRIM(_VOID, btDefaultCollisionConfiguration_delete, _IDL);
static void finalize_btPersistentManifold( _ref(btPersistentManifold)* _this ) { free_ref(_this); }
HL_PRIM void HL_NAME(btPersistentManifold_delete)( _ref(btPersistentManifold)* _this ) {
	free_ref(_this);
}
DEFINE_PRIM(_VOID, btPersistentManifold_delete, _IDL);
static void finalize_btDispatcher( _ref(btDispatcher)* _this ) { free_ref(_this); }
HL_PRIM void HL_NAME(btDispatcher_delete)( _ref(btDispatcher)* _this ) {
	free_ref(_this);
}
DEFINE_PRIM(_VOID, btDispatcher_delete, _IDL);
static void finalize_btCollisionDispatcher( _ref(btCollisionDispatcher)* _this ) { free_ref(_this); }
HL_PRIM void HL_NAME(btCollisionDispatcher_delete)( _ref(btCollisionDispatcher)* _this ) {
	free_ref(_this);
}
DEFINE_PRIM(_VOID, btCollisionDispatcher_delete, _IDL);
static void finalize_btOverlappingPairCallback( _ref(btOverlappingPairCallback)* _this ) { free_ref(_this); }
HL_PRIM void HL_NAME(btOverlappingPairCallback_delete)( _ref(btOverlappingPairCallback)* _this ) {
	free_ref(_this);
}
DEFINE_PRIM(_VOID, btOverlappingPairCallback_delete, _IDL);
static void finalize_btOverlappingPairCache( _ref(btOverlappingPairCache)* _this ) { free_ref(_this); }
HL_PRIM void HL_NAME(btOverlappingPairCache_delete)( _ref(btOverlappingPairCache)* _this ) {
	free_ref(_this);
}
DEFINE_PRIM(_VOID, btOverlappingPairCache_delete, _IDL);
static void finalize_btAxisSweep3( _ref(btAxisSweep3)* _this ) { free_ref(_this); }
HL_PRIM void HL_NAME(btAxisSweep3_delete)( _ref(btAxisSweep3)* _this ) {
	free_ref(_this);
}
DEFINE_PRIM(_VOID, btAxisSweep3_delete, _IDL);
static void finalize_btBroadphaseInterface( _ref(btBroadphaseInterface)* _this ) { free_ref(_this); }
HL_PRIM void HL_NAME(btBroadphaseInterface_delete)( _ref(btBroadphaseInterface)* _this ) {
	free_ref(_this);
}
DEFINE_PRIM(_VOID, btBroadphaseInterface_delete, _IDL);
static void finalize_btCollisionConfiguration( _ref(btCollisionConfiguration)* _this ) { free_ref(_this); }
HL_PRIM void HL_NAME(btCollisionConfiguration_delete)( _ref(btCollisionConfiguration)* _this ) {
	free_ref(_this);
}
DEFINE_PRIM(_VOID, btCollisionConfiguration_delete, _IDL);
static void finalize_btDbvtBroadphase( _ref(btDbvtBroadphase)* _this ) { free_ref(_this); }
HL_PRIM void HL_NAME(btDbvtBroadphase_delete)( _ref(btDbvtBroadphase)* _this ) {
	free_ref(_this);
}
DEFINE_PRIM(_VOID, btDbvtBroadphase_delete, _IDL);
static void finalize_btRigidBodyConstructionInfo( _ref(btRigidBody::btRigidBodyConstructionInfo)* _this ) { free_ref(_this); }
HL_PRIM void HL_NAME(btRigidBodyConstructionInfo_delete)( _ref(btRigidBody::btRigidBodyConstructionInfo)* _this ) {
	free_ref(_this);
}
DEFINE_PRIM(_VOID, btRigidBodyConstructionInfo_delete, _IDL);
static void finalize_btRigidBody( _ref(btRigidBody)* _this ) { free_ref(_this); }
HL_PRIM void HL_NAME(btRigidBody_delete)( _ref(btRigidBody)* _this ) {
	free_ref(_this);
}
DEFINE_PRIM(_VOID, btRigidBody_delete, _IDL);
static void finalize_btConstraintSetting( _ref(btConstraintSetting)* _this ) { free_ref(_this); }
HL_PRIM void HL_NAME(btConstraintSetting_delete)( _ref(btConstraintSetting)* _this ) {
	free_ref(_this);
}
DEFINE_PRIM(_VOID, btConstraintSetting_delete, _IDL);
static void finalize_btTypedConstraint( _ref(btTypedConstraint)* _this ) { free_ref(_this); }
HL_PRIM void HL_NAME(btTypedConstraint_delete)( _ref(btTypedConstraint)* _this ) {
	free_ref(_this);
}
DEFINE_PRIM(_VOID, btTypedConstraint_delete, _IDL);
static btConstraintParams btConstraintParams__values[] = { BT_CONSTRAINT_ERP,BT_CONSTRAINT_STOP_ERP,BT_CONSTRAINT_CFM,BT_CONSTRAINT_STOP_CFM };
static void finalize_btPoint2PointConstraint( _ref(btPoint2PointConstraint)* _this ) { free_ref(_this); }
HL_PRIM void HL_NAME(btPoint2PointConstraint_delete)( _ref(btPoint2PointConstraint)* _this ) {
	free_ref(_this);
}
DEFINE_PRIM(_VOID, btPoint2PointConstraint_delete, _IDL);
static void finalize_btGeneric6DofConstraint( _ref(btGeneric6DofConstraint)* _this ) { free_ref(_this); }
HL_PRIM void HL_NAME(btGeneric6DofConstraint_delete)( _ref(btGeneric6DofConstraint)* _this ) {
	free_ref(_this);
}
DEFINE_PRIM(_VOID, btGeneric6DofConstraint_delete, _IDL);
static void finalize_btGeneric6DofSpringConstraint( _ref(btGeneric6DofSpringConstraint)* _this ) { free_ref(_this); }
HL_PRIM void HL_NAME(btGeneric6DofSpringConstraint_delete)( _ref(btGeneric6DofSpringConstraint)* _this ) {
	free_ref(_this);
}
DEFINE_PRIM(_VOID, btGeneric6DofSpringConstraint_delete, _IDL);
static void finalize_btSequentialImpulseConstraintSolver( _ref(btSequentialImpulseConstraintSolver)* _this ) { free_ref(_this); }
HL_PRIM void HL_NAME(btSequentialImpulseConstraintSolver_delete)( _ref(btSequentialImpulseConstraintSolver)* _this ) {
	free_ref(_this);
}
DEFINE_PRIM(_VOID, btSequentialImpulseConstraintSolver_delete, _IDL);
static void finalize_btConeTwistConstraint( _ref(btConeTwistConstraint)* _this ) { free_ref(_this); }
HL_PRIM void HL_NAME(btConeTwistConstraint_delete)( _ref(btConeTwistConstraint)* _this ) {
	free_ref(_this);
}
DEFINE_PRIM(_VOID, btConeTwistConstraint_delete, _IDL);
static void finalize_btHingeConstraint( _ref(btHingeConstraint)* _this ) { free_ref(_this); }
HL_PRIM void HL_NAME(btHingeConstraint_delete)( _ref(btHingeConstraint)* _this ) {
	free_ref(_this);
}
DEFINE_PRIM(_VOID, btHingeConstraint_delete, _IDL);
static void finalize_btSliderConstraint( _ref(btSliderConstraint)* _this ) { free_ref(_this); }
HL_PRIM void HL_NAME(btSliderConstraint_delete)( _ref(btSliderConstraint)* _this ) {
	free_ref(_this);
}
DEFINE_PRIM(_VOID, btSliderConstraint_delete, _IDL);
static void finalize_btFixedConstraint( _ref(btFixedConstraint)* _this ) { free_ref(_this); }
HL_PRIM void HL_NAME(btFixedConstraint_delete)( _ref(btFixedConstraint)* _this ) {
	free_ref(_this);
}
DEFINE_PRIM(_VOID, btFixedConstraint_delete, _IDL);
static void finalize_btConstraintSolver( _ref(btConstraintSolver)* _this ) { free_ref(_this); }
HL_PRIM void HL_NAME(btConstraintSolver_delete)( _ref(btConstraintSolver)* _this ) {
	free_ref(_this);
}
DEFINE_PRIM(_VOID, btConstraintSolver_delete, _IDL);
static void finalize_btDispatcherInfo( _ref(btDispatcherInfo)* _this ) { free_ref(_this); }
HL_PRIM void HL_NAME(btDispatcherInfo_delete)( _ref(btDispatcherInfo)* _this ) {
	free_ref(_this);
}
DEFINE_PRIM(_VOID, btDispatcherInfo_delete, _IDL);
static void finalize_btCollisionWorld( _ref(btCollisionWorld)* _this ) { free_ref(_this); }
HL_PRIM void HL_NAME(btCollisionWorld_delete)( _ref(btCollisionWorld)* _this ) {
	free_ref(_this);
}
DEFINE_PRIM(_VOID, btCollisionWorld_delete, _IDL);
static void finalize_btContactSolverInfo( _ref(btContactSolverInfo)* _this ) { free_ref(_this); }
HL_PRIM void HL_NAME(btContactSolverInfo_delete)( _ref(btContactSolverInfo)* _this ) {
	free_ref(_this);
}
DEFINE_PRIM(_VOID, btContactSolverInfo_delete, _IDL);
static void finalize_btDynamicsWorld( _ref(btDynamicsWorld)* _this ) { free_ref(_this); }
HL_PRIM void HL_NAME(btDynamicsWorld_delete)( _ref(btDynamicsWorld)* _this ) {
	free_ref(_this);
}
DEFINE_PRIM(_VOID, btDynamicsWorld_delete, _IDL);
static void finalize_btDiscreteDynamicsWorld( _ref(btDiscreteDynamicsWorld)* _this ) { free_ref(_this); }
HL_PRIM void HL_NAME(btDiscreteDynamicsWorld_delete)( _ref(btDiscreteDynamicsWorld)* _this ) {
	free_ref(_this);
}
DEFINE_PRIM(_VOID, btDiscreteDynamicsWorld_delete, _IDL);
static void finalize_btVehicleTuning( _ref(btRaycastVehicle::btVehicleTuning)* _this ) { free_ref(_this); }
HL_PRIM void HL_NAME(btVehicleTuning_delete)( _ref(btRaycastVehicle::btVehicleTuning)* _this ) {
	free_ref(_this);
}
DEFINE_PRIM(_VOID, btVehicleTuning_delete, _IDL);
static void finalize_btVehicleRaycasterResult( _ref(btDefaultVehicleRaycaster::btVehicleRaycasterResult)* _this ) { free_ref(_this); }
HL_PRIM void HL_NAME(btVehicleRaycasterResult_delete)( _ref(btDefaultVehicleRaycaster::btVehicleRaycasterResult)* _this ) {
	free_ref(_this);
}
DEFINE_PRIM(_VOID, btVehicleRaycasterResult_delete, _IDL);
static void finalize_btVehicleRaycaster( _ref(btVehicleRaycaster)* _this ) { free_ref(_this); }
HL_PRIM void HL_NAME(btVehicleRaycaster_delete)( _ref(btVehicleRaycaster)* _this ) {
	free_ref(_this);
}
DEFINE_PRIM(_VOID, btVehicleRaycaster_delete, _IDL);
static void finalize_btDefaultVehicleRaycaster( _ref(btDefaultVehicleRaycaster)* _this ) { free_ref(_this); }
HL_PRIM void HL_NAME(btDefaultVehicleRaycaster_delete)( _ref(btDefaultVehicleRaycaster)* _this ) {
	free_ref(_this);
}
DEFINE_PRIM(_VOID, btDefaultVehicleRaycaster_delete, _IDL);
static void finalize_RaycastInfo( _ref(btWheelInfo::RaycastInfo)* _this ) { free_ref(_this); }
HL_PRIM void HL_NAME(RaycastInfo_delete)( _ref(btWheelInfo::RaycastInfo)* _this ) {
	free_ref(_this);
}
DEFINE_PRIM(_VOID, RaycastInfo_delete, _IDL);
static void finalize_btWheelInfoConstructionInfo( _ref(btWheelInfoConstructionInfo)* _this ) { free_ref(_this); }
HL_PRIM void HL_NAME(btWheelInfoConstructionInfo_delete)( _ref(btWheelInfoConstructionInfo)* _this ) {
	free_ref(_this);
}
DEFINE_PRIM(_VOID, btWheelInfoConstructionInfo_delete, _IDL);
static void finalize_btWheelInfo( _ref(btWheelInfo)* _this ) { free_ref(_this); }
HL_PRIM void HL_NAME(btWheelInfo_delete)( _ref(btWheelInfo)* _this ) {
	free_ref(_this);
}
DEFINE_PRIM(_VOID, btWheelInfo_delete, _IDL);
static void finalize_btActionInterface( _ref(btActionInterface)* _this ) { free_ref(_this); }
HL_PRIM void HL_NAME(btActionInterface_delete)( _ref(btActionInterface)* _this ) {
	free_ref(_this);
}
DEFINE_PRIM(_VOID, btActionInterface_delete, _IDL);
static void finalize_btKinematicCharacterController( _ref(btKinematicCharacterController)* _this ) { free_ref(_this); }
HL_PRIM void HL_NAME(btKinematicCharacterController_delete)( _ref(btKinematicCharacterController)* _this ) {
	free_ref(_this);
}
DEFINE_PRIM(_VOID, btKinematicCharacterController_delete, _IDL);
static void finalize_btRaycastVehicle( _ref(btRaycastVehicle)* _this ) { free_ref(_this); }
HL_PRIM void HL_NAME(btRaycastVehicle_delete)( _ref(btRaycastVehicle)* _this ) {
	free_ref(_this);
}
DEFINE_PRIM(_VOID, btRaycastVehicle_delete, _IDL);
static void finalize_btGhostObject( _ref(btGhostObject)* _this ) { free_ref(_this); }
HL_PRIM void HL_NAME(btGhostObject_delete)( _ref(btGhostObject)* _this ) {
	free_ref(_this);
}
DEFINE_PRIM(_VOID, btGhostObject_delete, _IDL);
static void finalize_btPairCachingGhostObject( _ref(btPairCachingGhostObject)* _this ) { free_ref(_this); }
HL_PRIM void HL_NAME(btPairCachingGhostObject_delete)( _ref(btPairCachingGhostObject)* _this ) {
	free_ref(_this);
}
DEFINE_PRIM(_VOID, btPairCachingGhostObject_delete, _IDL);
static void finalize_btGhostPairCallback( _ref(btGhostPairCallback)* _this ) { free_ref(_this); }
HL_PRIM void HL_NAME(btGhostPairCallback_delete)( _ref(btGhostPairCallback)* _this ) {
	free_ref(_this);
}
DEFINE_PRIM(_VOID, btGhostPairCallback_delete, _IDL);
static void finalize_btSoftBodyWorldInfo( _ref(btSoftBodyWorldInfo)* _this ) { free_ref(_this); }
HL_PRIM void HL_NAME(btSoftBodyWorldInfo_delete)( _ref(btSoftBodyWorldInfo)* _this ) {
	free_ref(_this);
}
DEFINE_PRIM(_VOID, btSoftBodyWorldInfo_delete, _IDL);
static void finalize_Node( _ref(btSoftBody::Node)* _this ) { free_ref(_this); }
HL_PRIM void HL_NAME(Node_delete)( _ref(btSoftBody::Node)* _this ) {
	free_ref(_this);
}
DEFINE_PRIM(_VOID, Node_delete, _IDL);
static void finalize_tNodeArray( _ref(btSoftBody::tNodeArray)* _this ) { free_ref(_this); }
HL_PRIM void HL_NAME(tNodeArray_delete)( _ref(btSoftBody::tNodeArray)* _this ) {
	free_ref(_this);
}
DEFINE_PRIM(_VOID, tNodeArray_delete, _IDL);
static void finalize_Material( _ref(btSoftBody::Material)* _this ) { free_ref(_this); }
HL_PRIM void HL_NAME(Material_delete)( _ref(btSoftBody::Material)* _this ) {
	free_ref(_this);
}
DEFINE_PRIM(_VOID, Material_delete, _IDL);
static void finalize_tMaterialArray( _ref(btSoftBody::tMaterialArray)* _this ) { free_ref(_this); }
HL_PRIM void HL_NAME(tMaterialArray_delete)( _ref(btSoftBody::tMaterialArray)* _this ) {
	free_ref(_this);
}
DEFINE_PRIM(_VOID, tMaterialArray_delete, _IDL);
static void finalize_Config( _ref(btSoftBody::Config)* _this ) { free_ref(_this); }
HL_PRIM void HL_NAME(Config_delete)( _ref(btSoftBody::Config)* _this ) {
	free_ref(_this);
}
DEFINE_PRIM(_VOID, Config_delete, _IDL);
static void finalize_btSoftBody( _ref(btSoftBody)* _this ) { free_ref(_this); }
HL_PRIM void HL_NAME(btSoftBody_delete)( _ref(btSoftBody)* _this ) {
	free_ref(_this);
}
DEFINE_PRIM(_VOID, btSoftBody_delete, _IDL);
static void finalize_btSoftBodyRigidBodyCollisionConfiguration( _ref(btSoftBodyRigidBodyCollisionConfiguration)* _this ) { free_ref(_this); }
HL_PRIM void HL_NAME(btSoftBodyRigidBodyCollisionConfiguration_delete)( _ref(btSoftBodyRigidBodyCollisionConfiguration)* _this ) {
	free_ref(_this);
}
DEFINE_PRIM(_VOID, btSoftBodyRigidBodyCollisionConfiguration_delete, _IDL);
static void finalize_btSoftBodySolver( _ref(btSoftBodySolver)* _this ) { free_ref(_this); }
HL_PRIM void HL_NAME(btSoftBodySolver_delete)( _ref(btSoftBodySolver)* _this ) {
	free_ref(_this);
}
DEFINE_PRIM(_VOID, btSoftBodySolver_delete, _IDL);
static void finalize_btDefaultSoftBodySolver( _ref(btDefaultSoftBodySolver)* _this ) { free_ref(_this); }
HL_PRIM void HL_NAME(btDefaultSoftBodySolver_delete)( _ref(btDefaultSoftBodySolver)* _this ) {
	free_ref(_this);
}
DEFINE_PRIM(_VOID, btDefaultSoftBodySolver_delete, _IDL);
static void finalize_btSoftBodyArray( _ref(btSoftBodyArray)* _this ) { free_ref(_this); }
HL_PRIM void HL_NAME(btSoftBodyArray_delete)( _ref(btSoftBodyArray)* _this ) {
	free_ref(_this);
}
DEFINE_PRIM(_VOID, btSoftBodyArray_delete, _IDL);
static void finalize_btSoftRigidDynamicsWorld( _ref(btSoftRigidDynamicsWorld)* _this ) { free_ref(_this); }
HL_PRIM void HL_NAME(btSoftRigidDynamicsWorld_delete)( _ref(btSoftRigidDynamicsWorld)* _this ) {
	free_ref(_this);
}
DEFINE_PRIM(_VOID, btSoftRigidDynamicsWorld_delete, _IDL);
static void finalize_btSoftBodyHelpers( _ref(btSoftBodyHelpers)* _this ) { free_ref(_this); }
HL_PRIM void HL_NAME(btSoftBodyHelpers_delete)( _ref(btSoftBodyHelpers)* _this ) {
	free_ref(_this);
}
DEFINE_PRIM(_VOID, btSoftBodyHelpers_delete, _IDL);
HL_PRIM _ref(btVector3)* HL_NAME(btVector3_new0)() {
	return alloc_ref((new btVector3()),btVector3);
}
DEFINE_PRIM(_IDL, btVector3_new0,);

HL_PRIM _ref(btVector3)* HL_NAME(btVector3_new3)(float x, float y, float z) {
	return alloc_ref((new btVector3(x, y, z)),btVector3);
}
DEFINE_PRIM(_IDL, btVector3_new3, _F32 _F32 _F32);

HL_PRIM float HL_NAME(btVector3_length0)(_ref(btVector3)* _this) {
	return _unref(_this)->length();
}
DEFINE_PRIM(_F32, btVector3_length0, _IDL);

HL_PRIM float HL_NAME(btVector3_x0)(_ref(btVector3)* _this) {
	return _unref(_this)->x();
}
DEFINE_PRIM(_F32, btVector3_x0, _IDL);

HL_PRIM float HL_NAME(btVector3_y0)(_ref(btVector3)* _this) {
	return _unref(_this)->y();
}
DEFINE_PRIM(_F32, btVector3_y0, _IDL);

HL_PRIM float HL_NAME(btVector3_z0)(_ref(btVector3)* _this) {
	return _unref(_this)->z();
}
DEFINE_PRIM(_F32, btVector3_z0, _IDL);

HL_PRIM void HL_NAME(btVector3_setX1)(_ref(btVector3)* _this, float x) {
	_unref(_this)->setX(x);
}
DEFINE_PRIM(_VOID, btVector3_setX1, _IDL _F32);

HL_PRIM void HL_NAME(btVector3_setY1)(_ref(btVector3)* _this, float y) {
	_unref(_this)->setY(y);
}
DEFINE_PRIM(_VOID, btVector3_setY1, _IDL _F32);

HL_PRIM void HL_NAME(btVector3_setZ1)(_ref(btVector3)* _this, float z) {
	_unref(_this)->setZ(z);
}
DEFINE_PRIM(_VOID, btVector3_setZ1, _IDL _F32);

HL_PRIM void HL_NAME(btVector3_setValue3)(_ref(btVector3)* _this, float x, float y, float z) {
	_unref(_this)->setValue(x, y, z);
}
DEFINE_PRIM(_VOID, btVector3_setValue3, _IDL _F32 _F32 _F32);

HL_PRIM void HL_NAME(btVector3_normalize0)(_ref(btVector3)* _this) {
	_unref(_this)->normalize();
}
DEFINE_PRIM(_VOID, btVector3_normalize0, _IDL);

HL_PRIM _ref(btVector3)* HL_NAME(btVector3_rotate2)(_ref(btVector3)* _this, _ref(btVector3)* wAxis, float angle) {
	return alloc_ref(new btVector3(_unref(_this)->rotate(*_unref(wAxis), angle)),btVector3);
}
DEFINE_PRIM(_IDL, btVector3_rotate2, _IDL _IDL _F32);

HL_PRIM float HL_NAME(btVector3_dot1)(_ref(btVector3)* _this, _ref(btVector3)* v) {
	return _unref(_this)->dot(*_unref(v));
}
DEFINE_PRIM(_F32, btVector3_dot1, _IDL _IDL);

HL_PRIM _ref(btVector3)* HL_NAME(btVector3_op_mul1)(_ref(btVector3)* _this, float x) {
	return alloc_ref(new btVector3(*_unref(_this) * (x)),btVector3);
}
DEFINE_PRIM(_IDL, btVector3_op_mul1, _IDL _F32);

HL_PRIM _ref(btVector3)* HL_NAME(btVector3_op_add1)(_ref(btVector3)* _this, _ref(btVector3)* v) {
	return alloc_ref(new btVector3(*_unref(_this) + (*_unref(v))),btVector3);
}
DEFINE_PRIM(_IDL, btVector3_op_add1, _IDL _IDL);

HL_PRIM _ref(btVector3)* HL_NAME(btVector3_op_sub1)(_ref(btVector3)* _this, _ref(btVector3)* v) {
	return alloc_ref(new btVector3(*_unref(_this) - (*_unref(v))),btVector3);
}
DEFINE_PRIM(_IDL, btVector3_op_sub1, _IDL _IDL);

HL_PRIM _ref(btVector4)* HL_NAME(btVector4_new0)() {
	return alloc_ref((new btVector4()),btVector4);
}
DEFINE_PRIM(_IDL, btVector4_new0,);

HL_PRIM _ref(btVector4)* HL_NAME(btVector4_new4)(float x, float y, float z, float w) {
	return alloc_ref((new btVector4(x, y, z, w)),btVector4);
}
DEFINE_PRIM(_IDL, btVector4_new4, _F32 _F32 _F32 _F32);

HL_PRIM float HL_NAME(btVector4_w0)(_ref(btVector4)* _this) {
	return _unref(_this)->w();
}
DEFINE_PRIM(_F32, btVector4_w0, _IDL);

HL_PRIM void HL_NAME(btVector4_setValue4)(_ref(btVector4)* _this, float x, float y, float z, float w) {
	_unref(_this)->setValue(x, y, z, w);
}
DEFINE_PRIM(_VOID, btVector4_setValue4, _IDL _F32 _F32 _F32 _F32);

HL_PRIM float HL_NAME(btQuadWord_x0)(_ref(btQuadWord)* _this) {
	return _unref(_this)->x();
}
DEFINE_PRIM(_F32, btQuadWord_x0, _IDL);

HL_PRIM float HL_NAME(btQuadWord_y0)(_ref(btQuadWord)* _this) {
	return _unref(_this)->y();
}
DEFINE_PRIM(_F32, btQuadWord_y0, _IDL);

HL_PRIM float HL_NAME(btQuadWord_z0)(_ref(btQuadWord)* _this) {
	return _unref(_this)->z();
}
DEFINE_PRIM(_F32, btQuadWord_z0, _IDL);

HL_PRIM float HL_NAME(btQuadWord_w0)(_ref(btQuadWord)* _this) {
	return _unref(_this)->w();
}
DEFINE_PRIM(_F32, btQuadWord_w0, _IDL);

HL_PRIM void HL_NAME(btQuadWord_setX1)(_ref(btQuadWord)* _this, float x) {
	_unref(_this)->setX(x);
}
DEFINE_PRIM(_VOID, btQuadWord_setX1, _IDL _F32);

HL_PRIM void HL_NAME(btQuadWord_setY1)(_ref(btQuadWord)* _this, float y) {
	_unref(_this)->setY(y);
}
DEFINE_PRIM(_VOID, btQuadWord_setY1, _IDL _F32);

HL_PRIM void HL_NAME(btQuadWord_setZ1)(_ref(btQuadWord)* _this, float z) {
	_unref(_this)->setZ(z);
}
DEFINE_PRIM(_VOID, btQuadWord_setZ1, _IDL _F32);

HL_PRIM void HL_NAME(btQuadWord_setW1)(_ref(btQuadWord)* _this, float w) {
	_unref(_this)->setW(w);
}
DEFINE_PRIM(_VOID, btQuadWord_setW1, _IDL _F32);

HL_PRIM _ref(btQuaternion)* HL_NAME(btQuaternion_new4)(float x, float y, float z, float w) {
	return alloc_ref((new btQuaternion(x, y, z, w)),btQuaternion);
}
DEFINE_PRIM(_IDL, btQuaternion_new4, _F32 _F32 _F32 _F32);

HL_PRIM void HL_NAME(btQuaternion_setValue4)(_ref(btQuaternion)* _this, float x, float y, float z, float w) {
	_unref(_this)->setValue(x, y, z, w);
}
DEFINE_PRIM(_VOID, btQuaternion_setValue4, _IDL _F32 _F32 _F32 _F32);

HL_PRIM void HL_NAME(btQuaternion_setEulerZYX3)(_ref(btQuaternion)* _this, float z, float y, float x) {
	_unref(_this)->setEulerZYX(z, y, x);
}
DEFINE_PRIM(_VOID, btQuaternion_setEulerZYX3, _IDL _F32 _F32 _F32);

HL_PRIM void HL_NAME(btQuaternion_setRotation2)(_ref(btQuaternion)* _this, _ref(btVector3)* axis, float angle) {
	_unref(_this)->setRotation(*_unref(axis), angle);
}
DEFINE_PRIM(_VOID, btQuaternion_setRotation2, _IDL _IDL _F32);

HL_PRIM void HL_NAME(btQuaternion_normalize0)(_ref(btQuaternion)* _this) {
	_unref(_this)->normalize();
}
DEFINE_PRIM(_VOID, btQuaternion_normalize0, _IDL);

HL_PRIM float HL_NAME(btQuaternion_length20)(_ref(btQuaternion)* _this) {
	return _unref(_this)->length2();
}
DEFINE_PRIM(_F32, btQuaternion_length20, _IDL);

HL_PRIM float HL_NAME(btQuaternion_length0)(_ref(btQuaternion)* _this) {
	return _unref(_this)->length();
}
DEFINE_PRIM(_F32, btQuaternion_length0, _IDL);

HL_PRIM float HL_NAME(btQuaternion_dot1)(_ref(btQuaternion)* _this, _ref(btQuaternion)* q) {
	return _unref(_this)->dot(*_unref(q));
}
DEFINE_PRIM(_F32, btQuaternion_dot1, _IDL _IDL);

HL_PRIM _ref(btQuaternion)* HL_NAME(btQuaternion_normalized0)(_ref(btQuaternion)* _this) {
	return alloc_ref(new btQuaternion(_unref(_this)->normalized()),btQuaternion);
}
DEFINE_PRIM(_IDL, btQuaternion_normalized0, _IDL);

HL_PRIM _ref(btVector3)* HL_NAME(btQuaternion_getAxis0)(_ref(btQuaternion)* _this) {
	return alloc_ref(new btVector3(_unref(_this)->getAxis()),btVector3);
}
DEFINE_PRIM(_IDL, btQuaternion_getAxis0, _IDL);

HL_PRIM _ref(btQuaternion)* HL_NAME(btQuaternion_inverse0)(_ref(btQuaternion)* _this) {
	return alloc_ref(new btQuaternion(_unref(_this)->inverse()),btQuaternion);
}
DEFINE_PRIM(_IDL, btQuaternion_inverse0, _IDL);

HL_PRIM float HL_NAME(btQuaternion_getAngle0)(_ref(btQuaternion)* _this) {
	return _unref(_this)->getAngle();
}
DEFINE_PRIM(_F32, btQuaternion_getAngle0, _IDL);

HL_PRIM float HL_NAME(btQuaternion_getAngleShortestPath0)(_ref(btQuaternion)* _this) {
	return _unref(_this)->getAngleShortestPath();
}
DEFINE_PRIM(_F32, btQuaternion_getAngleShortestPath0, _IDL);

HL_PRIM float HL_NAME(btQuaternion_angle1)(_ref(btQuaternion)* _this, _ref(btQuaternion)* q) {
	return _unref(_this)->angle(*_unref(q));
}
DEFINE_PRIM(_F32, btQuaternion_angle1, _IDL _IDL);

HL_PRIM float HL_NAME(btQuaternion_angleShortestPath1)(_ref(btQuaternion)* _this, _ref(btQuaternion)* q) {
	return _unref(_this)->angleShortestPath(*_unref(q));
}
DEFINE_PRIM(_F32, btQuaternion_angleShortestPath1, _IDL _IDL);

HL_PRIM _ref(btQuaternion)* HL_NAME(btQuaternion_op_add1)(_ref(btQuaternion)* _this, _ref(btQuaternion)* q) {
	return alloc_ref(new btQuaternion(*_unref(_this) + (*_unref(q))),btQuaternion);
}
DEFINE_PRIM(_IDL, btQuaternion_op_add1, _IDL _IDL);

HL_PRIM _ref(btQuaternion)* HL_NAME(btQuaternion_op_sub1)(_ref(btQuaternion)* _this, _ref(btQuaternion)* q) {
	return alloc_ref(new btQuaternion(*_unref(_this) - (*_unref(q))),btQuaternion);
}
DEFINE_PRIM(_IDL, btQuaternion_op_sub1, _IDL _IDL);

HL_PRIM _ref(btQuaternion)* HL_NAME(btQuaternion_op_mul1)(_ref(btQuaternion)* _this, float s) {
	return alloc_ref(new btQuaternion(*_unref(_this) * (s)),btQuaternion);
}
DEFINE_PRIM(_IDL, btQuaternion_op_mul1, _IDL _F32);

HL_PRIM _ref(btQuaternion)* HL_NAME(btQuaternion_op_mulq1)(_ref(btQuaternion)* _this, _ref(btQuaternion)* q) {
	return alloc_ref(new btQuaternion(*_unref(_this) *= (*_unref(q))),btQuaternion);
}
DEFINE_PRIM(_IDL, btQuaternion_op_mulq1, _IDL _IDL);

HL_PRIM _ref(btQuaternion)* HL_NAME(btQuaternion_op_div1)(_ref(btQuaternion)* _this, float s) {
	return alloc_ref(new btQuaternion(*_unref(_this) / (s)),btQuaternion);
}
DEFINE_PRIM(_IDL, btQuaternion_op_div1, _IDL _F32);

HL_PRIM void HL_NAME(btMatrix3x3_setEulerZYX3)(_ref(btMatrix3x3)* _this, float ex, float ey, float ez) {
	_unref(_this)->setEulerZYX(ex, ey, ez);
}
DEFINE_PRIM(_VOID, btMatrix3x3_setEulerZYX3, _IDL _F32 _F32 _F32);

HL_PRIM void HL_NAME(btMatrix3x3_getRotation1)(_ref(btMatrix3x3)* _this, _ref(btQuaternion)* q) {
	_unref(_this)->getRotation(*_unref(q));
}
DEFINE_PRIM(_VOID, btMatrix3x3_getRotation1, _IDL _IDL);

HL_PRIM _ref(btVector3)* HL_NAME(btMatrix3x3_getRow1)(_ref(btMatrix3x3)* _this, int y) {
	return alloc_ref(new btVector3(_unref(_this)->getRow(y)),btVector3);
}
DEFINE_PRIM(_IDL, btMatrix3x3_getRow1, _IDL _I32);

HL_PRIM _ref(btTransform)* HL_NAME(btTransform_new0)() {
	return alloc_ref((new btTransform()),btTransform);
}
DEFINE_PRIM(_IDL, btTransform_new0,);

HL_PRIM _ref(btTransform)* HL_NAME(btTransform_new2)(_ref(btQuaternion)* q, _ref(btVector3)* v) {
	return alloc_ref((new btTransform(*_unref(q), *_unref(v))),btTransform);
}
DEFINE_PRIM(_IDL, btTransform_new2, _IDL _IDL);

HL_PRIM void HL_NAME(btTransform_setIdentity0)(_ref(btTransform)* _this) {
	_unref(_this)->setIdentity();
}
DEFINE_PRIM(_VOID, btTransform_setIdentity0, _IDL);

HL_PRIM void HL_NAME(btTransform_setOrigin1)(_ref(btTransform)* _this, _ref(btVector3)* origin) {
	_unref(_this)->setOrigin(*_unref(origin));
}
DEFINE_PRIM(_VOID, btTransform_setOrigin1, _IDL _IDL);

HL_PRIM void HL_NAME(btTransform_setRotation1)(_ref(btTransform)* _this, _ref(btQuaternion)* rotation) {
	_unref(_this)->setRotation(*_unref(rotation));
}
DEFINE_PRIM(_VOID, btTransform_setRotation1, _IDL _IDL);

HL_PRIM _ref(btVector3)* HL_NAME(btTransform_getOrigin0)(_ref(btTransform)* _this) {
	return alloc_ref(new btVector3(_unref(_this)->getOrigin()),btVector3);
}
DEFINE_PRIM(_IDL, btTransform_getOrigin0, _IDL);

HL_PRIM _ref(btQuaternion)* HL_NAME(btTransform_getRotation0)(_ref(btTransform)* _this) {
	return alloc_ref(new btQuaternion(_unref(_this)->getRotation()),btQuaternion);
}
DEFINE_PRIM(_IDL, btTransform_getRotation0, _IDL);

HL_PRIM _ref(btMatrix3x3)* HL_NAME(btTransform_getBasis0)(_ref(btTransform)* _this) {
	return alloc_ref(new btMatrix3x3(_unref(_this)->getBasis()),btMatrix3x3);
}
DEFINE_PRIM(_IDL, btTransform_getBasis0, _IDL);

HL_PRIM void HL_NAME(btTransform_setFromOpenGLMatrix1)(_ref(btTransform)* _this, float* m) {
	_unref(_this)->setFromOpenGLMatrix(m);
}
DEFINE_PRIM(_VOID, btTransform_setFromOpenGLMatrix1, _IDL _BYTES);

HL_PRIM void HL_NAME(btMotionState_getWorldTransform1)(_ref(btMotionState)* _this, _ref(btTransform)* worldTrans) {
	_unref(_this)->getWorldTransform(*_unref(worldTrans));
}
DEFINE_PRIM(_VOID, btMotionState_getWorldTransform1, _IDL _IDL);

HL_PRIM void HL_NAME(btMotionState_setWorldTransform1)(_ref(btMotionState)* _this, _ref(btTransform)* worldTrans) {
	_unref(_this)->setWorldTransform(*_unref(worldTrans));
}
DEFINE_PRIM(_VOID, btMotionState_setWorldTransform1, _IDL _IDL);

HL_PRIM _ref(btDefaultMotionState)* HL_NAME(btDefaultMotionState_new2)(_ref(btTransform)* startTrans, _ref(btTransform)* centerOfMassOffset) {
	if( !startTrans )
		return alloc_ref((new btDefaultMotionState()),btDefaultMotionState);
	else
	if( !centerOfMassOffset )
		return alloc_ref((new btDefaultMotionState(*_unref(startTrans))),btDefaultMotionState);
	else
		return alloc_ref((new btDefaultMotionState(*_unref(startTrans), *_unref(centerOfMassOffset))),btDefaultMotionState);
}
DEFINE_PRIM(_IDL, btDefaultMotionState_new2, _IDL _IDL);

HL_PRIM _ref(btTransform)* HL_NAME(btDefaultMotionState_get_m_graphicsWorldTrans)( _ref(btDefaultMotionState)* _this ) {
	return alloc_ref(new btTransform(_unref(_this)->m_graphicsWorldTrans),btTransform);
}
HL_PRIM _ref(btTransform)* HL_NAME(btDefaultMotionState_set_m_graphicsWorldTrans)( _ref(btDefaultMotionState)* _this, _ref(btTransform)* value ) {
	_unref(_this)->m_graphicsWorldTrans = *_unref(value);
	return value;
}
DEFINE_PRIM(_IDL,btDefaultMotionState_get_m_graphicsWorldTrans,_IDL);
DEFINE_PRIM(_IDL,btDefaultMotionState_set_m_graphicsWorldTrans,_IDL _IDL);

HL_PRIM void HL_NAME(btCollisionObject_setAnisotropicFriction2)(_ref(btCollisionObject)* _this, _ref(btVector3)* anisotropicFriction, int frictionMode) {
	_unref(_this)->setAnisotropicFriction(*_unref(anisotropicFriction), frictionMode);
}
DEFINE_PRIM(_VOID, btCollisionObject_setAnisotropicFriction2, _IDL _IDL _I32);

HL_PRIM _ref(btCollisionShape)* HL_NAME(btCollisionObject_getCollisionShape0)(_ref(btCollisionObject)* _this) {
	return alloc_ref((_unref(_this)->getCollisionShape()),btCollisionShape);
}
DEFINE_PRIM(_IDL, btCollisionObject_getCollisionShape0, _IDL);

HL_PRIM void HL_NAME(btCollisionObject_setContactProcessingThreshold1)(_ref(btCollisionObject)* _this, float contactProcessingThreshold) {
	_unref(_this)->setContactProcessingThreshold(contactProcessingThreshold);
}
DEFINE_PRIM(_VOID, btCollisionObject_setContactProcessingThreshold1, _IDL _F32);

HL_PRIM void HL_NAME(btCollisionObject_setActivationState1)(_ref(btCollisionObject)* _this, int newState) {
	_unref(_this)->setActivationState(newState);
}
DEFINE_PRIM(_VOID, btCollisionObject_setActivationState1, _IDL _I32);

HL_PRIM void HL_NAME(btCollisionObject_forceActivationState1)(_ref(btCollisionObject)* _this, int newState) {
	_unref(_this)->forceActivationState(newState);
}
DEFINE_PRIM(_VOID, btCollisionObject_forceActivationState1, _IDL _I32);

HL_PRIM void HL_NAME(btCollisionObject_activate1)(_ref(btCollisionObject)* _this, _OPT(bool) forceActivation) {
	if( !forceActivation )
		_unref(_this)->activate();
	else
		_unref(_this)->activate(_GET_OPT(forceActivation,b));
}
DEFINE_PRIM(_VOID, btCollisionObject_activate1, _IDL _NULL(_BOOL));

HL_PRIM bool HL_NAME(btCollisionObject_isActive0)(_ref(btCollisionObject)* _this) {
	return _unref(_this)->isActive();
}
DEFINE_PRIM(_BOOL, btCollisionObject_isActive0, _IDL);

HL_PRIM bool HL_NAME(btCollisionObject_isKinematicObject0)(_ref(btCollisionObject)* _this) {
	return _unref(_this)->isKinematicObject();
}
DEFINE_PRIM(_BOOL, btCollisionObject_isKinematicObject0, _IDL);

HL_PRIM bool HL_NAME(btCollisionObject_isStaticObject0)(_ref(btCollisionObject)* _this) {
	return _unref(_this)->isStaticObject();
}
DEFINE_PRIM(_BOOL, btCollisionObject_isStaticObject0, _IDL);

HL_PRIM bool HL_NAME(btCollisionObject_isStaticOrKinematicObject0)(_ref(btCollisionObject)* _this) {
	return _unref(_this)->isStaticOrKinematicObject();
}
DEFINE_PRIM(_BOOL, btCollisionObject_isStaticOrKinematicObject0, _IDL);

HL_PRIM void HL_NAME(btCollisionObject_setRestitution1)(_ref(btCollisionObject)* _this, float rest) {
	_unref(_this)->setRestitution(rest);
}
DEFINE_PRIM(_VOID, btCollisionObject_setRestitution1, _IDL _F32);

HL_PRIM void HL_NAME(btCollisionObject_setFriction1)(_ref(btCollisionObject)* _this, float frict) {
	_unref(_this)->setFriction(frict);
}
DEFINE_PRIM(_VOID, btCollisionObject_setFriction1, _IDL _F32);

HL_PRIM void HL_NAME(btCollisionObject_setRollingFriction1)(_ref(btCollisionObject)* _this, float frict) {
	_unref(_this)->setRollingFriction(frict);
}
DEFINE_PRIM(_VOID, btCollisionObject_setRollingFriction1, _IDL _F32);

HL_PRIM _ref(btTransform)* HL_NAME(btCollisionObject_getWorldTransform0)(_ref(btCollisionObject)* _this) {
	return alloc_ref(new btTransform(_unref(_this)->getWorldTransform()),btTransform);
}
DEFINE_PRIM(_IDL, btCollisionObject_getWorldTransform0, _IDL);

HL_PRIM int HL_NAME(btCollisionObject_getCollisionFlags0)(_ref(btCollisionObject)* _this) {
	return _unref(_this)->getCollisionFlags();
}
DEFINE_PRIM(_I32, btCollisionObject_getCollisionFlags0, _IDL);

HL_PRIM void HL_NAME(btCollisionObject_setCollisionFlags1)(_ref(btCollisionObject)* _this, int flags) {
	_unref(_this)->setCollisionFlags(flags);
}
DEFINE_PRIM(_VOID, btCollisionObject_setCollisionFlags1, _IDL _I32);

HL_PRIM void HL_NAME(btCollisionObject_setWorldTransform1)(_ref(btCollisionObject)* _this, _ref(btTransform)* worldTrans) {
	_unref(_this)->setWorldTransform(*_unref(worldTrans));
}
DEFINE_PRIM(_VOID, btCollisionObject_setWorldTransform1, _IDL _IDL);

HL_PRIM void HL_NAME(btCollisionObject_setCollisionShape1)(_ref(btCollisionObject)* _this, _ref(btCollisionShape)* collisionShape) {
	_unref(_this)->setCollisionShape(_unref(collisionShape));
}
DEFINE_PRIM(_VOID, btCollisionObject_setCollisionShape1, _IDL _IDL);

HL_PRIM void HL_NAME(btCollisionObject_setCcdMotionThreshold1)(_ref(btCollisionObject)* _this, float ccdMotionThreshold) {
	_unref(_this)->setCcdMotionThreshold(ccdMotionThreshold);
}
DEFINE_PRIM(_VOID, btCollisionObject_setCcdMotionThreshold1, _IDL _F32);

HL_PRIM void HL_NAME(btCollisionObject_setCcdSweptSphereRadius1)(_ref(btCollisionObject)* _this, float radius) {
	_unref(_this)->setCcdSweptSphereRadius(radius);
}
DEFINE_PRIM(_VOID, btCollisionObject_setCcdSweptSphereRadius1, _IDL _F32);

HL_PRIM int HL_NAME(btCollisionObject_getUserIndex0)(_ref(btCollisionObject)* _this) {
	return _unref(_this)->getUserIndex();
}
DEFINE_PRIM(_I32, btCollisionObject_getUserIndex0, _IDL);

HL_PRIM void HL_NAME(btCollisionObject_setUserIndex1)(_ref(btCollisionObject)* _this, int index) {
	_unref(_this)->setUserIndex(index);
}
DEFINE_PRIM(_VOID, btCollisionObject_setUserIndex1, _IDL _I32);

HL_PRIM void* HL_NAME(btCollisionObject_getUserPointer0)(_ref(btCollisionObject)* _this) {
	return _unref(_this)->getUserPointer();
}
DEFINE_PRIM(_BYTES, btCollisionObject_getUserPointer0, _IDL);

HL_PRIM void HL_NAME(btCollisionObject_setUserPointer1)(_ref(btCollisionObject)* _this, void* userPointer) {
	_unref(_this)->setUserPointer(userPointer);
}
DEFINE_PRIM(_VOID, btCollisionObject_setUserPointer1, _IDL _BYTES);

HL_PRIM bool HL_NAME(RayResultCallback_hasHit0)(_ref(btCollisionWorld::RayResultCallback)* _this) {
	return _unref(_this)->hasHit();
}
DEFINE_PRIM(_BOOL, RayResultCallback_hasHit0, _IDL);

HL_PRIM short HL_NAME(RayResultCallback_get_m_collisionFilterGroup)( _ref(btCollisionWorld::RayResultCallback)* _this ) {
	return _unref(_this)->m_collisionFilterGroup;
}
HL_PRIM short HL_NAME(RayResultCallback_set_m_collisionFilterGroup)( _ref(btCollisionWorld::RayResultCallback)* _this, short value ) {
	_unref(_this)->m_collisionFilterGroup = (value);
	return value;
}
DEFINE_PRIM(_I16,RayResultCallback_get_m_collisionFilterGroup,_IDL);
DEFINE_PRIM(_I16,RayResultCallback_set_m_collisionFilterGroup,_IDL _I16);

HL_PRIM short HL_NAME(RayResultCallback_get_m_collisionFilterMask)( _ref(btCollisionWorld::RayResultCallback)* _this ) {
	return _unref(_this)->m_collisionFilterMask;
}
HL_PRIM short HL_NAME(RayResultCallback_set_m_collisionFilterMask)( _ref(btCollisionWorld::RayResultCallback)* _this, short value ) {
	_unref(_this)->m_collisionFilterMask = (value);
	return value;
}
DEFINE_PRIM(_I16,RayResultCallback_get_m_collisionFilterMask,_IDL);
DEFINE_PRIM(_I16,RayResultCallback_set_m_collisionFilterMask,_IDL _I16);

HL_PRIM HL_CONST _ref(btCollisionObject)* HL_NAME(RayResultCallback_get_m_collisionObject)( _ref(btCollisionWorld::RayResultCallback)* _this ) {
	return alloc_ref_const(_unref(_this)->m_collisionObject,btCollisionObject);
}
HL_PRIM HL_CONST _ref(btCollisionObject)* HL_NAME(RayResultCallback_set_m_collisionObject)( _ref(btCollisionWorld::RayResultCallback)* _this, HL_CONST _ref(btCollisionObject)* value ) {
	_unref(_this)->m_collisionObject = _unref(value);
	return value;
}
DEFINE_PRIM(_IDL,RayResultCallback_get_m_collisionObject,_IDL);
DEFINE_PRIM(_IDL,RayResultCallback_set_m_collisionObject,_IDL _IDL);

HL_PRIM _ref(btCollisionWorld::ClosestRayResultCallback)* HL_NAME(ClosestRayResultCallback_new2)(_ref(btVector3)* from, _ref(btVector3)* to) {
	return alloc_ref((new btCollisionWorld::ClosestRayResultCallback(*_unref(from), *_unref(to))),ClosestRayResultCallback);
}
DEFINE_PRIM(_IDL, ClosestRayResultCallback_new2, _IDL _IDL);

HL_PRIM _ref(btVector3)* HL_NAME(ClosestRayResultCallback_get_m_rayFromWorld)( _ref(btCollisionWorld::ClosestRayResultCallback)* _this ) {
	return alloc_ref(new btVector3(_unref(_this)->m_rayFromWorld),btVector3);
}
HL_PRIM _ref(btVector3)* HL_NAME(ClosestRayResultCallback_set_m_rayFromWorld)( _ref(btCollisionWorld::ClosestRayResultCallback)* _this, _ref(btVector3)* value ) {
	_unref(_this)->m_rayFromWorld = *_unref(value);
	return value;
}
DEFINE_PRIM(_IDL,ClosestRayResultCallback_get_m_rayFromWorld,_IDL);
DEFINE_PRIM(_IDL,ClosestRayResultCallback_set_m_rayFromWorld,_IDL _IDL);

HL_PRIM _ref(btVector3)* HL_NAME(ClosestRayResultCallback_get_m_rayToWorld)( _ref(btCollisionWorld::ClosestRayResultCallback)* _this ) {
	return alloc_ref(new btVector3(_unref(_this)->m_rayToWorld),btVector3);
}
HL_PRIM _ref(btVector3)* HL_NAME(ClosestRayResultCallback_set_m_rayToWorld)( _ref(btCollisionWorld::ClosestRayResultCallback)* _this, _ref(btVector3)* value ) {
	_unref(_this)->m_rayToWorld = *_unref(value);
	return value;
}
DEFINE_PRIM(_IDL,ClosestRayResultCallback_get_m_rayToWorld,_IDL);
DEFINE_PRIM(_IDL,ClosestRayResultCallback_set_m_rayToWorld,_IDL _IDL);

HL_PRIM _ref(btVector3)* HL_NAME(ClosestRayResultCallback_get_m_hitNormalWorld)( _ref(btCollisionWorld::ClosestRayResultCallback)* _this ) {
	return alloc_ref(new btVector3(_unref(_this)->m_hitNormalWorld),btVector3);
}
HL_PRIM _ref(btVector3)* HL_NAME(ClosestRayResultCallback_set_m_hitNormalWorld)( _ref(btCollisionWorld::ClosestRayResultCallback)* _this, _ref(btVector3)* value ) {
	_unref(_this)->m_hitNormalWorld = *_unref(value);
	return value;
}
DEFINE_PRIM(_IDL,ClosestRayResultCallback_get_m_hitNormalWorld,_IDL);
DEFINE_PRIM(_IDL,ClosestRayResultCallback_set_m_hitNormalWorld,_IDL _IDL);

HL_PRIM _ref(btVector3)* HL_NAME(ClosestRayResultCallback_get_m_hitPointWorld)( _ref(btCollisionWorld::ClosestRayResultCallback)* _this ) {
	return alloc_ref(new btVector3(_unref(_this)->m_hitPointWorld),btVector3);
}
HL_PRIM _ref(btVector3)* HL_NAME(ClosestRayResultCallback_set_m_hitPointWorld)( _ref(btCollisionWorld::ClosestRayResultCallback)* _this, _ref(btVector3)* value ) {
	_unref(_this)->m_hitPointWorld = *_unref(value);
	return value;
}
DEFINE_PRIM(_IDL,ClosestRayResultCallback_get_m_hitPointWorld,_IDL);
DEFINE_PRIM(_IDL,ClosestRayResultCallback_set_m_hitPointWorld,_IDL _IDL);

HL_PRIM HL_CONST _ref(btVector3)* HL_NAME(btManifoldPoint_getPositionWorldOnA0)(_ref(btManifoldPoint)* _this) {
	return alloc_ref(new btVector3(_unref(_this)->getPositionWorldOnA()),btVector3);
}
DEFINE_PRIM(_IDL, btManifoldPoint_getPositionWorldOnA0, _IDL);

HL_PRIM HL_CONST _ref(btVector3)* HL_NAME(btManifoldPoint_getPositionWorldOnB0)(_ref(btManifoldPoint)* _this) {
	return alloc_ref(new btVector3(_unref(_this)->getPositionWorldOnB()),btVector3);
}
DEFINE_PRIM(_IDL, btManifoldPoint_getPositionWorldOnB0, _IDL);

HL_PRIM HL_CONST double HL_NAME(btManifoldPoint_getAppliedImpulse0)(_ref(btManifoldPoint)* _this) {
	return _unref(_this)->getAppliedImpulse();
}
DEFINE_PRIM(_F64, btManifoldPoint_getAppliedImpulse0, _IDL);

HL_PRIM HL_CONST double HL_NAME(btManifoldPoint_getDistance0)(_ref(btManifoldPoint)* _this) {
	return _unref(_this)->getDistance();
}
DEFINE_PRIM(_F64, btManifoldPoint_getDistance0, _IDL);

HL_PRIM _ref(btVector3)* HL_NAME(btManifoldPoint_get_m_localPointA)( _ref(btManifoldPoint)* _this ) {
	return alloc_ref(new btVector3(_unref(_this)->m_localPointA),btVector3);
}
HL_PRIM _ref(btVector3)* HL_NAME(btManifoldPoint_set_m_localPointA)( _ref(btManifoldPoint)* _this, _ref(btVector3)* value ) {
	_unref(_this)->m_localPointA = *_unref(value);
	return value;
}
DEFINE_PRIM(_IDL,btManifoldPoint_get_m_localPointA,_IDL);
DEFINE_PRIM(_IDL,btManifoldPoint_set_m_localPointA,_IDL _IDL);

HL_PRIM _ref(btVector3)* HL_NAME(btManifoldPoint_get_m_localPointB)( _ref(btManifoldPoint)* _this ) {
	return alloc_ref(new btVector3(_unref(_this)->m_localPointB),btVector3);
}
HL_PRIM _ref(btVector3)* HL_NAME(btManifoldPoint_set_m_localPointB)( _ref(btManifoldPoint)* _this, _ref(btVector3)* value ) {
	_unref(_this)->m_localPointB = *_unref(value);
	return value;
}
DEFINE_PRIM(_IDL,btManifoldPoint_get_m_localPointB,_IDL);
DEFINE_PRIM(_IDL,btManifoldPoint_set_m_localPointB,_IDL _IDL);

HL_PRIM _ref(btVector3)* HL_NAME(btManifoldPoint_get_m_positionWorldOnB)( _ref(btManifoldPoint)* _this ) {
	return alloc_ref(new btVector3(_unref(_this)->m_positionWorldOnB),btVector3);
}
HL_PRIM _ref(btVector3)* HL_NAME(btManifoldPoint_set_m_positionWorldOnB)( _ref(btManifoldPoint)* _this, _ref(btVector3)* value ) {
	_unref(_this)->m_positionWorldOnB = *_unref(value);
	return value;
}
DEFINE_PRIM(_IDL,btManifoldPoint_get_m_positionWorldOnB,_IDL);
DEFINE_PRIM(_IDL,btManifoldPoint_set_m_positionWorldOnB,_IDL _IDL);

HL_PRIM _ref(btVector3)* HL_NAME(btManifoldPoint_get_m_positionWorldOnA)( _ref(btManifoldPoint)* _this ) {
	return alloc_ref(new btVector3(_unref(_this)->m_positionWorldOnA),btVector3);
}
HL_PRIM _ref(btVector3)* HL_NAME(btManifoldPoint_set_m_positionWorldOnA)( _ref(btManifoldPoint)* _this, _ref(btVector3)* value ) {
	_unref(_this)->m_positionWorldOnA = *_unref(value);
	return value;
}
DEFINE_PRIM(_IDL,btManifoldPoint_get_m_positionWorldOnA,_IDL);
DEFINE_PRIM(_IDL,btManifoldPoint_set_m_positionWorldOnA,_IDL _IDL);

HL_PRIM _ref(btVector3)* HL_NAME(btManifoldPoint_get_m_normalWorldOnB)( _ref(btManifoldPoint)* _this ) {
	return alloc_ref(new btVector3(_unref(_this)->m_normalWorldOnB),btVector3);
}
HL_PRIM _ref(btVector3)* HL_NAME(btManifoldPoint_set_m_normalWorldOnB)( _ref(btManifoldPoint)* _this, _ref(btVector3)* value ) {
	_unref(_this)->m_normalWorldOnB = *_unref(value);
	return value;
}
DEFINE_PRIM(_IDL,btManifoldPoint_get_m_normalWorldOnB,_IDL);
DEFINE_PRIM(_IDL,btManifoldPoint_set_m_normalWorldOnB,_IDL _IDL);

HL_PRIM float HL_NAME(ContactResultCallback_addSingleResult7)(_ref(btCollisionWorld::ContactResultCallback)* _this, _ref(btManifoldPoint)* cp, _ref(btCollisionObjectWrapper)* colObj0Wrap, int partId0, int index0, _ref(btCollisionObjectWrapper)* colObj1Wrap, int partId1, int index1) {
	return _unref(_this)->addSingleResult(*_unref(cp), _unref(colObj0Wrap), partId0, index0, _unref(colObj1Wrap), partId1, index1);
}
DEFINE_PRIM(_F32, ContactResultCallback_addSingleResult7, _IDL _IDL _IDL _I32 _I32 _IDL _I32 _I32);

HL_PRIM int HL_NAME(LocalShapeInfo_get_m_shapePart)( _ref(btCollisionWorld::LocalShapeInfo)* _this ) {
	return _unref(_this)->m_shapePart;
}
HL_PRIM int HL_NAME(LocalShapeInfo_set_m_shapePart)( _ref(btCollisionWorld::LocalShapeInfo)* _this, int value ) {
	_unref(_this)->m_shapePart = (value);
	return value;
}
DEFINE_PRIM(_I32,LocalShapeInfo_get_m_shapePart,_IDL);
DEFINE_PRIM(_I32,LocalShapeInfo_set_m_shapePart,_IDL _I32);

HL_PRIM int HL_NAME(LocalShapeInfo_get_m_triangleIndex)( _ref(btCollisionWorld::LocalShapeInfo)* _this ) {
	return _unref(_this)->m_triangleIndex;
}
HL_PRIM int HL_NAME(LocalShapeInfo_set_m_triangleIndex)( _ref(btCollisionWorld::LocalShapeInfo)* _this, int value ) {
	_unref(_this)->m_triangleIndex = (value);
	return value;
}
DEFINE_PRIM(_I32,LocalShapeInfo_get_m_triangleIndex,_IDL);
DEFINE_PRIM(_I32,LocalShapeInfo_set_m_triangleIndex,_IDL _I32);

HL_PRIM _ref(btCollisionWorld::LocalConvexResult)* HL_NAME(LocalConvexResult_new5)(_ref(btCollisionObject)* hitCollisionObject, _ref(btCollisionWorld::LocalShapeInfo)* localShapeInfo, _ref(btVector3)* hitNormalLocal, _ref(btVector3)* hitPointLocal, float hitFraction) {
	return alloc_ref((new btCollisionWorld::LocalConvexResult(_unref(hitCollisionObject), _unref(localShapeInfo), *_unref(hitNormalLocal), *_unref(hitPointLocal), hitFraction)),LocalConvexResult);
}
DEFINE_PRIM(_IDL, LocalConvexResult_new5, _IDL _IDL _IDL _IDL _F32);

HL_PRIM HL_CONST _ref(btCollisionObject)* HL_NAME(LocalConvexResult_get_m_hitCollisionObject)( _ref(btCollisionWorld::LocalConvexResult)* _this ) {
	return alloc_ref_const(_unref(_this)->m_hitCollisionObject,btCollisionObject);
}
HL_PRIM HL_CONST _ref(btCollisionObject)* HL_NAME(LocalConvexResult_set_m_hitCollisionObject)( _ref(btCollisionWorld::LocalConvexResult)* _this, HL_CONST _ref(btCollisionObject)* value ) {
	_unref(_this)->m_hitCollisionObject = _unref(value);
	return value;
}
DEFINE_PRIM(_IDL,LocalConvexResult_get_m_hitCollisionObject,_IDL);
DEFINE_PRIM(_IDL,LocalConvexResult_set_m_hitCollisionObject,_IDL _IDL);

HL_PRIM _ref(btCollisionWorld::LocalShapeInfo)* HL_NAME(LocalConvexResult_get_m_localShapeInfo)( _ref(btCollisionWorld::LocalConvexResult)* _this ) {
	return alloc_ref(_unref(_this)->m_localShapeInfo,LocalShapeInfo);
}
HL_PRIM _ref(btCollisionWorld::LocalShapeInfo)* HL_NAME(LocalConvexResult_set_m_localShapeInfo)( _ref(btCollisionWorld::LocalConvexResult)* _this, _ref(btCollisionWorld::LocalShapeInfo)* value ) {
	_unref(_this)->m_localShapeInfo = _unref(value);
	return value;
}
DEFINE_PRIM(_IDL,LocalConvexResult_get_m_localShapeInfo,_IDL);
DEFINE_PRIM(_IDL,LocalConvexResult_set_m_localShapeInfo,_IDL _IDL);

HL_PRIM _ref(btVector3)* HL_NAME(LocalConvexResult_get_m_hitNormalLocal)( _ref(btCollisionWorld::LocalConvexResult)* _this ) {
	return alloc_ref(new btVector3(_unref(_this)->m_hitNormalLocal),btVector3);
}
HL_PRIM _ref(btVector3)* HL_NAME(LocalConvexResult_set_m_hitNormalLocal)( _ref(btCollisionWorld::LocalConvexResult)* _this, _ref(btVector3)* value ) {
	_unref(_this)->m_hitNormalLocal = *_unref(value);
	return value;
}
DEFINE_PRIM(_IDL,LocalConvexResult_get_m_hitNormalLocal,_IDL);
DEFINE_PRIM(_IDL,LocalConvexResult_set_m_hitNormalLocal,_IDL _IDL);

HL_PRIM _ref(btVector3)* HL_NAME(LocalConvexResult_get_m_hitPointLocal)( _ref(btCollisionWorld::LocalConvexResult)* _this ) {
	return alloc_ref(new btVector3(_unref(_this)->m_hitPointLocal),btVector3);
}
HL_PRIM _ref(btVector3)* HL_NAME(LocalConvexResult_set_m_hitPointLocal)( _ref(btCollisionWorld::LocalConvexResult)* _this, _ref(btVector3)* value ) {
	_unref(_this)->m_hitPointLocal = *_unref(value);
	return value;
}
DEFINE_PRIM(_IDL,LocalConvexResult_get_m_hitPointLocal,_IDL);
DEFINE_PRIM(_IDL,LocalConvexResult_set_m_hitPointLocal,_IDL _IDL);

HL_PRIM float HL_NAME(LocalConvexResult_get_m_hitFraction)( _ref(btCollisionWorld::LocalConvexResult)* _this ) {
	return _unref(_this)->m_hitFraction;
}
HL_PRIM float HL_NAME(LocalConvexResult_set_m_hitFraction)( _ref(btCollisionWorld::LocalConvexResult)* _this, float value ) {
	_unref(_this)->m_hitFraction = (value);
	return value;
}
DEFINE_PRIM(_F32,LocalConvexResult_get_m_hitFraction,_IDL);
DEFINE_PRIM(_F32,LocalConvexResult_set_m_hitFraction,_IDL _F32);

HL_PRIM bool HL_NAME(ConvexResultCallback_hasHit0)(_ref(btCollisionWorld::ConvexResultCallback)* _this) {
	return _unref(_this)->hasHit();
}
DEFINE_PRIM(_BOOL, ConvexResultCallback_hasHit0, _IDL);

HL_PRIM short HL_NAME(ConvexResultCallback_get_m_collisionFilterGroup)( _ref(btCollisionWorld::ConvexResultCallback)* _this ) {
	return _unref(_this)->m_collisionFilterGroup;
}
HL_PRIM short HL_NAME(ConvexResultCallback_set_m_collisionFilterGroup)( _ref(btCollisionWorld::ConvexResultCallback)* _this, short value ) {
	_unref(_this)->m_collisionFilterGroup = (value);
	return value;
}
DEFINE_PRIM(_I16,ConvexResultCallback_get_m_collisionFilterGroup,_IDL);
DEFINE_PRIM(_I16,ConvexResultCallback_set_m_collisionFilterGroup,_IDL _I16);

HL_PRIM short HL_NAME(ConvexResultCallback_get_m_collisionFilterMask)( _ref(btCollisionWorld::ConvexResultCallback)* _this ) {
	return _unref(_this)->m_collisionFilterMask;
}
HL_PRIM short HL_NAME(ConvexResultCallback_set_m_collisionFilterMask)( _ref(btCollisionWorld::ConvexResultCallback)* _this, short value ) {
	_unref(_this)->m_collisionFilterMask = (value);
	return value;
}
DEFINE_PRIM(_I16,ConvexResultCallback_get_m_collisionFilterMask,_IDL);
DEFINE_PRIM(_I16,ConvexResultCallback_set_m_collisionFilterMask,_IDL _I16);

HL_PRIM float HL_NAME(ConvexResultCallback_get_m_closestHitFraction)( _ref(btCollisionWorld::ConvexResultCallback)* _this ) {
	return _unref(_this)->m_closestHitFraction;
}
HL_PRIM float HL_NAME(ConvexResultCallback_set_m_closestHitFraction)( _ref(btCollisionWorld::ConvexResultCallback)* _this, float value ) {
	_unref(_this)->m_closestHitFraction = (value);
	return value;
}
DEFINE_PRIM(_F32,ConvexResultCallback_get_m_closestHitFraction,_IDL);
DEFINE_PRIM(_F32,ConvexResultCallback_set_m_closestHitFraction,_IDL _F32);

HL_PRIM _ref(btCollisionWorld::ClosestConvexResultCallback)* HL_NAME(ClosestConvexResultCallback_new2)(_ref(btVector3)* convexFromWorld, _ref(btVector3)* convexToWorld) {
	return alloc_ref((new btCollisionWorld::ClosestConvexResultCallback(*_unref(convexFromWorld), *_unref(convexToWorld))),ClosestConvexResultCallback);
}
DEFINE_PRIM(_IDL, ClosestConvexResultCallback_new2, _IDL _IDL);

HL_PRIM _ref(btVector3)* HL_NAME(ClosestConvexResultCallback_get_m_convexFromWorld)( _ref(btCollisionWorld::ClosestConvexResultCallback)* _this ) {
	return alloc_ref(new btVector3(_unref(_this)->m_convexFromWorld),btVector3);
}
HL_PRIM _ref(btVector3)* HL_NAME(ClosestConvexResultCallback_set_m_convexFromWorld)( _ref(btCollisionWorld::ClosestConvexResultCallback)* _this, _ref(btVector3)* value ) {
	_unref(_this)->m_convexFromWorld = *_unref(value);
	return value;
}
DEFINE_PRIM(_IDL,ClosestConvexResultCallback_get_m_convexFromWorld,_IDL);
DEFINE_PRIM(_IDL,ClosestConvexResultCallback_set_m_convexFromWorld,_IDL _IDL);

HL_PRIM _ref(btVector3)* HL_NAME(ClosestConvexResultCallback_get_m_convexToWorld)( _ref(btCollisionWorld::ClosestConvexResultCallback)* _this ) {
	return alloc_ref(new btVector3(_unref(_this)->m_convexToWorld),btVector3);
}
HL_PRIM _ref(btVector3)* HL_NAME(ClosestConvexResultCallback_set_m_convexToWorld)( _ref(btCollisionWorld::ClosestConvexResultCallback)* _this, _ref(btVector3)* value ) {
	_unref(_this)->m_convexToWorld = *_unref(value);
	return value;
}
DEFINE_PRIM(_IDL,ClosestConvexResultCallback_get_m_convexToWorld,_IDL);
DEFINE_PRIM(_IDL,ClosestConvexResultCallback_set_m_convexToWorld,_IDL _IDL);

HL_PRIM _ref(btVector3)* HL_NAME(ClosestConvexResultCallback_get_m_hitNormalWorld)( _ref(btCollisionWorld::ClosestConvexResultCallback)* _this ) {
	return alloc_ref(new btVector3(_unref(_this)->m_hitNormalWorld),btVector3);
}
HL_PRIM _ref(btVector3)* HL_NAME(ClosestConvexResultCallback_set_m_hitNormalWorld)( _ref(btCollisionWorld::ClosestConvexResultCallback)* _this, _ref(btVector3)* value ) {
	_unref(_this)->m_hitNormalWorld = *_unref(value);
	return value;
}
DEFINE_PRIM(_IDL,ClosestConvexResultCallback_get_m_hitNormalWorld,_IDL);
DEFINE_PRIM(_IDL,ClosestConvexResultCallback_set_m_hitNormalWorld,_IDL _IDL);

HL_PRIM _ref(btVector3)* HL_NAME(ClosestConvexResultCallback_get_m_hitPointWorld)( _ref(btCollisionWorld::ClosestConvexResultCallback)* _this ) {
	return alloc_ref(new btVector3(_unref(_this)->m_hitPointWorld),btVector3);
}
HL_PRIM _ref(btVector3)* HL_NAME(ClosestConvexResultCallback_set_m_hitPointWorld)( _ref(btCollisionWorld::ClosestConvexResultCallback)* _this, _ref(btVector3)* value ) {
	_unref(_this)->m_hitPointWorld = *_unref(value);
	return value;
}
DEFINE_PRIM(_IDL,ClosestConvexResultCallback_get_m_hitPointWorld,_IDL);
DEFINE_PRIM(_IDL,ClosestConvexResultCallback_set_m_hitPointWorld,_IDL _IDL);

HL_PRIM void HL_NAME(btCollisionShape_setLocalScaling1)(_ref(btCollisionShape)* _this, _ref(btVector3)* scaling) {
	_unref(_this)->setLocalScaling(*_unref(scaling));
}
DEFINE_PRIM(_VOID, btCollisionShape_setLocalScaling1, _IDL _IDL);

HL_PRIM void HL_NAME(btCollisionShape_calculateLocalInertia2)(_ref(btCollisionShape)* _this, float mass, _ref(btVector3)* inertia) {
	_unref(_this)->calculateLocalInertia(mass, *_unref(inertia));
}
DEFINE_PRIM(_VOID, btCollisionShape_calculateLocalInertia2, _IDL _F32 _IDL);

HL_PRIM void HL_NAME(btCollisionShape_setMargin1)(_ref(btCollisionShape)* _this, float margin) {
	_unref(_this)->setMargin(margin);
}
DEFINE_PRIM(_VOID, btCollisionShape_setMargin1, _IDL _F32);

HL_PRIM float HL_NAME(btCollisionShape_getMargin0)(_ref(btCollisionShape)* _this) {
	return _unref(_this)->getMargin();
}
DEFINE_PRIM(_F32, btCollisionShape_getMargin0, _IDL);

HL_PRIM _ref(btConvexTriangleMeshShape)* HL_NAME(btConvexTriangleMeshShape_new2)(_ref(btStridingMeshInterface)* meshInterface, _OPT(bool) calcAabb) {
	if( !calcAabb )
		return alloc_ref((new btConvexTriangleMeshShape(_unref(meshInterface))),btConvexTriangleMeshShape);
	else
		return alloc_ref((new btConvexTriangleMeshShape(_unref(meshInterface), _GET_OPT(calcAabb,b))),btConvexTriangleMeshShape);
}
DEFINE_PRIM(_IDL, btConvexTriangleMeshShape_new2, _IDL _NULL(_BOOL));

HL_PRIM _ref(btBoxShape)* HL_NAME(btBoxShape_new1)(_ref(btVector3)* boxHalfExtents) {
	return alloc_ref((new btBoxShape(*_unref(boxHalfExtents))),btBoxShape);
}
DEFINE_PRIM(_IDL, btBoxShape_new1, _IDL);

HL_PRIM void HL_NAME(btBoxShape_setMargin1)(_ref(btBoxShape)* _this, float margin) {
	_unref(_this)->setMargin(margin);
}
DEFINE_PRIM(_VOID, btBoxShape_setMargin1, _IDL _F32);

HL_PRIM float HL_NAME(btBoxShape_getMargin0)(_ref(btBoxShape)* _this) {
	return _unref(_this)->getMargin();
}
DEFINE_PRIM(_F32, btBoxShape_getMargin0, _IDL);

HL_PRIM _ref(btCapsuleShape)* HL_NAME(btCapsuleShape_new2)(float radius, float height) {
	return alloc_ref((new btCapsuleShape(radius, height)),btCapsuleShape);
}
DEFINE_PRIM(_IDL, btCapsuleShape_new2, _F32 _F32);

HL_PRIM void HL_NAME(btCapsuleShape_setMargin1)(_ref(btCapsuleShape)* _this, float margin) {
	_unref(_this)->setMargin(margin);
}
DEFINE_PRIM(_VOID, btCapsuleShape_setMargin1, _IDL _F32);

HL_PRIM float HL_NAME(btCapsuleShape_getMargin0)(_ref(btCapsuleShape)* _this) {
	return _unref(_this)->getMargin();
}
DEFINE_PRIM(_F32, btCapsuleShape_getMargin0, _IDL);

HL_PRIM _ref(btCapsuleShapeX)* HL_NAME(btCapsuleShapeX_new2)(float radius, float height) {
	return alloc_ref((new btCapsuleShapeX(radius, height)),btCapsuleShapeX);
}
DEFINE_PRIM(_IDL, btCapsuleShapeX_new2, _F32 _F32);

HL_PRIM void HL_NAME(btCapsuleShapeX_setMargin1)(_ref(btCapsuleShapeX)* _this, float margin) {
	_unref(_this)->setMargin(margin);
}
DEFINE_PRIM(_VOID, btCapsuleShapeX_setMargin1, _IDL _F32);

HL_PRIM float HL_NAME(btCapsuleShapeX_getMargin0)(_ref(btCapsuleShapeX)* _this) {
	return _unref(_this)->getMargin();
}
DEFINE_PRIM(_F32, btCapsuleShapeX_getMargin0, _IDL);

HL_PRIM _ref(btCapsuleShapeZ)* HL_NAME(btCapsuleShapeZ_new2)(float radius, float height) {
	return alloc_ref((new btCapsuleShapeZ(radius, height)),btCapsuleShapeZ);
}
DEFINE_PRIM(_IDL, btCapsuleShapeZ_new2, _F32 _F32);

HL_PRIM void HL_NAME(btCapsuleShapeZ_setMargin1)(_ref(btCapsuleShapeZ)* _this, float margin) {
	_unref(_this)->setMargin(margin);
}
DEFINE_PRIM(_VOID, btCapsuleShapeZ_setMargin1, _IDL _F32);

HL_PRIM float HL_NAME(btCapsuleShapeZ_getMargin0)(_ref(btCapsuleShapeZ)* _this) {
	return _unref(_this)->getMargin();
}
DEFINE_PRIM(_F32, btCapsuleShapeZ_getMargin0, _IDL);

HL_PRIM _ref(btCylinderShape)* HL_NAME(btCylinderShape_new1)(_ref(btVector3)* halfExtents) {
	return alloc_ref((new btCylinderShape(*_unref(halfExtents))),btCylinderShape);
}
DEFINE_PRIM(_IDL, btCylinderShape_new1, _IDL);

HL_PRIM void HL_NAME(btCylinderShape_setMargin1)(_ref(btCylinderShape)* _this, float margin) {
	_unref(_this)->setMargin(margin);
}
DEFINE_PRIM(_VOID, btCylinderShape_setMargin1, _IDL _F32);

HL_PRIM float HL_NAME(btCylinderShape_getMargin0)(_ref(btCylinderShape)* _this) {
	return _unref(_this)->getMargin();
}
DEFINE_PRIM(_F32, btCylinderShape_getMargin0, _IDL);

HL_PRIM _ref(btCylinderShapeX)* HL_NAME(btCylinderShapeX_new1)(_ref(btVector3)* halfExtents) {
	return alloc_ref((new btCylinderShapeX(*_unref(halfExtents))),btCylinderShapeX);
}
DEFINE_PRIM(_IDL, btCylinderShapeX_new1, _IDL);

HL_PRIM void HL_NAME(btCylinderShapeX_setMargin1)(_ref(btCylinderShapeX)* _this, float margin) {
	_unref(_this)->setMargin(margin);
}
DEFINE_PRIM(_VOID, btCylinderShapeX_setMargin1, _IDL _F32);

HL_PRIM float HL_NAME(btCylinderShapeX_getMargin0)(_ref(btCylinderShapeX)* _this) {
	return _unref(_this)->getMargin();
}
DEFINE_PRIM(_F32, btCylinderShapeX_getMargin0, _IDL);

HL_PRIM _ref(btCylinderShapeZ)* HL_NAME(btCylinderShapeZ_new1)(_ref(btVector3)* halfExtents) {
	return alloc_ref((new btCylinderShapeZ(*_unref(halfExtents))),btCylinderShapeZ);
}
DEFINE_PRIM(_IDL, btCylinderShapeZ_new1, _IDL);

HL_PRIM void HL_NAME(btCylinderShapeZ_setMargin1)(_ref(btCylinderShapeZ)* _this, float margin) {
	_unref(_this)->setMargin(margin);
}
DEFINE_PRIM(_VOID, btCylinderShapeZ_setMargin1, _IDL _F32);

HL_PRIM float HL_NAME(btCylinderShapeZ_getMargin0)(_ref(btCylinderShapeZ)* _this) {
	return _unref(_this)->getMargin();
}
DEFINE_PRIM(_F32, btCylinderShapeZ_getMargin0, _IDL);

HL_PRIM _ref(btSphereShape)* HL_NAME(btSphereShape_new1)(float radius) {
	return alloc_ref((new btSphereShape(radius)),btSphereShape);
}
DEFINE_PRIM(_IDL, btSphereShape_new1, _F32);

HL_PRIM void HL_NAME(btSphereShape_setMargin1)(_ref(btSphereShape)* _this, float margin) {
	_unref(_this)->setMargin(margin);
}
DEFINE_PRIM(_VOID, btSphereShape_setMargin1, _IDL _F32);

HL_PRIM float HL_NAME(btSphereShape_getMargin0)(_ref(btSphereShape)* _this) {
	return _unref(_this)->getMargin();
}
DEFINE_PRIM(_F32, btSphereShape_getMargin0, _IDL);

HL_PRIM _ref(btConeShape)* HL_NAME(btConeShape_new2)(float radius, float height) {
	return alloc_ref((new btConeShape(radius, height)),btConeShape);
}
DEFINE_PRIM(_IDL, btConeShape_new2, _F32 _F32);

HL_PRIM _ref(btConvexHullShape)* HL_NAME(btConvexHullShape_new0)() {
	return alloc_ref((new btConvexHullShape()),btConvexHullShape);
}
DEFINE_PRIM(_IDL, btConvexHullShape_new0,);

HL_PRIM void HL_NAME(btConvexHullShape_addPoint2)(_ref(btConvexHullShape)* _this, _ref(btVector3)* point, _OPT(bool) recalculateLocalAABB) {
	if( !recalculateLocalAABB )
		_unref(_this)->addPoint(*_unref(point));
	else
		_unref(_this)->addPoint(*_unref(point), _GET_OPT(recalculateLocalAABB,b));
}
DEFINE_PRIM(_VOID, btConvexHullShape_addPoint2, _IDL _IDL _NULL(_BOOL));

HL_PRIM void HL_NAME(btConvexHullShape_setMargin1)(_ref(btConvexHullShape)* _this, float margin) {
	_unref(_this)->setMargin(margin);
}
DEFINE_PRIM(_VOID, btConvexHullShape_setMargin1, _IDL _F32);

HL_PRIM float HL_NAME(btConvexHullShape_getMargin0)(_ref(btConvexHullShape)* _this) {
	return _unref(_this)->getMargin();
}
DEFINE_PRIM(_F32, btConvexHullShape_getMargin0, _IDL);

HL_PRIM _ref(btConeShapeX)* HL_NAME(btConeShapeX_new2)(float radius, float height) {
	return alloc_ref((new btConeShapeX(radius, height)),btConeShapeX);
}
DEFINE_PRIM(_IDL, btConeShapeX_new2, _F32 _F32);

HL_PRIM _ref(btConeShapeZ)* HL_NAME(btConeShapeZ_new2)(float radius, float height) {
	return alloc_ref((new btConeShapeZ(radius, height)),btConeShapeZ);
}
DEFINE_PRIM(_IDL, btConeShapeZ_new2, _F32 _F32);

HL_PRIM _ref(btCompoundShape)* HL_NAME(btCompoundShape_new1)(_OPT(bool) enableDynamicAabbTree) {
	if( !enableDynamicAabbTree )
		return alloc_ref((new btCompoundShape()),btCompoundShape);
	else
		return alloc_ref((new btCompoundShape(_GET_OPT(enableDynamicAabbTree,b))),btCompoundShape);
}
DEFINE_PRIM(_IDL, btCompoundShape_new1, _NULL(_BOOL));

HL_PRIM void HL_NAME(btCompoundShape_addChildShape2)(_ref(btCompoundShape)* _this, _ref(btTransform)* localTransform, _ref(btCollisionShape)* shape) {
	_unref(_this)->addChildShape(*_unref(localTransform), _unref(shape));
}
DEFINE_PRIM(_VOID, btCompoundShape_addChildShape2, _IDL _IDL _IDL);

HL_PRIM void HL_NAME(btCompoundShape_removeChildShapeByIndex1)(_ref(btCompoundShape)* _this, int childShapeindex) {
	_unref(_this)->removeChildShapeByIndex(childShapeindex);
}
DEFINE_PRIM(_VOID, btCompoundShape_removeChildShapeByIndex1, _IDL _I32);

HL_PRIM HL_CONST int HL_NAME(btCompoundShape_getNumChildShapes0)(_ref(btCompoundShape)* _this) {
	return _unref(_this)->getNumChildShapes();
}
DEFINE_PRIM(_I32, btCompoundShape_getNumChildShapes0, _IDL);

HL_PRIM _ref(btCollisionShape)* HL_NAME(btCompoundShape_getChildShape1)(_ref(btCompoundShape)* _this, int index) {
	return alloc_ref((_unref(_this)->getChildShape(index)),btCollisionShape);
}
DEFINE_PRIM(_IDL, btCompoundShape_getChildShape1, _IDL _I32);

HL_PRIM void HL_NAME(btCompoundShape_setMargin1)(_ref(btCompoundShape)* _this, float margin) {
	_unref(_this)->setMargin(margin);
}
DEFINE_PRIM(_VOID, btCompoundShape_setMargin1, _IDL _F32);

HL_PRIM float HL_NAME(btCompoundShape_getMargin0)(_ref(btCompoundShape)* _this) {
	return _unref(_this)->getMargin();
}
DEFINE_PRIM(_F32, btCompoundShape_getMargin0, _IDL);

HL_PRIM _ref(btTriangleMesh)* HL_NAME(btTriangleMesh_new2)(_OPT(bool) use32bitIndices, _OPT(bool) use4componentVertices) {
	if( !use32bitIndices )
		return alloc_ref((new btTriangleMesh()),btTriangleMesh);
	else
	if( !use4componentVertices )
		return alloc_ref((new btTriangleMesh(_GET_OPT(use32bitIndices,b))),btTriangleMesh);
	else
		return alloc_ref((new btTriangleMesh(_GET_OPT(use32bitIndices,b), _GET_OPT(use4componentVertices,b))),btTriangleMesh);
}
DEFINE_PRIM(_IDL, btTriangleMesh_new2, _NULL(_BOOL) _NULL(_BOOL));

HL_PRIM void HL_NAME(btTriangleMesh_addTriangle4)(_ref(btTriangleMesh)* _this, _ref(btVector3)* vertex0, _ref(btVector3)* vertex1, _ref(btVector3)* vertex2, _OPT(bool) removeDuplicateVertices) {
	if( !removeDuplicateVertices )
		_unref(_this)->addTriangle(*_unref(vertex0), *_unref(vertex1), *_unref(vertex2));
	else
		_unref(_this)->addTriangle(*_unref(vertex0), *_unref(vertex1), *_unref(vertex2), _GET_OPT(removeDuplicateVertices,b));
}
DEFINE_PRIM(_VOID, btTriangleMesh_addTriangle4, _IDL _IDL _IDL _IDL _NULL(_BOOL));

HL_PRIM _ref(btStaticPlaneShape)* HL_NAME(btStaticPlaneShape_new2)(_ref(btVector3)* planeNormal, float planeConstant) {
	return alloc_ref((new btStaticPlaneShape(*_unref(planeNormal), planeConstant)),btStaticPlaneShape);
}
DEFINE_PRIM(_IDL, btStaticPlaneShape_new2, _IDL _F32);

HL_PRIM _ref(btBvhTriangleMeshShape)* HL_NAME(btBvhTriangleMeshShape_new3)(_ref(btStridingMeshInterface)* meshInterface, bool useQuantizedAabbCompression, _OPT(bool) buildBvh) {
	if( !buildBvh )
		return alloc_ref((new btBvhTriangleMeshShape(_unref(meshInterface), useQuantizedAabbCompression)),btBvhTriangleMeshShape);
	else
		return alloc_ref((new btBvhTriangleMeshShape(_unref(meshInterface), useQuantizedAabbCompression, _GET_OPT(buildBvh,b))),btBvhTriangleMeshShape);
}
DEFINE_PRIM(_IDL, btBvhTriangleMeshShape_new3, _IDL _BOOL _NULL(_BOOL));

HL_PRIM _ref(btHeightfieldTerrainShape)* HL_NAME(btHeightfieldTerrainShape_new9)(int heightStickWidth, int heightStickLength, void* heightfieldData, float heightScale, float minHeight, float maxHeight, int upAxis, int hdt, bool flipQuadEdges) {
	return alloc_ref((new btHeightfieldTerrainShape(heightStickWidth, heightStickLength, heightfieldData, heightScale, minHeight, maxHeight, upAxis, PHY_ScalarType__values[hdt], flipQuadEdges)),btHeightfieldTerrainShape);
}
DEFINE_PRIM(_IDL, btHeightfieldTerrainShape_new9, _I32 _I32 _BYTES _F32 _F32 _F32 _I32 _I32 _BOOL);

HL_PRIM void HL_NAME(btHeightfieldTerrainShape_setMargin1)(_ref(btHeightfieldTerrainShape)* _this, float margin) {
	_unref(_this)->setMargin(margin);
}
DEFINE_PRIM(_VOID, btHeightfieldTerrainShape_setMargin1, _IDL _F32);

HL_PRIM float HL_NAME(btHeightfieldTerrainShape_getMargin0)(_ref(btHeightfieldTerrainShape)* _this) {
	return _unref(_this)->getMargin();
}
DEFINE_PRIM(_F32, btHeightfieldTerrainShape_getMargin0, _IDL);

HL_PRIM _ref(btGImpactMeshShape)* HL_NAME(btGImpactMeshShape_new1)(_ref(btStridingMeshInterface)* meshInterface) {
	return alloc_ref((new btGImpactMeshShape(meshInterface)),btGImpactMeshShape);
}
DEFINE_PRIM(_IDL, btGImpactMeshShape_new1, _IDL);

HL_PRIM void HL_NAME(btGImpactMeshShape_updateBound0)(_ref(btGImpactMeshShape)* _this) {
	_unref(_this)->updateBound();
}
DEFINE_PRIM(_VOID, btGImpactMeshShape_updateBound0, _IDL);

HL_PRIM void HL_NAME(btGImpactMeshShape_registerAlgorithm1)(_ref(btGImpactMeshShape)* _this, _ref(btCollisionDispatcher)* dispatcher) {
	btGImpactCollisionAlgorithm::registerAlgorithm(dispatcher);
}
DEFINE_PRIM(_VOID, btGImpactMeshShape_registerAlgorithm1, _IDL _IDL);

HL_PRIM _ref(btDefaultCollisionConstructionInfo)* HL_NAME(btDefaultCollisionConstructionInfo_new0)() {
	return alloc_ref((new btDefaultCollisionConstructionInfo()),btDefaultCollisionConstructionInfo);
}
DEFINE_PRIM(_IDL, btDefaultCollisionConstructionInfo_new0,);

HL_PRIM _ref(btDefaultCollisionConfiguration)* HL_NAME(btDefaultCollisionConfiguration_new1)(_ref(btDefaultCollisionConstructionInfo)* info) {
	if( !info )
		return alloc_ref((new btDefaultCollisionConfiguration()),btDefaultCollisionConfiguration);
	else
		return alloc_ref((new btDefaultCollisionConfiguration(*_unref(info))),btDefaultCollisionConfiguration);
}
DEFINE_PRIM(_IDL, btDefaultCollisionConfiguration_new1, _IDL);

HL_PRIM _ref(btPersistentManifold)* HL_NAME(btPersistentManifold_new0)() {
	return alloc_ref((new btPersistentManifold()),btPersistentManifold);
}
DEFINE_PRIM(_IDL, btPersistentManifold_new0,);

HL_PRIM HL_CONST _ref(btCollisionObject)* HL_NAME(btPersistentManifold_getBody00)(_ref(btPersistentManifold)* _this) {
	return alloc_ref_const((_unref(_this)->getBody0()),btCollisionObject);
}
DEFINE_PRIM(_IDL, btPersistentManifold_getBody00, _IDL);

HL_PRIM HL_CONST _ref(btCollisionObject)* HL_NAME(btPersistentManifold_getBody10)(_ref(btPersistentManifold)* _this) {
	return alloc_ref_const((_unref(_this)->getBody1()),btCollisionObject);
}
DEFINE_PRIM(_IDL, btPersistentManifold_getBody10, _IDL);

HL_PRIM int HL_NAME(btPersistentManifold_getNumContacts0)(_ref(btPersistentManifold)* _this) {
	return _unref(_this)->getNumContacts();
}
DEFINE_PRIM(_I32, btPersistentManifold_getNumContacts0, _IDL);

HL_PRIM _ref(btManifoldPoint)* HL_NAME(btPersistentManifold_getContactPoint1)(_ref(btPersistentManifold)* _this, int index) {
	return alloc_ref(new btManifoldPoint(_unref(_this)->getContactPoint(index)),btManifoldPoint);
}
DEFINE_PRIM(_IDL, btPersistentManifold_getContactPoint1, _IDL _I32);

HL_PRIM int HL_NAME(btDispatcher_getNumManifolds0)(_ref(btDispatcher)* _this) {
	return _unref(_this)->getNumManifolds();
}
DEFINE_PRIM(_I32, btDispatcher_getNumManifolds0, _IDL);

HL_PRIM _ref(btPersistentManifold)* HL_NAME(btDispatcher_getManifoldByIndexInternal1)(_ref(btDispatcher)* _this, int index) {
	return alloc_ref((_unref(_this)->getManifoldByIndexInternal(index)),btPersistentManifold);
}
DEFINE_PRIM(_IDL, btDispatcher_getManifoldByIndexInternal1, _IDL _I32);

HL_PRIM _ref(btCollisionDispatcher)* HL_NAME(btCollisionDispatcher_new1)(_ref(btDefaultCollisionConfiguration)* conf) {
	return alloc_ref((new btCollisionDispatcher(_unref(conf))),btCollisionDispatcher);
}
DEFINE_PRIM(_IDL, btCollisionDispatcher_new1, _IDL);

HL_PRIM void HL_NAME(btOverlappingPairCache_setInternalGhostPairCallback1)(_ref(btOverlappingPairCache)* _this, _ref(btOverlappingPairCallback)* ghostPairCallback) {
	_unref(_this)->setInternalGhostPairCallback(_unref(ghostPairCallback));
}
DEFINE_PRIM(_VOID, btOverlappingPairCache_setInternalGhostPairCallback1, _IDL _IDL);

HL_PRIM _ref(btAxisSweep3)* HL_NAME(btAxisSweep3_new5)(_ref(btVector3)* worldAabbMin, _ref(btVector3)* worldAabbMax, _OPT(int) maxHandles, _ref(btOverlappingPairCache)* pairCache, _OPT(bool) disableRaycastAccelerator) {
	if( !maxHandles )
		return alloc_ref((new btAxisSweep3(*_unref(worldAabbMin), *_unref(worldAabbMax))),btAxisSweep3);
	else
	if( !pairCache )
		return alloc_ref((new btAxisSweep3(*_unref(worldAabbMin), *_unref(worldAabbMax), _GET_OPT(maxHandles,i))),btAxisSweep3);
	else
	if( !disableRaycastAccelerator )
		return alloc_ref((new btAxisSweep3(*_unref(worldAabbMin), *_unref(worldAabbMax), _GET_OPT(maxHandles,i), _unref(pairCache))),btAxisSweep3);
	else
		return alloc_ref((new btAxisSweep3(*_unref(worldAabbMin), *_unref(worldAabbMax), _GET_OPT(maxHandles,i), _unref(pairCache), _GET_OPT(disableRaycastAccelerator,b))),btAxisSweep3);
}
DEFINE_PRIM(_IDL, btAxisSweep3_new5, _IDL _IDL _NULL(_I32) _IDL _NULL(_BOOL));

HL_PRIM _ref(btDbvtBroadphase)* HL_NAME(btDbvtBroadphase_new0)() {
	return alloc_ref((new btDbvtBroadphase()),btDbvtBroadphase);
}
DEFINE_PRIM(_IDL, btDbvtBroadphase_new0,);

HL_PRIM _ref(btRigidBody::btRigidBodyConstructionInfo)* HL_NAME(btRigidBodyConstructionInfo_new4)(float mass, _ref(btMotionState)* motionState, _ref(btCollisionShape)* collisionShape, _ref(btVector3)* localInertia) {
	if( !localInertia )
		return alloc_ref((new btRigidBody::btRigidBodyConstructionInfo(mass, _unref(motionState), _unref(collisionShape))),btRigidBodyConstructionInfo);
	else
		return alloc_ref((new btRigidBody::btRigidBodyConstructionInfo(mass, _unref(motionState), _unref(collisionShape), *_unref(localInertia))),btRigidBodyConstructionInfo);
}
DEFINE_PRIM(_IDL, btRigidBodyConstructionInfo_new4, _F32 _IDL _IDL _IDL);

HL_PRIM float HL_NAME(btRigidBodyConstructionInfo_get_m_linearDamping)( _ref(btRigidBody::btRigidBodyConstructionInfo)* _this ) {
	return _unref(_this)->m_linearDamping;
}
HL_PRIM float HL_NAME(btRigidBodyConstructionInfo_set_m_linearDamping)( _ref(btRigidBody::btRigidBodyConstructionInfo)* _this, float value ) {
	_unref(_this)->m_linearDamping = (value);
	return value;
}
DEFINE_PRIM(_F32,btRigidBodyConstructionInfo_get_m_linearDamping,_IDL);
DEFINE_PRIM(_F32,btRigidBodyConstructionInfo_set_m_linearDamping,_IDL _F32);

HL_PRIM float HL_NAME(btRigidBodyConstructionInfo_get_m_angularDamping)( _ref(btRigidBody::btRigidBodyConstructionInfo)* _this ) {
	return _unref(_this)->m_angularDamping;
}
HL_PRIM float HL_NAME(btRigidBodyConstructionInfo_set_m_angularDamping)( _ref(btRigidBody::btRigidBodyConstructionInfo)* _this, float value ) {
	_unref(_this)->m_angularDamping = (value);
	return value;
}
DEFINE_PRIM(_F32,btRigidBodyConstructionInfo_get_m_angularDamping,_IDL);
DEFINE_PRIM(_F32,btRigidBodyConstructionInfo_set_m_angularDamping,_IDL _F32);

HL_PRIM float HL_NAME(btRigidBodyConstructionInfo_get_m_friction)( _ref(btRigidBody::btRigidBodyConstructionInfo)* _this ) {
	return _unref(_this)->m_friction;
}
HL_PRIM float HL_NAME(btRigidBodyConstructionInfo_set_m_friction)( _ref(btRigidBody::btRigidBodyConstructionInfo)* _this, float value ) {
	_unref(_this)->m_friction = (value);
	return value;
}
DEFINE_PRIM(_F32,btRigidBodyConstructionInfo_get_m_friction,_IDL);
DEFINE_PRIM(_F32,btRigidBodyConstructionInfo_set_m_friction,_IDL _F32);

HL_PRIM float HL_NAME(btRigidBodyConstructionInfo_get_m_rollingFriction)( _ref(btRigidBody::btRigidBodyConstructionInfo)* _this ) {
	return _unref(_this)->m_rollingFriction;
}
HL_PRIM float HL_NAME(btRigidBodyConstructionInfo_set_m_rollingFriction)( _ref(btRigidBody::btRigidBodyConstructionInfo)* _this, float value ) {
	_unref(_this)->m_rollingFriction = (value);
	return value;
}
DEFINE_PRIM(_F32,btRigidBodyConstructionInfo_get_m_rollingFriction,_IDL);
DEFINE_PRIM(_F32,btRigidBodyConstructionInfo_set_m_rollingFriction,_IDL _F32);

HL_PRIM float HL_NAME(btRigidBodyConstructionInfo_get_m_restitution)( _ref(btRigidBody::btRigidBodyConstructionInfo)* _this ) {
	return _unref(_this)->m_restitution;
}
HL_PRIM float HL_NAME(btRigidBodyConstructionInfo_set_m_restitution)( _ref(btRigidBody::btRigidBodyConstructionInfo)* _this, float value ) {
	_unref(_this)->m_restitution = (value);
	return value;
}
DEFINE_PRIM(_F32,btRigidBodyConstructionInfo_get_m_restitution,_IDL);
DEFINE_PRIM(_F32,btRigidBodyConstructionInfo_set_m_restitution,_IDL _F32);

HL_PRIM float HL_NAME(btRigidBodyConstructionInfo_get_m_linearSleepingThreshold)( _ref(btRigidBody::btRigidBodyConstructionInfo)* _this ) {
	return _unref(_this)->m_linearSleepingThreshold;
}
HL_PRIM float HL_NAME(btRigidBodyConstructionInfo_set_m_linearSleepingThreshold)( _ref(btRigidBody::btRigidBodyConstructionInfo)* _this, float value ) {
	_unref(_this)->m_linearSleepingThreshold = (value);
	return value;
}
DEFINE_PRIM(_F32,btRigidBodyConstructionInfo_get_m_linearSleepingThreshold,_IDL);
DEFINE_PRIM(_F32,btRigidBodyConstructionInfo_set_m_linearSleepingThreshold,_IDL _F32);

HL_PRIM float HL_NAME(btRigidBodyConstructionInfo_get_m_angularSleepingThreshold)( _ref(btRigidBody::btRigidBodyConstructionInfo)* _this ) {
	return _unref(_this)->m_angularSleepingThreshold;
}
HL_PRIM float HL_NAME(btRigidBodyConstructionInfo_set_m_angularSleepingThreshold)( _ref(btRigidBody::btRigidBodyConstructionInfo)* _this, float value ) {
	_unref(_this)->m_angularSleepingThreshold = (value);
	return value;
}
DEFINE_PRIM(_F32,btRigidBodyConstructionInfo_get_m_angularSleepingThreshold,_IDL);
DEFINE_PRIM(_F32,btRigidBodyConstructionInfo_set_m_angularSleepingThreshold,_IDL _F32);

HL_PRIM bool HL_NAME(btRigidBodyConstructionInfo_get_m_additionalDamping)( _ref(btRigidBody::btRigidBodyConstructionInfo)* _this ) {
	return _unref(_this)->m_additionalDamping;
}
HL_PRIM bool HL_NAME(btRigidBodyConstructionInfo_set_m_additionalDamping)( _ref(btRigidBody::btRigidBodyConstructionInfo)* _this, bool value ) {
	_unref(_this)->m_additionalDamping = (value);
	return value;
}
DEFINE_PRIM(_BOOL,btRigidBodyConstructionInfo_get_m_additionalDamping,_IDL);
DEFINE_PRIM(_BOOL,btRigidBodyConstructionInfo_set_m_additionalDamping,_IDL _BOOL);

HL_PRIM float HL_NAME(btRigidBodyConstructionInfo_get_m_additionalDampingFactor)( _ref(btRigidBody::btRigidBodyConstructionInfo)* _this ) {
	return _unref(_this)->m_additionalDampingFactor;
}
HL_PRIM float HL_NAME(btRigidBodyConstructionInfo_set_m_additionalDampingFactor)( _ref(btRigidBody::btRigidBodyConstructionInfo)* _this, float value ) {
	_unref(_this)->m_additionalDampingFactor = (value);
	return value;
}
DEFINE_PRIM(_F32,btRigidBodyConstructionInfo_get_m_additionalDampingFactor,_IDL);
DEFINE_PRIM(_F32,btRigidBodyConstructionInfo_set_m_additionalDampingFactor,_IDL _F32);

HL_PRIM float HL_NAME(btRigidBodyConstructionInfo_get_m_additionalLinearDampingThresholdSqr)( _ref(btRigidBody::btRigidBodyConstructionInfo)* _this ) {
	return _unref(_this)->m_additionalLinearDampingThresholdSqr;
}
HL_PRIM float HL_NAME(btRigidBodyConstructionInfo_set_m_additionalLinearDampingThresholdSqr)( _ref(btRigidBody::btRigidBodyConstructionInfo)* _this, float value ) {
	_unref(_this)->m_additionalLinearDampingThresholdSqr = (value);
	return value;
}
DEFINE_PRIM(_F32,btRigidBodyConstructionInfo_get_m_additionalLinearDampingThresholdSqr,_IDL);
DEFINE_PRIM(_F32,btRigidBodyConstructionInfo_set_m_additionalLinearDampingThresholdSqr,_IDL _F32);

HL_PRIM float HL_NAME(btRigidBodyConstructionInfo_get_m_additionalAngularDampingThresholdSqr)( _ref(btRigidBody::btRigidBodyConstructionInfo)* _this ) {
	return _unref(_this)->m_additionalAngularDampingThresholdSqr;
}
HL_PRIM float HL_NAME(btRigidBodyConstructionInfo_set_m_additionalAngularDampingThresholdSqr)( _ref(btRigidBody::btRigidBodyConstructionInfo)* _this, float value ) {
	_unref(_this)->m_additionalAngularDampingThresholdSqr = (value);
	return value;
}
DEFINE_PRIM(_F32,btRigidBodyConstructionInfo_get_m_additionalAngularDampingThresholdSqr,_IDL);
DEFINE_PRIM(_F32,btRigidBodyConstructionInfo_set_m_additionalAngularDampingThresholdSqr,_IDL _F32);

HL_PRIM float HL_NAME(btRigidBodyConstructionInfo_get_m_additionalAngularDampingFactor)( _ref(btRigidBody::btRigidBodyConstructionInfo)* _this ) {
	return _unref(_this)->m_additionalAngularDampingFactor;
}
HL_PRIM float HL_NAME(btRigidBodyConstructionInfo_set_m_additionalAngularDampingFactor)( _ref(btRigidBody::btRigidBodyConstructionInfo)* _this, float value ) {
	_unref(_this)->m_additionalAngularDampingFactor = (value);
	return value;
}
DEFINE_PRIM(_F32,btRigidBodyConstructionInfo_get_m_additionalAngularDampingFactor,_IDL);
DEFINE_PRIM(_F32,btRigidBodyConstructionInfo_set_m_additionalAngularDampingFactor,_IDL _F32);

HL_PRIM _ref(btRigidBody)* HL_NAME(btRigidBody_new1)(_ref(btRigidBody::btRigidBodyConstructionInfo)* constructionInfo) {
	return alloc_ref((new btRigidBody(*_unref(constructionInfo))),btRigidBody);
}
DEFINE_PRIM(_IDL, btRigidBody_new1, _IDL);

HL_PRIM HL_CONST _ref(btTransform)* HL_NAME(btRigidBody_getCenterOfMassTransform0)(_ref(btRigidBody)* _this) {
	return alloc_ref(new btTransform(_unref(_this)->getCenterOfMassTransform()),btTransform);
}
DEFINE_PRIM(_IDL, btRigidBody_getCenterOfMassTransform0, _IDL);

HL_PRIM void HL_NAME(btRigidBody_setCenterOfMassTransform1)(_ref(btRigidBody)* _this, _ref(btTransform)* xform) {
	_unref(_this)->setCenterOfMassTransform(*_unref(xform));
}
DEFINE_PRIM(_VOID, btRigidBody_setCenterOfMassTransform1, _IDL _IDL);

HL_PRIM void HL_NAME(btRigidBody_setSleepingThresholds2)(_ref(btRigidBody)* _this, float linear, float angular) {
	_unref(_this)->setSleepingThresholds(linear, angular);
}
DEFINE_PRIM(_VOID, btRigidBody_setSleepingThresholds2, _IDL _F32 _F32);

HL_PRIM void HL_NAME(btRigidBody_setDamping2)(_ref(btRigidBody)* _this, float lin_damping, float ang_damping) {
	_unref(_this)->setDamping(lin_damping, ang_damping);
}
DEFINE_PRIM(_VOID, btRigidBody_setDamping2, _IDL _F32 _F32);

HL_PRIM void HL_NAME(btRigidBody_setMassProps2)(_ref(btRigidBody)* _this, float mass, _ref(btVector3)* inertia) {
	_unref(_this)->setMassProps(mass, *_unref(inertia));
}
DEFINE_PRIM(_VOID, btRigidBody_setMassProps2, _IDL _F32 _IDL);

HL_PRIM void HL_NAME(btRigidBody_setLinearFactor1)(_ref(btRigidBody)* _this, _ref(btVector3)* linearFactor) {
	_unref(_this)->setLinearFactor(*_unref(linearFactor));
}
DEFINE_PRIM(_VOID, btRigidBody_setLinearFactor1, _IDL _IDL);

HL_PRIM void HL_NAME(btRigidBody_applyTorque1)(_ref(btRigidBody)* _this, _ref(btVector3)* torque) {
	_unref(_this)->applyTorque(*_unref(torque));
}
DEFINE_PRIM(_VOID, btRigidBody_applyTorque1, _IDL _IDL);

HL_PRIM void HL_NAME(btRigidBody_applyForce2)(_ref(btRigidBody)* _this, _ref(btVector3)* force, _ref(btVector3)* rel_pos) {
	_unref(_this)->applyForce(*_unref(force), *_unref(rel_pos));
}
DEFINE_PRIM(_VOID, btRigidBody_applyForce2, _IDL _IDL _IDL);

HL_PRIM void HL_NAME(btRigidBody_applyCentralForce1)(_ref(btRigidBody)* _this, _ref(btVector3)* force) {
	_unref(_this)->applyCentralForce(*_unref(force));
}
DEFINE_PRIM(_VOID, btRigidBody_applyCentralForce1, _IDL _IDL);

HL_PRIM void HL_NAME(btRigidBody_applyTorqueImpulse1)(_ref(btRigidBody)* _this, _ref(btVector3)* torque) {
	_unref(_this)->applyTorqueImpulse(*_unref(torque));
}
DEFINE_PRIM(_VOID, btRigidBody_applyTorqueImpulse1, _IDL _IDL);

HL_PRIM void HL_NAME(btRigidBody_applyImpulse2)(_ref(btRigidBody)* _this, _ref(btVector3)* impulse, _ref(btVector3)* rel_pos) {
	_unref(_this)->applyImpulse(*_unref(impulse), *_unref(rel_pos));
}
DEFINE_PRIM(_VOID, btRigidBody_applyImpulse2, _IDL _IDL _IDL);

HL_PRIM void HL_NAME(btRigidBody_applyCentralImpulse1)(_ref(btRigidBody)* _this, _ref(btVector3)* impulse) {
	_unref(_this)->applyCentralImpulse(*_unref(impulse));
}
DEFINE_PRIM(_VOID, btRigidBody_applyCentralImpulse1, _IDL _IDL);

HL_PRIM void HL_NAME(btRigidBody_updateInertiaTensor0)(_ref(btRigidBody)* _this) {
	_unref(_this)->updateInertiaTensor();
}
DEFINE_PRIM(_VOID, btRigidBody_updateInertiaTensor0, _IDL);

HL_PRIM HL_CONST _ref(btVector3)* HL_NAME(btRigidBody_getLinearVelocity0)(_ref(btRigidBody)* _this) {
	return alloc_ref(new btVector3(_unref(_this)->getLinearVelocity()),btVector3);
}
DEFINE_PRIM(_IDL, btRigidBody_getLinearVelocity0, _IDL);

HL_PRIM HL_CONST _ref(btVector3)* HL_NAME(btRigidBody_getAngularVelocity0)(_ref(btRigidBody)* _this) {
	return alloc_ref(new btVector3(_unref(_this)->getAngularVelocity()),btVector3);
}
DEFINE_PRIM(_IDL, btRigidBody_getAngularVelocity0, _IDL);

HL_PRIM void HL_NAME(btRigidBody_setLinearVelocity1)(_ref(btRigidBody)* _this, _ref(btVector3)* lin_vel) {
	_unref(_this)->setLinearVelocity(*_unref(lin_vel));
}
DEFINE_PRIM(_VOID, btRigidBody_setLinearVelocity1, _IDL _IDL);

HL_PRIM void HL_NAME(btRigidBody_setAngularVelocity1)(_ref(btRigidBody)* _this, _ref(btVector3)* ang_vel) {
	_unref(_this)->setAngularVelocity(*_unref(ang_vel));
}
DEFINE_PRIM(_VOID, btRigidBody_setAngularVelocity1, _IDL _IDL);

HL_PRIM _ref(btMotionState)* HL_NAME(btRigidBody_getMotionState0)(_ref(btRigidBody)* _this) {
	return alloc_ref((_unref(_this)->getMotionState()),btMotionState);
}
DEFINE_PRIM(_IDL, btRigidBody_getMotionState0, _IDL);

HL_PRIM void HL_NAME(btRigidBody_setMotionState1)(_ref(btRigidBody)* _this, _ref(btMotionState)* motionState) {
	_unref(_this)->setMotionState(_unref(motionState));
}
DEFINE_PRIM(_VOID, btRigidBody_setMotionState1, _IDL _IDL);

HL_PRIM void HL_NAME(btRigidBody_setAngularFactor1)(_ref(btRigidBody)* _this, _ref(btVector3)* angularFactor) {
	_unref(_this)->setAngularFactor(*_unref(angularFactor));
}
DEFINE_PRIM(_VOID, btRigidBody_setAngularFactor1, _IDL _IDL);

HL_PRIM _ref(btRigidBody)* HL_NAME(btRigidBody_upcast1)(_ref(btRigidBody)* _this, _ref(btCollisionObject)* colObj) {
	return alloc_ref((_unref(_this)->upcast(_unref(colObj))),btRigidBody);
}
DEFINE_PRIM(_IDL, btRigidBody_upcast1, _IDL _IDL);

HL_PRIM void HL_NAME(btRigidBody_getAabb2)(_ref(btRigidBody)* _this, _ref(btVector3)* aabbMin, _ref(btVector3)* aabbMax) {
	_unref(_this)->getAabb(*_unref(aabbMin), *_unref(aabbMax));
}
DEFINE_PRIM(_VOID, btRigidBody_getAabb2, _IDL _IDL _IDL);

HL_PRIM HL_CONST _ref(btVector3)* HL_NAME(btRigidBody_getGravity0)(_ref(btRigidBody)* _this) {
	return alloc_ref(new btVector3(_unref(_this)->getGravity()),btVector3);
}
DEFINE_PRIM(_IDL, btRigidBody_getGravity0, _IDL);

HL_PRIM void HL_NAME(btRigidBody_setGravity1)(_ref(btRigidBody)* _this, _ref(btVector3)* acceleration) {
	_unref(_this)->setGravity(*_unref(acceleration));
}
DEFINE_PRIM(_VOID, btRigidBody_setGravity1, _IDL _IDL);

HL_PRIM _ref(btConstraintSetting)* HL_NAME(btConstraintSetting_new0)() {
	return alloc_ref((new btConstraintSetting()),btConstraintSetting);
}
DEFINE_PRIM(_IDL, btConstraintSetting_new0,);

HL_PRIM float HL_NAME(btConstraintSetting_get_m_tau)( _ref(btConstraintSetting)* _this ) {
	return _unref(_this)->m_tau;
}
HL_PRIM float HL_NAME(btConstraintSetting_set_m_tau)( _ref(btConstraintSetting)* _this, float value ) {
	_unref(_this)->m_tau = (value);
	return value;
}
DEFINE_PRIM(_F32,btConstraintSetting_get_m_tau,_IDL);
DEFINE_PRIM(_F32,btConstraintSetting_set_m_tau,_IDL _F32);

HL_PRIM float HL_NAME(btConstraintSetting_get_m_damping)( _ref(btConstraintSetting)* _this ) {
	return _unref(_this)->m_damping;
}
HL_PRIM float HL_NAME(btConstraintSetting_set_m_damping)( _ref(btConstraintSetting)* _this, float value ) {
	_unref(_this)->m_damping = (value);
	return value;
}
DEFINE_PRIM(_F32,btConstraintSetting_get_m_damping,_IDL);
DEFINE_PRIM(_F32,btConstraintSetting_set_m_damping,_IDL _F32);

HL_PRIM float HL_NAME(btConstraintSetting_get_m_impulseClamp)( _ref(btConstraintSetting)* _this ) {
	return _unref(_this)->m_impulseClamp;
}
HL_PRIM float HL_NAME(btConstraintSetting_set_m_impulseClamp)( _ref(btConstraintSetting)* _this, float value ) {
	_unref(_this)->m_impulseClamp = (value);
	return value;
}
DEFINE_PRIM(_F32,btConstraintSetting_get_m_impulseClamp,_IDL);
DEFINE_PRIM(_F32,btConstraintSetting_set_m_impulseClamp,_IDL _F32);

HL_PRIM void HL_NAME(btTypedConstraint_enableFeedback1)(_ref(btTypedConstraint)* _this, bool needsFeedback) {
	_unref(_this)->enableFeedback(needsFeedback);
}
DEFINE_PRIM(_VOID, btTypedConstraint_enableFeedback1, _IDL _BOOL);

HL_PRIM HL_CONST float HL_NAME(btTypedConstraint_getBreakingImpulseThreshold0)(_ref(btTypedConstraint)* _this) {
	return _unref(_this)->getBreakingImpulseThreshold();
}
DEFINE_PRIM(_F32, btTypedConstraint_getBreakingImpulseThreshold0, _IDL);

HL_PRIM void HL_NAME(btTypedConstraint_setBreakingImpulseThreshold1)(_ref(btTypedConstraint)* _this, float threshold) {
	_unref(_this)->setBreakingImpulseThreshold(threshold);
}
DEFINE_PRIM(_VOID, btTypedConstraint_setBreakingImpulseThreshold1, _IDL _F32);

HL_PRIM HL_CONST float HL_NAME(btTypedConstraint_getParam2)(_ref(btTypedConstraint)* _this, int num, int axis) {
	return _unref(_this)->getParam(num, axis);
}
DEFINE_PRIM(_F32, btTypedConstraint_getParam2, _IDL _I32 _I32);

HL_PRIM void HL_NAME(btTypedConstraint_setParam3)(_ref(btTypedConstraint)* _this, int num, float value, int axis) {
	_unref(_this)->setParam(num, value, axis);
}
DEFINE_PRIM(_VOID, btTypedConstraint_setParam3, _IDL _I32 _F32 _I32);

HL_PRIM _ref(btPoint2PointConstraint)* HL_NAME(btPoint2PointConstraint_new4)(_ref(btRigidBody)* rbA, _ref(btRigidBody)* rbB, _ref(btVector3)* pivotInA, _ref(btVector3)* pivotInB) {
	return alloc_ref((new btPoint2PointConstraint(*_unref(rbA), *_unref(rbB), *_unref(pivotInA), *_unref(pivotInB))),btPoint2PointConstraint);
}
DEFINE_PRIM(_IDL, btPoint2PointConstraint_new4, _IDL _IDL _IDL _IDL);

HL_PRIM _ref(btPoint2PointConstraint)* HL_NAME(btPoint2PointConstraint_new2)(_ref(btRigidBody)* rbA, _ref(btVector3)* pivotInA) {
	return alloc_ref((new btPoint2PointConstraint(*_unref(rbA), *_unref(pivotInA))),btPoint2PointConstraint);
}
DEFINE_PRIM(_IDL, btPoint2PointConstraint_new2, _IDL _IDL);

HL_PRIM void HL_NAME(btPoint2PointConstraint_setPivotA1)(_ref(btPoint2PointConstraint)* _this, _ref(btVector3)* pivotA) {
	_unref(_this)->setPivotA(*_unref(pivotA));
}
DEFINE_PRIM(_VOID, btPoint2PointConstraint_setPivotA1, _IDL _IDL);

HL_PRIM void HL_NAME(btPoint2PointConstraint_setPivotB1)(_ref(btPoint2PointConstraint)* _this, _ref(btVector3)* pivotB) {
	_unref(_this)->setPivotB(*_unref(pivotB));
}
DEFINE_PRIM(_VOID, btPoint2PointConstraint_setPivotB1, _IDL _IDL);

HL_PRIM HL_CONST _ref(btVector3)* HL_NAME(btPoint2PointConstraint_getPivotInA0)(_ref(btPoint2PointConstraint)* _this) {
	return alloc_ref(new btVector3(_unref(_this)->getPivotInA()),btVector3);
}
DEFINE_PRIM(_IDL, btPoint2PointConstraint_getPivotInA0, _IDL);

HL_PRIM HL_CONST _ref(btVector3)* HL_NAME(btPoint2PointConstraint_getPivotInB0)(_ref(btPoint2PointConstraint)* _this) {
	return alloc_ref(new btVector3(_unref(_this)->getPivotInB()),btVector3);
}
DEFINE_PRIM(_IDL, btPoint2PointConstraint_getPivotInB0, _IDL);

HL_PRIM _ref(btConstraintSetting)* HL_NAME(btPoint2PointConstraint_get_m_setting)( _ref(btPoint2PointConstraint)* _this ) {
	return alloc_ref(new btConstraintSetting(_unref(_this)->m_setting),btConstraintSetting);
}
HL_PRIM _ref(btConstraintSetting)* HL_NAME(btPoint2PointConstraint_set_m_setting)( _ref(btPoint2PointConstraint)* _this, _ref(btConstraintSetting)* value ) {
	_unref(_this)->m_setting = *_unref(value);
	return value;
}
DEFINE_PRIM(_IDL,btPoint2PointConstraint_get_m_setting,_IDL);
DEFINE_PRIM(_IDL,btPoint2PointConstraint_set_m_setting,_IDL _IDL);

HL_PRIM _ref(btGeneric6DofConstraint)* HL_NAME(btGeneric6DofConstraint_new5)(_ref(btRigidBody)* rbA, _ref(btRigidBody)* rbB, _ref(btTransform)* frameInA, _ref(btTransform)* frameInB, bool useLinearFrameReferenceFrameA) {
	return alloc_ref((new btGeneric6DofConstraint(*_unref(rbA), *_unref(rbB), *_unref(frameInA), *_unref(frameInB), useLinearFrameReferenceFrameA)),btGeneric6DofConstraint);
}
DEFINE_PRIM(_IDL, btGeneric6DofConstraint_new5, _IDL _IDL _IDL _IDL _BOOL);

HL_PRIM _ref(btGeneric6DofConstraint)* HL_NAME(btGeneric6DofConstraint_new3)(_ref(btRigidBody)* rbB, _ref(btTransform)* frameInB, bool useLinearFrameReferenceFrameB) {
	return alloc_ref((new btGeneric6DofConstraint(*_unref(rbB), *_unref(frameInB), useLinearFrameReferenceFrameB)),btGeneric6DofConstraint);
}
DEFINE_PRIM(_IDL, btGeneric6DofConstraint_new3, _IDL _IDL _BOOL);

HL_PRIM void HL_NAME(btGeneric6DofConstraint_setLinearLowerLimit1)(_ref(btGeneric6DofConstraint)* _this, _ref(btVector3)* linearLower) {
	_unref(_this)->setLinearLowerLimit(*_unref(linearLower));
}
DEFINE_PRIM(_VOID, btGeneric6DofConstraint_setLinearLowerLimit1, _IDL _IDL);

HL_PRIM void HL_NAME(btGeneric6DofConstraint_setLinearUpperLimit1)(_ref(btGeneric6DofConstraint)* _this, _ref(btVector3)* linearUpper) {
	_unref(_this)->setLinearUpperLimit(*_unref(linearUpper));
}
DEFINE_PRIM(_VOID, btGeneric6DofConstraint_setLinearUpperLimit1, _IDL _IDL);

HL_PRIM void HL_NAME(btGeneric6DofConstraint_setAngularLowerLimit1)(_ref(btGeneric6DofConstraint)* _this, _ref(btVector3)* angularLower) {
	_unref(_this)->setAngularLowerLimit(*_unref(angularLower));
}
DEFINE_PRIM(_VOID, btGeneric6DofConstraint_setAngularLowerLimit1, _IDL _IDL);

HL_PRIM void HL_NAME(btGeneric6DofConstraint_setAngularUpperLimit1)(_ref(btGeneric6DofConstraint)* _this, _ref(btVector3)* angularUpper) {
	_unref(_this)->setAngularUpperLimit(*_unref(angularUpper));
}
DEFINE_PRIM(_VOID, btGeneric6DofConstraint_setAngularUpperLimit1, _IDL _IDL);

HL_PRIM _ref(btTransform)* HL_NAME(btGeneric6DofConstraint_getFrameOffsetA0)(_ref(btGeneric6DofConstraint)* _this) {
	return &_this->getFrameOffsetA();
}
DEFINE_PRIM(_IDL, btGeneric6DofConstraint_getFrameOffsetA0, _IDL);

HL_PRIM _ref(btGeneric6DofSpringConstraint)* HL_NAME(btGeneric6DofSpringConstraint_new5)(_ref(btRigidBody)* rbA, _ref(btRigidBody)* rbB, _ref(btTransform)* frameInA, _ref(btTransform)* frameInB, bool useLinearFrameReferenceFrameA) {
	return alloc_ref((new btGeneric6DofSpringConstraint(*_unref(rbA), *_unref(rbB), *_unref(frameInA), *_unref(frameInB), useLinearFrameReferenceFrameA)),btGeneric6DofSpringConstraint);
}
DEFINE_PRIM(_IDL, btGeneric6DofSpringConstraint_new5, _IDL _IDL _IDL _IDL _BOOL);

HL_PRIM _ref(btGeneric6DofSpringConstraint)* HL_NAME(btGeneric6DofSpringConstraint_new3)(_ref(btRigidBody)* rbB, _ref(btTransform)* frameInB, bool useLinearFrameReferenceFrameB) {
	return alloc_ref((new btGeneric6DofSpringConstraint(*_unref(rbB), *_unref(frameInB), useLinearFrameReferenceFrameB)),btGeneric6DofSpringConstraint);
}
DEFINE_PRIM(_IDL, btGeneric6DofSpringConstraint_new3, _IDL _IDL _BOOL);

HL_PRIM void HL_NAME(btGeneric6DofSpringConstraint_enableSpring2)(_ref(btGeneric6DofSpringConstraint)* _this, int index, bool onOff) {
	_unref(_this)->enableSpring(index, onOff);
}
DEFINE_PRIM(_VOID, btGeneric6DofSpringConstraint_enableSpring2, _IDL _I32 _BOOL);

HL_PRIM void HL_NAME(btGeneric6DofSpringConstraint_setStiffness2)(_ref(btGeneric6DofSpringConstraint)* _this, int index, float stiffness) {
	_unref(_this)->setStiffness(index, stiffness);
}
DEFINE_PRIM(_VOID, btGeneric6DofSpringConstraint_setStiffness2, _IDL _I32 _F32);

HL_PRIM void HL_NAME(btGeneric6DofSpringConstraint_setDamping2)(_ref(btGeneric6DofSpringConstraint)* _this, int index, float damping) {
	_unref(_this)->setDamping(index, damping);
}
DEFINE_PRIM(_VOID, btGeneric6DofSpringConstraint_setDamping2, _IDL _I32 _F32);

HL_PRIM _ref(btSequentialImpulseConstraintSolver)* HL_NAME(btSequentialImpulseConstraintSolver_new0)() {
	return alloc_ref((new btSequentialImpulseConstraintSolver()),btSequentialImpulseConstraintSolver);
}
DEFINE_PRIM(_IDL, btSequentialImpulseConstraintSolver_new0,);

HL_PRIM _ref(btConeTwistConstraint)* HL_NAME(btConeTwistConstraint_new4)(_ref(btRigidBody)* rbA, _ref(btRigidBody)* rbB, _ref(btTransform)* rbAFrame, _ref(btTransform)* rbBFrame) {
	return alloc_ref((new btConeTwistConstraint(*_unref(rbA), *_unref(rbB), *_unref(rbAFrame), *_unref(rbBFrame))),btConeTwistConstraint);
}
DEFINE_PRIM(_IDL, btConeTwistConstraint_new4, _IDL _IDL _IDL _IDL);

HL_PRIM _ref(btConeTwistConstraint)* HL_NAME(btConeTwistConstraint_new2)(_ref(btRigidBody)* rbA, _ref(btTransform)* rbAFrame) {
	return alloc_ref((new btConeTwistConstraint(*_unref(rbA), *_unref(rbAFrame))),btConeTwistConstraint);
}
DEFINE_PRIM(_IDL, btConeTwistConstraint_new2, _IDL _IDL);

HL_PRIM void HL_NAME(btConeTwistConstraint_setLimit2)(_ref(btConeTwistConstraint)* _this, int limitIndex, float limitValue) {
	_unref(_this)->setLimit(limitIndex, limitValue);
}
DEFINE_PRIM(_VOID, btConeTwistConstraint_setLimit2, _IDL _I32 _F32);

HL_PRIM void HL_NAME(btConeTwistConstraint_setAngularOnly1)(_ref(btConeTwistConstraint)* _this, bool angularOnly) {
	_unref(_this)->setAngularOnly(angularOnly);
}
DEFINE_PRIM(_VOID, btConeTwistConstraint_setAngularOnly1, _IDL _BOOL);

HL_PRIM void HL_NAME(btConeTwistConstraint_setDamping1)(_ref(btConeTwistConstraint)* _this, float damping) {
	_unref(_this)->setDamping(damping);
}
DEFINE_PRIM(_VOID, btConeTwistConstraint_setDamping1, _IDL _F32);

HL_PRIM void HL_NAME(btConeTwistConstraint_enableMotor1)(_ref(btConeTwistConstraint)* _this, bool b) {
	_unref(_this)->enableMotor(b);
}
DEFINE_PRIM(_VOID, btConeTwistConstraint_enableMotor1, _IDL _BOOL);

HL_PRIM void HL_NAME(btConeTwistConstraint_setMaxMotorImpulse1)(_ref(btConeTwistConstraint)* _this, float maxMotorImpulse) {
	_unref(_this)->setMaxMotorImpulse(maxMotorImpulse);
}
DEFINE_PRIM(_VOID, btConeTwistConstraint_setMaxMotorImpulse1, _IDL _F32);

HL_PRIM void HL_NAME(btConeTwistConstraint_setMaxMotorImpulseNormalized1)(_ref(btConeTwistConstraint)* _this, float maxMotorImpulse) {
	_unref(_this)->setMaxMotorImpulseNormalized(maxMotorImpulse);
}
DEFINE_PRIM(_VOID, btConeTwistConstraint_setMaxMotorImpulseNormalized1, _IDL _F32);

HL_PRIM void HL_NAME(btConeTwistConstraint_setMotorTarget1)(_ref(btConeTwistConstraint)* _this, _ref(btQuaternion)* q) {
	_unref(_this)->setMotorTarget(*_unref(q));
}
DEFINE_PRIM(_VOID, btConeTwistConstraint_setMotorTarget1, _IDL _IDL);

HL_PRIM void HL_NAME(btConeTwistConstraint_setMotorTargetInConstraintSpace1)(_ref(btConeTwistConstraint)* _this, _ref(btQuaternion)* q) {
	_unref(_this)->setMotorTargetInConstraintSpace(*_unref(q));
}
DEFINE_PRIM(_VOID, btConeTwistConstraint_setMotorTargetInConstraintSpace1, _IDL _IDL);

HL_PRIM _ref(btHingeConstraint)* HL_NAME(btHingeConstraint_new7)(_ref(btRigidBody)* rbA, _ref(btRigidBody)* rbB, _ref(btVector3)* pivotInA, _ref(btVector3)* pivotInB, _ref(btVector3)* axisInA, _ref(btVector3)* axisInB, _OPT(bool) useReferenceFrameA) {
	if( !useReferenceFrameA )
		return alloc_ref((new btHingeConstraint(*_unref(rbA), *_unref(rbB), *_unref(pivotInA), *_unref(pivotInB), *_unref(axisInA), *_unref(axisInB))),btHingeConstraint);
	else
		return alloc_ref((new btHingeConstraint(*_unref(rbA), *_unref(rbB), *_unref(pivotInA), *_unref(pivotInB), *_unref(axisInA), *_unref(axisInB), _GET_OPT(useReferenceFrameA,b))),btHingeConstraint);
}
DEFINE_PRIM(_IDL, btHingeConstraint_new7, _IDL _IDL _IDL _IDL _IDL _IDL _NULL(_BOOL));

HL_PRIM _ref(btHingeConstraint)* HL_NAME(btHingeConstraint_new4)(_ref(btRigidBody)* rbA, _ref(btVector3)* pivotInA, _ref(btVector3)* axisInA, _OPT(bool) useReferenceFrameA) {
	if( !useReferenceFrameA )
		return alloc_ref((new btHingeConstraint(*_unref(rbA), *_unref(pivotInA), *_unref(axisInA))),btHingeConstraint);
	else
		return alloc_ref((new btHingeConstraint(*_unref(rbA), *_unref(pivotInA), *_unref(axisInA), _GET_OPT(useReferenceFrameA,b))),btHingeConstraint);
}
DEFINE_PRIM(_IDL, btHingeConstraint_new4, _IDL _IDL _IDL _NULL(_BOOL));

HL_PRIM _ref(btHingeConstraint)* HL_NAME(btHingeConstraint_new5)(_ref(btRigidBody)* rbA, _ref(btRigidBody)* rbB, _ref(btTransform)* rbAFrame, _ref(btTransform)* rbBFrame, _OPT(bool) useReferenceFrameA) {
	if( !useReferenceFrameA )
		return alloc_ref((new btHingeConstraint(*_unref(rbA), *_unref(rbB), *_unref(rbAFrame), *_unref(rbBFrame))),btHingeConstraint);
	else
		return alloc_ref((new btHingeConstraint(*_unref(rbA), *_unref(rbB), *_unref(rbAFrame), *_unref(rbBFrame), _GET_OPT(useReferenceFrameA,b))),btHingeConstraint);
}
DEFINE_PRIM(_IDL, btHingeConstraint_new5, _IDL _IDL _IDL _IDL _NULL(_BOOL));

HL_PRIM _ref(btHingeConstraint)* HL_NAME(btHingeConstraint_new3)(_ref(btRigidBody)* rbA, _ref(btTransform)* rbAFrame, _OPT(bool) useReferenceFrameA) {
	if( !useReferenceFrameA )
		return alloc_ref((new btHingeConstraint(*_unref(rbA), *_unref(rbAFrame))),btHingeConstraint);
	else
		return alloc_ref((new btHingeConstraint(*_unref(rbA), *_unref(rbAFrame), _GET_OPT(useReferenceFrameA,b))),btHingeConstraint);
}
DEFINE_PRIM(_IDL, btHingeConstraint_new3, _IDL _IDL _NULL(_BOOL));

HL_PRIM void HL_NAME(btHingeConstraint_setLimit5)(_ref(btHingeConstraint)* _this, float low, float high, float softness, float biasFactor, _OPT(float) relaxationFactor) {
	if( !relaxationFactor )
		_unref(_this)->setLimit(low, high, softness, biasFactor);
	else
		_unref(_this)->setLimit(low, high, softness, biasFactor, _GET_OPT(relaxationFactor,f));
}
DEFINE_PRIM(_VOID, btHingeConstraint_setLimit5, _IDL _F32 _F32 _F32 _F32 _NULL(_F32));

HL_PRIM void HL_NAME(btHingeConstraint_enableAngularMotor3)(_ref(btHingeConstraint)* _this, bool enableMotor, float targetVelocity, float maxMotorImpulse) {
	_unref(_this)->enableAngularMotor(enableMotor, targetVelocity, maxMotorImpulse);
}
DEFINE_PRIM(_VOID, btHingeConstraint_enableAngularMotor3, _IDL _BOOL _F32 _F32);

HL_PRIM void HL_NAME(btHingeConstraint_setAngularOnly1)(_ref(btHingeConstraint)* _this, bool angularOnly) {
	_unref(_this)->setAngularOnly(angularOnly);
}
DEFINE_PRIM(_VOID, btHingeConstraint_setAngularOnly1, _IDL _BOOL);

HL_PRIM void HL_NAME(btHingeConstraint_enableMotor1)(_ref(btHingeConstraint)* _this, bool enableMotor) {
	_unref(_this)->enableMotor(enableMotor);
}
DEFINE_PRIM(_VOID, btHingeConstraint_enableMotor1, _IDL _BOOL);

HL_PRIM void HL_NAME(btHingeConstraint_setMaxMotorImpulse1)(_ref(btHingeConstraint)* _this, float maxMotorImpulse) {
	_unref(_this)->setMaxMotorImpulse(maxMotorImpulse);
}
DEFINE_PRIM(_VOID, btHingeConstraint_setMaxMotorImpulse1, _IDL _F32);

HL_PRIM void HL_NAME(btHingeConstraint_setMotorTarget2)(_ref(btHingeConstraint)* _this, _ref(btQuaternion)* qAinB, float dt) {
	_unref(_this)->setMotorTarget(*_unref(qAinB), dt);
}
DEFINE_PRIM(_VOID, btHingeConstraint_setMotorTarget2, _IDL _IDL _F32);

HL_PRIM _ref(btSliderConstraint)* HL_NAME(btSliderConstraint_new5)(_ref(btRigidBody)* rbA, _ref(btRigidBody)* rbB, _ref(btTransform)* frameInA, _ref(btTransform)* frameInB, bool useLinearReferenceFrameA) {
	return alloc_ref((new btSliderConstraint(*_unref(rbA), *_unref(rbB), *_unref(frameInA), *_unref(frameInB), useLinearReferenceFrameA)),btSliderConstraint);
}
DEFINE_PRIM(_IDL, btSliderConstraint_new5, _IDL _IDL _IDL _IDL _BOOL);

HL_PRIM _ref(btSliderConstraint)* HL_NAME(btSliderConstraint_new3)(_ref(btRigidBody)* rbB, _ref(btTransform)* frameInB, bool useLinearReferenceFrameA) {
	return alloc_ref((new btSliderConstraint(*_unref(rbB), *_unref(frameInB), useLinearReferenceFrameA)),btSliderConstraint);
}
DEFINE_PRIM(_IDL, btSliderConstraint_new3, _IDL _IDL _BOOL);

HL_PRIM void HL_NAME(btSliderConstraint_setLowerLinLimit1)(_ref(btSliderConstraint)* _this, float lowerLimit) {
	_unref(_this)->setLowerLinLimit(lowerLimit);
}
DEFINE_PRIM(_VOID, btSliderConstraint_setLowerLinLimit1, _IDL _F32);

HL_PRIM void HL_NAME(btSliderConstraint_setUpperLinLimit1)(_ref(btSliderConstraint)* _this, float upperLimit) {
	_unref(_this)->setUpperLinLimit(upperLimit);
}
DEFINE_PRIM(_VOID, btSliderConstraint_setUpperLinLimit1, _IDL _F32);

HL_PRIM void HL_NAME(btSliderConstraint_setLowerAngLimit1)(_ref(btSliderConstraint)* _this, float lowerAngLimit) {
	_unref(_this)->setLowerAngLimit(lowerAngLimit);
}
DEFINE_PRIM(_VOID, btSliderConstraint_setLowerAngLimit1, _IDL _F32);

HL_PRIM void HL_NAME(btSliderConstraint_setUpperAngLimit1)(_ref(btSliderConstraint)* _this, float upperAngLimit) {
	_unref(_this)->setUpperAngLimit(upperAngLimit);
}
DEFINE_PRIM(_VOID, btSliderConstraint_setUpperAngLimit1, _IDL _F32);

HL_PRIM _ref(btFixedConstraint)* HL_NAME(btFixedConstraint_new4)(_ref(btRigidBody)* rbA, _ref(btRigidBody)* rbB, _ref(btTransform)* frameInA, _ref(btTransform)* frameInB) {
	return alloc_ref((new btFixedConstraint(*_unref(rbA), *_unref(rbB), *_unref(frameInA), *_unref(frameInB))),btFixedConstraint);
}
DEFINE_PRIM(_IDL, btFixedConstraint_new4, _IDL _IDL _IDL _IDL);

HL_PRIM float HL_NAME(btDispatcherInfo_get_m_timeStep)( _ref(btDispatcherInfo)* _this ) {
	return _unref(_this)->m_timeStep;
}
HL_PRIM float HL_NAME(btDispatcherInfo_set_m_timeStep)( _ref(btDispatcherInfo)* _this, float value ) {
	_unref(_this)->m_timeStep = (value);
	return value;
}
DEFINE_PRIM(_F32,btDispatcherInfo_get_m_timeStep,_IDL);
DEFINE_PRIM(_F32,btDispatcherInfo_set_m_timeStep,_IDL _F32);

HL_PRIM int HL_NAME(btDispatcherInfo_get_m_stepCount)( _ref(btDispatcherInfo)* _this ) {
	return _unref(_this)->m_stepCount;
}
HL_PRIM int HL_NAME(btDispatcherInfo_set_m_stepCount)( _ref(btDispatcherInfo)* _this, int value ) {
	_unref(_this)->m_stepCount = (value);
	return value;
}
DEFINE_PRIM(_I32,btDispatcherInfo_get_m_stepCount,_IDL);
DEFINE_PRIM(_I32,btDispatcherInfo_set_m_stepCount,_IDL _I32);

HL_PRIM int HL_NAME(btDispatcherInfo_get_m_dispatchFunc)( _ref(btDispatcherInfo)* _this ) {
	return _unref(_this)->m_dispatchFunc;
}
HL_PRIM int HL_NAME(btDispatcherInfo_set_m_dispatchFunc)( _ref(btDispatcherInfo)* _this, int value ) {
	_unref(_this)->m_dispatchFunc = (value);
	return value;
}
DEFINE_PRIM(_I32,btDispatcherInfo_get_m_dispatchFunc,_IDL);
DEFINE_PRIM(_I32,btDispatcherInfo_set_m_dispatchFunc,_IDL _I32);

HL_PRIM float HL_NAME(btDispatcherInfo_get_m_timeOfImpact)( _ref(btDispatcherInfo)* _this ) {
	return _unref(_this)->m_timeOfImpact;
}
HL_PRIM float HL_NAME(btDispatcherInfo_set_m_timeOfImpact)( _ref(btDispatcherInfo)* _this, float value ) {
	_unref(_this)->m_timeOfImpact = (value);
	return value;
}
DEFINE_PRIM(_F32,btDispatcherInfo_get_m_timeOfImpact,_IDL);
DEFINE_PRIM(_F32,btDispatcherInfo_set_m_timeOfImpact,_IDL _F32);

HL_PRIM bool HL_NAME(btDispatcherInfo_get_m_useContinuous)( _ref(btDispatcherInfo)* _this ) {
	return _unref(_this)->m_useContinuous;
}
HL_PRIM bool HL_NAME(btDispatcherInfo_set_m_useContinuous)( _ref(btDispatcherInfo)* _this, bool value ) {
	_unref(_this)->m_useContinuous = (value);
	return value;
}
DEFINE_PRIM(_BOOL,btDispatcherInfo_get_m_useContinuous,_IDL);
DEFINE_PRIM(_BOOL,btDispatcherInfo_set_m_useContinuous,_IDL _BOOL);

HL_PRIM bool HL_NAME(btDispatcherInfo_get_m_enableSatConvex)( _ref(btDispatcherInfo)* _this ) {
	return _unref(_this)->m_enableSatConvex;
}
HL_PRIM bool HL_NAME(btDispatcherInfo_set_m_enableSatConvex)( _ref(btDispatcherInfo)* _this, bool value ) {
	_unref(_this)->m_enableSatConvex = (value);
	return value;
}
DEFINE_PRIM(_BOOL,btDispatcherInfo_get_m_enableSatConvex,_IDL);
DEFINE_PRIM(_BOOL,btDispatcherInfo_set_m_enableSatConvex,_IDL _BOOL);

HL_PRIM bool HL_NAME(btDispatcherInfo_get_m_enableSPU)( _ref(btDispatcherInfo)* _this ) {
	return _unref(_this)->m_enableSPU;
}
HL_PRIM bool HL_NAME(btDispatcherInfo_set_m_enableSPU)( _ref(btDispatcherInfo)* _this, bool value ) {
	_unref(_this)->m_enableSPU = (value);
	return value;
}
DEFINE_PRIM(_BOOL,btDispatcherInfo_get_m_enableSPU,_IDL);
DEFINE_PRIM(_BOOL,btDispatcherInfo_set_m_enableSPU,_IDL _BOOL);

HL_PRIM bool HL_NAME(btDispatcherInfo_get_m_useEpa)( _ref(btDispatcherInfo)* _this ) {
	return _unref(_this)->m_useEpa;
}
HL_PRIM bool HL_NAME(btDispatcherInfo_set_m_useEpa)( _ref(btDispatcherInfo)* _this, bool value ) {
	_unref(_this)->m_useEpa = (value);
	return value;
}
DEFINE_PRIM(_BOOL,btDispatcherInfo_get_m_useEpa,_IDL);
DEFINE_PRIM(_BOOL,btDispatcherInfo_set_m_useEpa,_IDL _BOOL);

HL_PRIM float HL_NAME(btDispatcherInfo_get_m_allowedCcdPenetration)( _ref(btDispatcherInfo)* _this ) {
	return _unref(_this)->m_allowedCcdPenetration;
}
HL_PRIM float HL_NAME(btDispatcherInfo_set_m_allowedCcdPenetration)( _ref(btDispatcherInfo)* _this, float value ) {
	_unref(_this)->m_allowedCcdPenetration = (value);
	return value;
}
DEFINE_PRIM(_F32,btDispatcherInfo_get_m_allowedCcdPenetration,_IDL);
DEFINE_PRIM(_F32,btDispatcherInfo_set_m_allowedCcdPenetration,_IDL _F32);

HL_PRIM bool HL_NAME(btDispatcherInfo_get_m_useConvexConservativeDistanceUtil)( _ref(btDispatcherInfo)* _this ) {
	return _unref(_this)->m_useConvexConservativeDistanceUtil;
}
HL_PRIM bool HL_NAME(btDispatcherInfo_set_m_useConvexConservativeDistanceUtil)( _ref(btDispatcherInfo)* _this, bool value ) {
	_unref(_this)->m_useConvexConservativeDistanceUtil = (value);
	return value;
}
DEFINE_PRIM(_BOOL,btDispatcherInfo_get_m_useConvexConservativeDistanceUtil,_IDL);
DEFINE_PRIM(_BOOL,btDispatcherInfo_set_m_useConvexConservativeDistanceUtil,_IDL _BOOL);

HL_PRIM float HL_NAME(btDispatcherInfo_get_m_convexConservativeDistanceThreshold)( _ref(btDispatcherInfo)* _this ) {
	return _unref(_this)->m_convexConservativeDistanceThreshold;
}
HL_PRIM float HL_NAME(btDispatcherInfo_set_m_convexConservativeDistanceThreshold)( _ref(btDispatcherInfo)* _this, float value ) {
	_unref(_this)->m_convexConservativeDistanceThreshold = (value);
	return value;
}
DEFINE_PRIM(_F32,btDispatcherInfo_get_m_convexConservativeDistanceThreshold,_IDL);
DEFINE_PRIM(_F32,btDispatcherInfo_set_m_convexConservativeDistanceThreshold,_IDL _F32);

HL_PRIM _ref(btDispatcher)* HL_NAME(btCollisionWorld_getDispatcher0)(_ref(btCollisionWorld)* _this) {
	return alloc_ref((_unref(_this)->getDispatcher()),btDispatcher);
}
DEFINE_PRIM(_IDL, btCollisionWorld_getDispatcher0, _IDL);

HL_PRIM void HL_NAME(btCollisionWorld_rayTest3)(_ref(btCollisionWorld)* _this, _ref(btVector3)* rayFromWorld, _ref(btVector3)* rayToWorld, _ref(btCollisionWorld::RayResultCallback)* resultCallback) {
	_unref(_this)->rayTest(*_unref(rayFromWorld), *_unref(rayToWorld), *_unref(resultCallback));
}
DEFINE_PRIM(_VOID, btCollisionWorld_rayTest3, _IDL _IDL _IDL _IDL);

HL_PRIM _ref(btOverlappingPairCache)* HL_NAME(btCollisionWorld_getPairCache0)(_ref(btCollisionWorld)* _this) {
	return alloc_ref((_unref(_this)->getPairCache()),btOverlappingPairCache);
}
DEFINE_PRIM(_IDL, btCollisionWorld_getPairCache0, _IDL);

HL_PRIM _ref(btDispatcherInfo)* HL_NAME(btCollisionWorld_getDispatchInfo0)(_ref(btCollisionWorld)* _this) {
	return alloc_ref(new btDispatcherInfo(_unref(_this)->getDispatchInfo()),btDispatcherInfo);
}
DEFINE_PRIM(_IDL, btCollisionWorld_getDispatchInfo0, _IDL);

HL_PRIM void HL_NAME(btCollisionWorld_addCollisionObject3)(_ref(btCollisionWorld)* _this, _ref(btCollisionObject)* collisionObject, _OPT(short) collisionFilterGroup, _OPT(short) collisionFilterMask) {
	if( !collisionFilterGroup )
		_unref(_this)->addCollisionObject(_unref(collisionObject));
	else
	if( !collisionFilterMask )
		_unref(_this)->addCollisionObject(_unref(collisionObject), _GET_OPT(collisionFilterGroup,ui16));
	else
		_unref(_this)->addCollisionObject(_unref(collisionObject), _GET_OPT(collisionFilterGroup,ui16), _GET_OPT(collisionFilterMask,ui16));
}
DEFINE_PRIM(_VOID, btCollisionWorld_addCollisionObject3, _IDL _IDL _NULL(_I16) _NULL(_I16));

HL_PRIM HL_CONST _ref(btBroadphaseInterface)* HL_NAME(btCollisionWorld_getBroadphase0)(_ref(btCollisionWorld)* _this) {
	return alloc_ref_const((_unref(_this)->getBroadphase()),btBroadphaseInterface);
}
DEFINE_PRIM(_IDL, btCollisionWorld_getBroadphase0, _IDL);

HL_PRIM void HL_NAME(btCollisionWorld_convexSweepTest5)(_ref(btCollisionWorld)* _this, _ref(btConvexShape)* castShape, _ref(btTransform)* from, _ref(btTransform)* to, _ref(btCollisionWorld::ConvexResultCallback)* resultCallback, float allowedCcdPenetration) {
	_unref(_this)->convexSweepTest(_unref(castShape), *_unref(from), *_unref(to), *_unref(resultCallback), allowedCcdPenetration);
}
DEFINE_PRIM(_VOID, btCollisionWorld_convexSweepTest5, _IDL _IDL _IDL _IDL _IDL _F32);

HL_PRIM void HL_NAME(btCollisionWorld_contactPairTest3)(_ref(btCollisionWorld)* _this, _ref(btCollisionObject)* colObjA, _ref(btCollisionObject)* colObjB, _ref(btCollisionWorld::ContactResultCallback)* resultCallback) {
	_unref(_this)->contactPairTest(_unref(colObjA), _unref(colObjB), *_unref(resultCallback));
}
DEFINE_PRIM(_VOID, btCollisionWorld_contactPairTest3, _IDL _IDL _IDL _IDL);

HL_PRIM void HL_NAME(btCollisionWorld_contactTest2)(_ref(btCollisionWorld)* _this, _ref(btCollisionObject)* colObj, _ref(btCollisionWorld::ContactResultCallback)* resultCallback) {
	_unref(_this)->contactTest(_unref(colObj), *_unref(resultCallback));
}
DEFINE_PRIM(_VOID, btCollisionWorld_contactTest2, _IDL _IDL _IDL);

HL_PRIM void HL_NAME(btCollisionWorld_updateSingleAabb1)(_ref(btCollisionWorld)* _this, _ref(btCollisionObject)* collisionObject) {
	_unref(_this)->updateSingleAabb(_unref(collisionObject));
}
DEFINE_PRIM(_VOID, btCollisionWorld_updateSingleAabb1, _IDL _IDL);

HL_PRIM void HL_NAME(btCollisionWorld_debugDrawWorld0)(_ref(btCollisionWorld)* _this) {
	_unref(_this)->debugDrawWorld();
}
DEFINE_PRIM(_VOID, btCollisionWorld_debugDrawWorld0, _IDL);

HL_PRIM int HL_NAME(btContactSolverInfo_get_m_splitImpulse)( _ref(btContactSolverInfo)* _this ) {
	return _unref(_this)->m_splitImpulse;
}
HL_PRIM int HL_NAME(btContactSolverInfo_set_m_splitImpulse)( _ref(btContactSolverInfo)* _this, int value ) {
	_unref(_this)->m_splitImpulse = (value);
	return value;
}
DEFINE_PRIM(_I32,btContactSolverInfo_get_m_splitImpulse,_IDL);
DEFINE_PRIM(_I32,btContactSolverInfo_set_m_splitImpulse,_IDL _I32);

HL_PRIM int HL_NAME(btContactSolverInfo_get_m_splitImpulsePenetrationThreshold)( _ref(btContactSolverInfo)* _this ) {
	return _unref(_this)->m_splitImpulsePenetrationThreshold;
}
HL_PRIM int HL_NAME(btContactSolverInfo_set_m_splitImpulsePenetrationThreshold)( _ref(btContactSolverInfo)* _this, int value ) {
	_unref(_this)->m_splitImpulsePenetrationThreshold = (value);
	return value;
}
DEFINE_PRIM(_I32,btContactSolverInfo_get_m_splitImpulsePenetrationThreshold,_IDL);
DEFINE_PRIM(_I32,btContactSolverInfo_set_m_splitImpulsePenetrationThreshold,_IDL _I32);

HL_PRIM int HL_NAME(btContactSolverInfo_get_m_numIterations)( _ref(btContactSolverInfo)* _this ) {
	return _unref(_this)->m_numIterations;
}
HL_PRIM int HL_NAME(btContactSolverInfo_set_m_numIterations)( _ref(btContactSolverInfo)* _this, int value ) {
	_unref(_this)->m_numIterations = (value);
	return value;
}
DEFINE_PRIM(_I32,btContactSolverInfo_get_m_numIterations,_IDL);
DEFINE_PRIM(_I32,btContactSolverInfo_set_m_numIterations,_IDL _I32);

HL_PRIM void HL_NAME(btDynamicsWorld_addAction1)(_ref(btDynamicsWorld)* _this, _ref(btActionInterface)* action) {
	_unref(_this)->addAction(_unref(action));
}
DEFINE_PRIM(_VOID, btDynamicsWorld_addAction1, _IDL _IDL);

HL_PRIM void HL_NAME(btDynamicsWorld_removeAction1)(_ref(btDynamicsWorld)* _this, _ref(btActionInterface)* action) {
	_unref(_this)->removeAction(_unref(action));
}
DEFINE_PRIM(_VOID, btDynamicsWorld_removeAction1, _IDL _IDL);

HL_PRIM _ref(btContactSolverInfo)* HL_NAME(btDynamicsWorld_getSolverInfo0)(_ref(btDynamicsWorld)* _this) {
	return alloc_ref(new btContactSolverInfo(_unref(_this)->getSolverInfo()),btContactSolverInfo);
}
DEFINE_PRIM(_IDL, btDynamicsWorld_getSolverInfo0, _IDL);

HL_PRIM _ref(btDiscreteDynamicsWorld)* HL_NAME(btDiscreteDynamicsWorld_new4)(_ref(btDispatcher)* dispatcher, _ref(btBroadphaseInterface)* pairCache, _ref(btConstraintSolver)* constraintSolver, _ref(btCollisionConfiguration)* collisionConfiguration) {
	return alloc_ref((new btDiscreteDynamicsWorld(_unref(dispatcher), _unref(pairCache), _unref(constraintSolver), _unref(collisionConfiguration))),btDiscreteDynamicsWorld);
}
DEFINE_PRIM(_IDL, btDiscreteDynamicsWorld_new4, _IDL _IDL _IDL _IDL);

HL_PRIM void HL_NAME(btDiscreteDynamicsWorld_setGravity1)(_ref(btDiscreteDynamicsWorld)* _this, _ref(btVector3)* gravity) {
	_unref(_this)->setGravity(*_unref(gravity));
}
DEFINE_PRIM(_VOID, btDiscreteDynamicsWorld_setGravity1, _IDL _IDL);

HL_PRIM _ref(btVector3)* HL_NAME(btDiscreteDynamicsWorld_getGravity0)(_ref(btDiscreteDynamicsWorld)* _this) {
	return alloc_ref(new btVector3(_unref(_this)->getGravity()),btVector3);
}
DEFINE_PRIM(_IDL, btDiscreteDynamicsWorld_getGravity0, _IDL);

HL_PRIM void HL_NAME(btDiscreteDynamicsWorld_addRigidBody1)(_ref(btDiscreteDynamicsWorld)* _this, _ref(btRigidBody)* body) {
	_unref(_this)->addRigidBody(_unref(body));
}
DEFINE_PRIM(_VOID, btDiscreteDynamicsWorld_addRigidBody1, _IDL _IDL);

HL_PRIM void HL_NAME(btDiscreteDynamicsWorld_addRigidBody3)(_ref(btDiscreteDynamicsWorld)* _this, _ref(btRigidBody)* body, short group, short mask) {
	_unref(_this)->addRigidBody(_unref(body), group, mask);
}
DEFINE_PRIM(_VOID, btDiscreteDynamicsWorld_addRigidBody3, _IDL _IDL _I16 _I16);

HL_PRIM void HL_NAME(btDiscreteDynamicsWorld_removeRigidBody1)(_ref(btDiscreteDynamicsWorld)* _this, _ref(btRigidBody)* body) {
	_unref(_this)->removeRigidBody(_unref(body));
}
DEFINE_PRIM(_VOID, btDiscreteDynamicsWorld_removeRigidBody1, _IDL _IDL);

HL_PRIM void HL_NAME(btDiscreteDynamicsWorld_addConstraint2)(_ref(btDiscreteDynamicsWorld)* _this, _ref(btTypedConstraint)* constraint, _OPT(bool) disableCollisionsBetweenLinkedBodies) {
	if( !disableCollisionsBetweenLinkedBodies )
		_unref(_this)->addConstraint(_unref(constraint));
	else
		_unref(_this)->addConstraint(_unref(constraint), _GET_OPT(disableCollisionsBetweenLinkedBodies,b));
}
DEFINE_PRIM(_VOID, btDiscreteDynamicsWorld_addConstraint2, _IDL _IDL _NULL(_BOOL));

HL_PRIM void HL_NAME(btDiscreteDynamicsWorld_removeConstraint1)(_ref(btDiscreteDynamicsWorld)* _this, _ref(btTypedConstraint)* constraint) {
	_unref(_this)->removeConstraint(_unref(constraint));
}
DEFINE_PRIM(_VOID, btDiscreteDynamicsWorld_removeConstraint1, _IDL _IDL);

HL_PRIM int HL_NAME(btDiscreteDynamicsWorld_stepSimulation3)(_ref(btDiscreteDynamicsWorld)* _this, float timeStep, _OPT(int) maxSubSteps, _OPT(float) fixedTimeStep) {
	if( !maxSubSteps )
		return _unref(_this)->stepSimulation(timeStep);
	else
	if( !fixedTimeStep )
		return _unref(_this)->stepSimulation(timeStep, _GET_OPT(maxSubSteps,i));
	else
		return _unref(_this)->stepSimulation(timeStep, _GET_OPT(maxSubSteps,i), _GET_OPT(fixedTimeStep,f));
}
DEFINE_PRIM(_I32, btDiscreteDynamicsWorld_stepSimulation3, _IDL _F32 _NULL(_I32) _NULL(_F32));

HL_PRIM _ref(btRaycastVehicle::btVehicleTuning)* HL_NAME(btVehicleTuning_new0)() {
	return alloc_ref((new btRaycastVehicle::btVehicleTuning()),btVehicleTuning);
}
DEFINE_PRIM(_IDL, btVehicleTuning_new0,);

HL_PRIM float HL_NAME(btVehicleTuning_get_m_suspensionStiffness)( _ref(btRaycastVehicle::btVehicleTuning)* _this ) {
	return _unref(_this)->m_suspensionStiffness;
}
HL_PRIM float HL_NAME(btVehicleTuning_set_m_suspensionStiffness)( _ref(btRaycastVehicle::btVehicleTuning)* _this, float value ) {
	_unref(_this)->m_suspensionStiffness = (value);
	return value;
}
DEFINE_PRIM(_F32,btVehicleTuning_get_m_suspensionStiffness,_IDL);
DEFINE_PRIM(_F32,btVehicleTuning_set_m_suspensionStiffness,_IDL _F32);

HL_PRIM float HL_NAME(btVehicleTuning_get_m_suspensionCompression)( _ref(btRaycastVehicle::btVehicleTuning)* _this ) {
	return _unref(_this)->m_suspensionCompression;
}
HL_PRIM float HL_NAME(btVehicleTuning_set_m_suspensionCompression)( _ref(btRaycastVehicle::btVehicleTuning)* _this, float value ) {
	_unref(_this)->m_suspensionCompression = (value);
	return value;
}
DEFINE_PRIM(_F32,btVehicleTuning_get_m_suspensionCompression,_IDL);
DEFINE_PRIM(_F32,btVehicleTuning_set_m_suspensionCompression,_IDL _F32);

HL_PRIM float HL_NAME(btVehicleTuning_get_m_suspensionDamping)( _ref(btRaycastVehicle::btVehicleTuning)* _this ) {
	return _unref(_this)->m_suspensionDamping;
}
HL_PRIM float HL_NAME(btVehicleTuning_set_m_suspensionDamping)( _ref(btRaycastVehicle::btVehicleTuning)* _this, float value ) {
	_unref(_this)->m_suspensionDamping = (value);
	return value;
}
DEFINE_PRIM(_F32,btVehicleTuning_get_m_suspensionDamping,_IDL);
DEFINE_PRIM(_F32,btVehicleTuning_set_m_suspensionDamping,_IDL _F32);

HL_PRIM float HL_NAME(btVehicleTuning_get_m_maxSuspensionTravelCm)( _ref(btRaycastVehicle::btVehicleTuning)* _this ) {
	return _unref(_this)->m_maxSuspensionTravelCm;
}
HL_PRIM float HL_NAME(btVehicleTuning_set_m_maxSuspensionTravelCm)( _ref(btRaycastVehicle::btVehicleTuning)* _this, float value ) {
	_unref(_this)->m_maxSuspensionTravelCm = (value);
	return value;
}
DEFINE_PRIM(_F32,btVehicleTuning_get_m_maxSuspensionTravelCm,_IDL);
DEFINE_PRIM(_F32,btVehicleTuning_set_m_maxSuspensionTravelCm,_IDL _F32);

HL_PRIM float HL_NAME(btVehicleTuning_get_m_frictionSlip)( _ref(btRaycastVehicle::btVehicleTuning)* _this ) {
	return _unref(_this)->m_frictionSlip;
}
HL_PRIM float HL_NAME(btVehicleTuning_set_m_frictionSlip)( _ref(btRaycastVehicle::btVehicleTuning)* _this, float value ) {
	_unref(_this)->m_frictionSlip = (value);
	return value;
}
DEFINE_PRIM(_F32,btVehicleTuning_get_m_frictionSlip,_IDL);
DEFINE_PRIM(_F32,btVehicleTuning_set_m_frictionSlip,_IDL _F32);

HL_PRIM float HL_NAME(btVehicleTuning_get_m_maxSuspensionForce)( _ref(btRaycastVehicle::btVehicleTuning)* _this ) {
	return _unref(_this)->m_maxSuspensionForce;
}
HL_PRIM float HL_NAME(btVehicleTuning_set_m_maxSuspensionForce)( _ref(btRaycastVehicle::btVehicleTuning)* _this, float value ) {
	_unref(_this)->m_maxSuspensionForce = (value);
	return value;
}
DEFINE_PRIM(_F32,btVehicleTuning_get_m_maxSuspensionForce,_IDL);
DEFINE_PRIM(_F32,btVehicleTuning_set_m_maxSuspensionForce,_IDL _F32);

HL_PRIM _ref(btVector3)* HL_NAME(btVehicleRaycasterResult_get_m_hitPointInWorld)( _ref(btDefaultVehicleRaycaster::btVehicleRaycasterResult)* _this ) {
	return alloc_ref(new btVector3(_unref(_this)->m_hitPointInWorld),btVector3);
}
HL_PRIM _ref(btVector3)* HL_NAME(btVehicleRaycasterResult_set_m_hitPointInWorld)( _ref(btDefaultVehicleRaycaster::btVehicleRaycasterResult)* _this, _ref(btVector3)* value ) {
	_unref(_this)->m_hitPointInWorld = *_unref(value);
	return value;
}
DEFINE_PRIM(_IDL,btVehicleRaycasterResult_get_m_hitPointInWorld,_IDL);
DEFINE_PRIM(_IDL,btVehicleRaycasterResult_set_m_hitPointInWorld,_IDL _IDL);

HL_PRIM _ref(btVector3)* HL_NAME(btVehicleRaycasterResult_get_m_hitNormalInWorld)( _ref(btDefaultVehicleRaycaster::btVehicleRaycasterResult)* _this ) {
	return alloc_ref(new btVector3(_unref(_this)->m_hitNormalInWorld),btVector3);
}
HL_PRIM _ref(btVector3)* HL_NAME(btVehicleRaycasterResult_set_m_hitNormalInWorld)( _ref(btDefaultVehicleRaycaster::btVehicleRaycasterResult)* _this, _ref(btVector3)* value ) {
	_unref(_this)->m_hitNormalInWorld = *_unref(value);
	return value;
}
DEFINE_PRIM(_IDL,btVehicleRaycasterResult_get_m_hitNormalInWorld,_IDL);
DEFINE_PRIM(_IDL,btVehicleRaycasterResult_set_m_hitNormalInWorld,_IDL _IDL);

HL_PRIM float HL_NAME(btVehicleRaycasterResult_get_m_distFraction)( _ref(btDefaultVehicleRaycaster::btVehicleRaycasterResult)* _this ) {
	return _unref(_this)->m_distFraction;
}
HL_PRIM float HL_NAME(btVehicleRaycasterResult_set_m_distFraction)( _ref(btDefaultVehicleRaycaster::btVehicleRaycasterResult)* _this, float value ) {
	_unref(_this)->m_distFraction = (value);
	return value;
}
DEFINE_PRIM(_F32,btVehicleRaycasterResult_get_m_distFraction,_IDL);
DEFINE_PRIM(_F32,btVehicleRaycasterResult_set_m_distFraction,_IDL _F32);

HL_PRIM void HL_NAME(btVehicleRaycaster_castRay3)(_ref(btVehicleRaycaster)* _this, _ref(btVector3)* from, _ref(btVector3)* to, _ref(btDefaultVehicleRaycaster::btVehicleRaycasterResult)* result) {
	_unref(_this)->castRay(*_unref(from), *_unref(to), *_unref(result));
}
DEFINE_PRIM(_VOID, btVehicleRaycaster_castRay3, _IDL _IDL _IDL _IDL);

HL_PRIM _ref(btDefaultVehicleRaycaster)* HL_NAME(btDefaultVehicleRaycaster_new1)(_ref(btDynamicsWorld)* world) {
	return alloc_ref((new btDefaultVehicleRaycaster(_unref(world))),btDefaultVehicleRaycaster);
}
DEFINE_PRIM(_IDL, btDefaultVehicleRaycaster_new1, _IDL);

HL_PRIM _ref(btVector3)* HL_NAME(RaycastInfo_get_m_contactNormalWS)( _ref(btWheelInfo::RaycastInfo)* _this ) {
	return alloc_ref(new btVector3(_unref(_this)->m_contactNormalWS),btVector3);
}
HL_PRIM _ref(btVector3)* HL_NAME(RaycastInfo_set_m_contactNormalWS)( _ref(btWheelInfo::RaycastInfo)* _this, _ref(btVector3)* value ) {
	_unref(_this)->m_contactNormalWS = *_unref(value);
	return value;
}
DEFINE_PRIM(_IDL,RaycastInfo_get_m_contactNormalWS,_IDL);
DEFINE_PRIM(_IDL,RaycastInfo_set_m_contactNormalWS,_IDL _IDL);

HL_PRIM _ref(btVector3)* HL_NAME(RaycastInfo_get_m_contactPointWS)( _ref(btWheelInfo::RaycastInfo)* _this ) {
	return alloc_ref(new btVector3(_unref(_this)->m_contactPointWS),btVector3);
}
HL_PRIM _ref(btVector3)* HL_NAME(RaycastInfo_set_m_contactPointWS)( _ref(btWheelInfo::RaycastInfo)* _this, _ref(btVector3)* value ) {
	_unref(_this)->m_contactPointWS = *_unref(value);
	return value;
}
DEFINE_PRIM(_IDL,RaycastInfo_get_m_contactPointWS,_IDL);
DEFINE_PRIM(_IDL,RaycastInfo_set_m_contactPointWS,_IDL _IDL);

HL_PRIM float HL_NAME(RaycastInfo_get_m_suspensionLength)( _ref(btWheelInfo::RaycastInfo)* _this ) {
	return _unref(_this)->m_suspensionLength;
}
HL_PRIM float HL_NAME(RaycastInfo_set_m_suspensionLength)( _ref(btWheelInfo::RaycastInfo)* _this, float value ) {
	_unref(_this)->m_suspensionLength = (value);
	return value;
}
DEFINE_PRIM(_F32,RaycastInfo_get_m_suspensionLength,_IDL);
DEFINE_PRIM(_F32,RaycastInfo_set_m_suspensionLength,_IDL _F32);

HL_PRIM _ref(btVector3)* HL_NAME(RaycastInfo_get_m_hardPointWS)( _ref(btWheelInfo::RaycastInfo)* _this ) {
	return alloc_ref(new btVector3(_unref(_this)->m_hardPointWS),btVector3);
}
HL_PRIM _ref(btVector3)* HL_NAME(RaycastInfo_set_m_hardPointWS)( _ref(btWheelInfo::RaycastInfo)* _this, _ref(btVector3)* value ) {
	_unref(_this)->m_hardPointWS = *_unref(value);
	return value;
}
DEFINE_PRIM(_IDL,RaycastInfo_get_m_hardPointWS,_IDL);
DEFINE_PRIM(_IDL,RaycastInfo_set_m_hardPointWS,_IDL _IDL);

HL_PRIM _ref(btVector3)* HL_NAME(RaycastInfo_get_m_wheelDirectionWS)( _ref(btWheelInfo::RaycastInfo)* _this ) {
	return alloc_ref(new btVector3(_unref(_this)->m_wheelDirectionWS),btVector3);
}
HL_PRIM _ref(btVector3)* HL_NAME(RaycastInfo_set_m_wheelDirectionWS)( _ref(btWheelInfo::RaycastInfo)* _this, _ref(btVector3)* value ) {
	_unref(_this)->m_wheelDirectionWS = *_unref(value);
	return value;
}
DEFINE_PRIM(_IDL,RaycastInfo_get_m_wheelDirectionWS,_IDL);
DEFINE_PRIM(_IDL,RaycastInfo_set_m_wheelDirectionWS,_IDL _IDL);

HL_PRIM _ref(btVector3)* HL_NAME(RaycastInfo_get_m_wheelAxleWS)( _ref(btWheelInfo::RaycastInfo)* _this ) {
	return alloc_ref(new btVector3(_unref(_this)->m_wheelAxleWS),btVector3);
}
HL_PRIM _ref(btVector3)* HL_NAME(RaycastInfo_set_m_wheelAxleWS)( _ref(btWheelInfo::RaycastInfo)* _this, _ref(btVector3)* value ) {
	_unref(_this)->m_wheelAxleWS = *_unref(value);
	return value;
}
DEFINE_PRIM(_IDL,RaycastInfo_get_m_wheelAxleWS,_IDL);
DEFINE_PRIM(_IDL,RaycastInfo_set_m_wheelAxleWS,_IDL _IDL);

HL_PRIM bool HL_NAME(RaycastInfo_get_m_isInContact)( _ref(btWheelInfo::RaycastInfo)* _this ) {
	return _unref(_this)->m_isInContact;
}
HL_PRIM bool HL_NAME(RaycastInfo_set_m_isInContact)( _ref(btWheelInfo::RaycastInfo)* _this, bool value ) {
	_unref(_this)->m_isInContact = (value);
	return value;
}
DEFINE_PRIM(_BOOL,RaycastInfo_get_m_isInContact,_IDL);
DEFINE_PRIM(_BOOL,RaycastInfo_set_m_isInContact,_IDL _BOOL);

HL_PRIM void* HL_NAME(RaycastInfo_get_m_groundObject)( _ref(btWheelInfo::RaycastInfo)* _this ) {
	return _unref(_this)->m_groundObject;
}
HL_PRIM void* HL_NAME(RaycastInfo_set_m_groundObject)( _ref(btWheelInfo::RaycastInfo)* _this, void* value ) {
	_unref(_this)->m_groundObject = (value);
	return value;
}
DEFINE_PRIM(_BYTES,RaycastInfo_get_m_groundObject,_IDL);
DEFINE_PRIM(_BYTES,RaycastInfo_set_m_groundObject,_IDL _BYTES);

HL_PRIM _ref(btVector3)* HL_NAME(btWheelInfoConstructionInfo_get_m_chassisConnectionCS)( _ref(btWheelInfoConstructionInfo)* _this ) {
	return alloc_ref(new btVector3(_unref(_this)->m_chassisConnectionCS),btVector3);
}
HL_PRIM _ref(btVector3)* HL_NAME(btWheelInfoConstructionInfo_set_m_chassisConnectionCS)( _ref(btWheelInfoConstructionInfo)* _this, _ref(btVector3)* value ) {
	_unref(_this)->m_chassisConnectionCS = *_unref(value);
	return value;
}
DEFINE_PRIM(_IDL,btWheelInfoConstructionInfo_get_m_chassisConnectionCS,_IDL);
DEFINE_PRIM(_IDL,btWheelInfoConstructionInfo_set_m_chassisConnectionCS,_IDL _IDL);

HL_PRIM _ref(btVector3)* HL_NAME(btWheelInfoConstructionInfo_get_m_wheelDirectionCS)( _ref(btWheelInfoConstructionInfo)* _this ) {
	return alloc_ref(new btVector3(_unref(_this)->m_wheelDirectionCS),btVector3);
}
HL_PRIM _ref(btVector3)* HL_NAME(btWheelInfoConstructionInfo_set_m_wheelDirectionCS)( _ref(btWheelInfoConstructionInfo)* _this, _ref(btVector3)* value ) {
	_unref(_this)->m_wheelDirectionCS = *_unref(value);
	return value;
}
DEFINE_PRIM(_IDL,btWheelInfoConstructionInfo_get_m_wheelDirectionCS,_IDL);
DEFINE_PRIM(_IDL,btWheelInfoConstructionInfo_set_m_wheelDirectionCS,_IDL _IDL);

HL_PRIM _ref(btVector3)* HL_NAME(btWheelInfoConstructionInfo_get_m_wheelAxleCS)( _ref(btWheelInfoConstructionInfo)* _this ) {
	return alloc_ref(new btVector3(_unref(_this)->m_wheelAxleCS),btVector3);
}
HL_PRIM _ref(btVector3)* HL_NAME(btWheelInfoConstructionInfo_set_m_wheelAxleCS)( _ref(btWheelInfoConstructionInfo)* _this, _ref(btVector3)* value ) {
	_unref(_this)->m_wheelAxleCS = *_unref(value);
	return value;
}
DEFINE_PRIM(_IDL,btWheelInfoConstructionInfo_get_m_wheelAxleCS,_IDL);
DEFINE_PRIM(_IDL,btWheelInfoConstructionInfo_set_m_wheelAxleCS,_IDL _IDL);

HL_PRIM float HL_NAME(btWheelInfoConstructionInfo_get_m_suspensionRestLength)( _ref(btWheelInfoConstructionInfo)* _this ) {
	return _unref(_this)->m_suspensionRestLength;
}
HL_PRIM float HL_NAME(btWheelInfoConstructionInfo_set_m_suspensionRestLength)( _ref(btWheelInfoConstructionInfo)* _this, float value ) {
	_unref(_this)->m_suspensionRestLength = (value);
	return value;
}
DEFINE_PRIM(_F32,btWheelInfoConstructionInfo_get_m_suspensionRestLength,_IDL);
DEFINE_PRIM(_F32,btWheelInfoConstructionInfo_set_m_suspensionRestLength,_IDL _F32);

HL_PRIM float HL_NAME(btWheelInfoConstructionInfo_get_m_maxSuspensionTravelCm)( _ref(btWheelInfoConstructionInfo)* _this ) {
	return _unref(_this)->m_maxSuspensionTravelCm;
}
HL_PRIM float HL_NAME(btWheelInfoConstructionInfo_set_m_maxSuspensionTravelCm)( _ref(btWheelInfoConstructionInfo)* _this, float value ) {
	_unref(_this)->m_maxSuspensionTravelCm = (value);
	return value;
}
DEFINE_PRIM(_F32,btWheelInfoConstructionInfo_get_m_maxSuspensionTravelCm,_IDL);
DEFINE_PRIM(_F32,btWheelInfoConstructionInfo_set_m_maxSuspensionTravelCm,_IDL _F32);

HL_PRIM float HL_NAME(btWheelInfoConstructionInfo_get_m_wheelRadius)( _ref(btWheelInfoConstructionInfo)* _this ) {
	return _unref(_this)->m_wheelRadius;
}
HL_PRIM float HL_NAME(btWheelInfoConstructionInfo_set_m_wheelRadius)( _ref(btWheelInfoConstructionInfo)* _this, float value ) {
	_unref(_this)->m_wheelRadius = (value);
	return value;
}
DEFINE_PRIM(_F32,btWheelInfoConstructionInfo_get_m_wheelRadius,_IDL);
DEFINE_PRIM(_F32,btWheelInfoConstructionInfo_set_m_wheelRadius,_IDL _F32);

HL_PRIM float HL_NAME(btWheelInfoConstructionInfo_get_m_suspensionStiffness)( _ref(btWheelInfoConstructionInfo)* _this ) {
	return _unref(_this)->m_suspensionStiffness;
}
HL_PRIM float HL_NAME(btWheelInfoConstructionInfo_set_m_suspensionStiffness)( _ref(btWheelInfoConstructionInfo)* _this, float value ) {
	_unref(_this)->m_suspensionStiffness = (value);
	return value;
}
DEFINE_PRIM(_F32,btWheelInfoConstructionInfo_get_m_suspensionStiffness,_IDL);
DEFINE_PRIM(_F32,btWheelInfoConstructionInfo_set_m_suspensionStiffness,_IDL _F32);

HL_PRIM float HL_NAME(btWheelInfoConstructionInfo_get_m_wheelsDampingCompression)( _ref(btWheelInfoConstructionInfo)* _this ) {
	return _unref(_this)->m_wheelsDampingCompression;
}
HL_PRIM float HL_NAME(btWheelInfoConstructionInfo_set_m_wheelsDampingCompression)( _ref(btWheelInfoConstructionInfo)* _this, float value ) {
	_unref(_this)->m_wheelsDampingCompression = (value);
	return value;
}
DEFINE_PRIM(_F32,btWheelInfoConstructionInfo_get_m_wheelsDampingCompression,_IDL);
DEFINE_PRIM(_F32,btWheelInfoConstructionInfo_set_m_wheelsDampingCompression,_IDL _F32);

HL_PRIM float HL_NAME(btWheelInfoConstructionInfo_get_m_wheelsDampingRelaxation)( _ref(btWheelInfoConstructionInfo)* _this ) {
	return _unref(_this)->m_wheelsDampingRelaxation;
}
HL_PRIM float HL_NAME(btWheelInfoConstructionInfo_set_m_wheelsDampingRelaxation)( _ref(btWheelInfoConstructionInfo)* _this, float value ) {
	_unref(_this)->m_wheelsDampingRelaxation = (value);
	return value;
}
DEFINE_PRIM(_F32,btWheelInfoConstructionInfo_get_m_wheelsDampingRelaxation,_IDL);
DEFINE_PRIM(_F32,btWheelInfoConstructionInfo_set_m_wheelsDampingRelaxation,_IDL _F32);

HL_PRIM float HL_NAME(btWheelInfoConstructionInfo_get_m_frictionSlip)( _ref(btWheelInfoConstructionInfo)* _this ) {
	return _unref(_this)->m_frictionSlip;
}
HL_PRIM float HL_NAME(btWheelInfoConstructionInfo_set_m_frictionSlip)( _ref(btWheelInfoConstructionInfo)* _this, float value ) {
	_unref(_this)->m_frictionSlip = (value);
	return value;
}
DEFINE_PRIM(_F32,btWheelInfoConstructionInfo_get_m_frictionSlip,_IDL);
DEFINE_PRIM(_F32,btWheelInfoConstructionInfo_set_m_frictionSlip,_IDL _F32);

HL_PRIM float HL_NAME(btWheelInfoConstructionInfo_get_m_maxSuspensionForce)( _ref(btWheelInfoConstructionInfo)* _this ) {
	return _unref(_this)->m_maxSuspensionForce;
}
HL_PRIM float HL_NAME(btWheelInfoConstructionInfo_set_m_maxSuspensionForce)( _ref(btWheelInfoConstructionInfo)* _this, float value ) {
	_unref(_this)->m_maxSuspensionForce = (value);
	return value;
}
DEFINE_PRIM(_F32,btWheelInfoConstructionInfo_get_m_maxSuspensionForce,_IDL);
DEFINE_PRIM(_F32,btWheelInfoConstructionInfo_set_m_maxSuspensionForce,_IDL _F32);

HL_PRIM bool HL_NAME(btWheelInfoConstructionInfo_get_m_bIsFrontWheel)( _ref(btWheelInfoConstructionInfo)* _this ) {
	return _unref(_this)->m_bIsFrontWheel;
}
HL_PRIM bool HL_NAME(btWheelInfoConstructionInfo_set_m_bIsFrontWheel)( _ref(btWheelInfoConstructionInfo)* _this, bool value ) {
	_unref(_this)->m_bIsFrontWheel = (value);
	return value;
}
DEFINE_PRIM(_BOOL,btWheelInfoConstructionInfo_get_m_bIsFrontWheel,_IDL);
DEFINE_PRIM(_BOOL,btWheelInfoConstructionInfo_set_m_bIsFrontWheel,_IDL _BOOL);

HL_PRIM float HL_NAME(btWheelInfo_get_m_suspensionStiffness)( _ref(btWheelInfo)* _this ) {
	return _unref(_this)->m_suspensionStiffness;
}
HL_PRIM float HL_NAME(btWheelInfo_set_m_suspensionStiffness)( _ref(btWheelInfo)* _this, float value ) {
	_unref(_this)->m_suspensionStiffness = (value);
	return value;
}
DEFINE_PRIM(_F32,btWheelInfo_get_m_suspensionStiffness,_IDL);
DEFINE_PRIM(_F32,btWheelInfo_set_m_suspensionStiffness,_IDL _F32);

HL_PRIM float HL_NAME(btWheelInfo_get_m_frictionSlip)( _ref(btWheelInfo)* _this ) {
	return _unref(_this)->m_frictionSlip;
}
HL_PRIM float HL_NAME(btWheelInfo_set_m_frictionSlip)( _ref(btWheelInfo)* _this, float value ) {
	_unref(_this)->m_frictionSlip = (value);
	return value;
}
DEFINE_PRIM(_F32,btWheelInfo_get_m_frictionSlip,_IDL);
DEFINE_PRIM(_F32,btWheelInfo_set_m_frictionSlip,_IDL _F32);

HL_PRIM float HL_NAME(btWheelInfo_get_m_engineForce)( _ref(btWheelInfo)* _this ) {
	return _unref(_this)->m_engineForce;
}
HL_PRIM float HL_NAME(btWheelInfo_set_m_engineForce)( _ref(btWheelInfo)* _this, float value ) {
	_unref(_this)->m_engineForce = (value);
	return value;
}
DEFINE_PRIM(_F32,btWheelInfo_get_m_engineForce,_IDL);
DEFINE_PRIM(_F32,btWheelInfo_set_m_engineForce,_IDL _F32);

HL_PRIM float HL_NAME(btWheelInfo_get_m_rollInfluence)( _ref(btWheelInfo)* _this ) {
	return _unref(_this)->m_rollInfluence;
}
HL_PRIM float HL_NAME(btWheelInfo_set_m_rollInfluence)( _ref(btWheelInfo)* _this, float value ) {
	_unref(_this)->m_rollInfluence = (value);
	return value;
}
DEFINE_PRIM(_F32,btWheelInfo_get_m_rollInfluence,_IDL);
DEFINE_PRIM(_F32,btWheelInfo_set_m_rollInfluence,_IDL _F32);

HL_PRIM float HL_NAME(btWheelInfo_get_m_suspensionRestLength1)( _ref(btWheelInfo)* _this ) {
	return _unref(_this)->m_suspensionRestLength1;
}
HL_PRIM float HL_NAME(btWheelInfo_set_m_suspensionRestLength1)( _ref(btWheelInfo)* _this, float value ) {
	_unref(_this)->m_suspensionRestLength1 = (value);
	return value;
}
DEFINE_PRIM(_F32,btWheelInfo_get_m_suspensionRestLength1,_IDL);
DEFINE_PRIM(_F32,btWheelInfo_set_m_suspensionRestLength1,_IDL _F32);

HL_PRIM float HL_NAME(btWheelInfo_get_m_wheelsRadius)( _ref(btWheelInfo)* _this ) {
	return _unref(_this)->m_wheelsRadius;
}
HL_PRIM float HL_NAME(btWheelInfo_set_m_wheelsRadius)( _ref(btWheelInfo)* _this, float value ) {
	_unref(_this)->m_wheelsRadius = (value);
	return value;
}
DEFINE_PRIM(_F32,btWheelInfo_get_m_wheelsRadius,_IDL);
DEFINE_PRIM(_F32,btWheelInfo_set_m_wheelsRadius,_IDL _F32);

HL_PRIM float HL_NAME(btWheelInfo_get_m_wheelsDampingCompression)( _ref(btWheelInfo)* _this ) {
	return _unref(_this)->m_wheelsDampingCompression;
}
HL_PRIM float HL_NAME(btWheelInfo_set_m_wheelsDampingCompression)( _ref(btWheelInfo)* _this, float value ) {
	_unref(_this)->m_wheelsDampingCompression = (value);
	return value;
}
DEFINE_PRIM(_F32,btWheelInfo_get_m_wheelsDampingCompression,_IDL);
DEFINE_PRIM(_F32,btWheelInfo_set_m_wheelsDampingCompression,_IDL _F32);

HL_PRIM float HL_NAME(btWheelInfo_get_m_wheelsDampingRelaxation)( _ref(btWheelInfo)* _this ) {
	return _unref(_this)->m_wheelsDampingRelaxation;
}
HL_PRIM float HL_NAME(btWheelInfo_set_m_wheelsDampingRelaxation)( _ref(btWheelInfo)* _this, float value ) {
	_unref(_this)->m_wheelsDampingRelaxation = (value);
	return value;
}
DEFINE_PRIM(_F32,btWheelInfo_get_m_wheelsDampingRelaxation,_IDL);
DEFINE_PRIM(_F32,btWheelInfo_set_m_wheelsDampingRelaxation,_IDL _F32);

HL_PRIM float HL_NAME(btWheelInfo_get_m_steering)( _ref(btWheelInfo)* _this ) {
	return _unref(_this)->m_steering;
}
HL_PRIM float HL_NAME(btWheelInfo_set_m_steering)( _ref(btWheelInfo)* _this, float value ) {
	_unref(_this)->m_steering = (value);
	return value;
}
DEFINE_PRIM(_F32,btWheelInfo_get_m_steering,_IDL);
DEFINE_PRIM(_F32,btWheelInfo_set_m_steering,_IDL _F32);

HL_PRIM float HL_NAME(btWheelInfo_get_m_maxSuspensionForce)( _ref(btWheelInfo)* _this ) {
	return _unref(_this)->m_maxSuspensionForce;
}
HL_PRIM float HL_NAME(btWheelInfo_set_m_maxSuspensionForce)( _ref(btWheelInfo)* _this, float value ) {
	_unref(_this)->m_maxSuspensionForce = (value);
	return value;
}
DEFINE_PRIM(_F32,btWheelInfo_get_m_maxSuspensionForce,_IDL);
DEFINE_PRIM(_F32,btWheelInfo_set_m_maxSuspensionForce,_IDL _F32);

HL_PRIM float HL_NAME(btWheelInfo_get_m_maxSuspensionTravelCm)( _ref(btWheelInfo)* _this ) {
	return _unref(_this)->m_maxSuspensionTravelCm;
}
HL_PRIM float HL_NAME(btWheelInfo_set_m_maxSuspensionTravelCm)( _ref(btWheelInfo)* _this, float value ) {
	_unref(_this)->m_maxSuspensionTravelCm = (value);
	return value;
}
DEFINE_PRIM(_F32,btWheelInfo_get_m_maxSuspensionTravelCm,_IDL);
DEFINE_PRIM(_F32,btWheelInfo_set_m_maxSuspensionTravelCm,_IDL _F32);

HL_PRIM float HL_NAME(btWheelInfo_get_m_wheelsSuspensionForce)( _ref(btWheelInfo)* _this ) {
	return _unref(_this)->m_wheelsSuspensionForce;
}
HL_PRIM float HL_NAME(btWheelInfo_set_m_wheelsSuspensionForce)( _ref(btWheelInfo)* _this, float value ) {
	_unref(_this)->m_wheelsSuspensionForce = (value);
	return value;
}
DEFINE_PRIM(_F32,btWheelInfo_get_m_wheelsSuspensionForce,_IDL);
DEFINE_PRIM(_F32,btWheelInfo_set_m_wheelsSuspensionForce,_IDL _F32);

HL_PRIM bool HL_NAME(btWheelInfo_get_m_bIsFrontWheel)( _ref(btWheelInfo)* _this ) {
	return _unref(_this)->m_bIsFrontWheel;
}
HL_PRIM bool HL_NAME(btWheelInfo_set_m_bIsFrontWheel)( _ref(btWheelInfo)* _this, bool value ) {
	_unref(_this)->m_bIsFrontWheel = (value);
	return value;
}
DEFINE_PRIM(_BOOL,btWheelInfo_get_m_bIsFrontWheel,_IDL);
DEFINE_PRIM(_BOOL,btWheelInfo_set_m_bIsFrontWheel,_IDL _BOOL);

HL_PRIM _ref(btWheelInfo::RaycastInfo)* HL_NAME(btWheelInfo_get_m_raycastInfo)( _ref(btWheelInfo)* _this ) {
	return alloc_ref(new btWheelInfo::RaycastInfo(_unref(_this)->m_raycastInfo),RaycastInfo);
}
HL_PRIM _ref(btWheelInfo::RaycastInfo)* HL_NAME(btWheelInfo_set_m_raycastInfo)( _ref(btWheelInfo)* _this, _ref(btWheelInfo::RaycastInfo)* value ) {
	_unref(_this)->m_raycastInfo = *_unref(value);
	return value;
}
DEFINE_PRIM(_IDL,btWheelInfo_get_m_raycastInfo,_IDL);
DEFINE_PRIM(_IDL,btWheelInfo_set_m_raycastInfo,_IDL _IDL);

HL_PRIM _ref(btVector3)* HL_NAME(btWheelInfo_get_m_chassisConnectionPointCS)( _ref(btWheelInfo)* _this ) {
	return alloc_ref(new btVector3(_unref(_this)->m_chassisConnectionPointCS),btVector3);
}
HL_PRIM _ref(btVector3)* HL_NAME(btWheelInfo_set_m_chassisConnectionPointCS)( _ref(btWheelInfo)* _this, _ref(btVector3)* value ) {
	_unref(_this)->m_chassisConnectionPointCS = *_unref(value);
	return value;
}
DEFINE_PRIM(_IDL,btWheelInfo_get_m_chassisConnectionPointCS,_IDL);
DEFINE_PRIM(_IDL,btWheelInfo_set_m_chassisConnectionPointCS,_IDL _IDL);

HL_PRIM _ref(btWheelInfo)* HL_NAME(btWheelInfo_new1)(_ref(btWheelInfoConstructionInfo)* ci) {
	return alloc_ref((new btWheelInfo(*_unref(ci))),btWheelInfo);
}
DEFINE_PRIM(_IDL, btWheelInfo_new1, _IDL);

HL_PRIM float HL_NAME(btWheelInfo_getSuspensionRestLength0)(_ref(btWheelInfo)* _this) {
	return _unref(_this)->getSuspensionRestLength();
}
DEFINE_PRIM(_F32, btWheelInfo_getSuspensionRestLength0, _IDL);

HL_PRIM void HL_NAME(btWheelInfo_updateWheel2)(_ref(btWheelInfo)* _this, _ref(btRigidBody)* chassis, _ref(btWheelInfo::RaycastInfo)* raycastInfo) {
	_unref(_this)->updateWheel(*_unref(chassis), *_unref(raycastInfo));
}
DEFINE_PRIM(_VOID, btWheelInfo_updateWheel2, _IDL _IDL _IDL);

HL_PRIM _ref(btTransform)* HL_NAME(btWheelInfo_get_m_worldTransform)( _ref(btWheelInfo)* _this ) {
	return alloc_ref(new btTransform(_unref(_this)->m_worldTransform),btTransform);
}
HL_PRIM _ref(btTransform)* HL_NAME(btWheelInfo_set_m_worldTransform)( _ref(btWheelInfo)* _this, _ref(btTransform)* value ) {
	_unref(_this)->m_worldTransform = *_unref(value);
	return value;
}
DEFINE_PRIM(_IDL,btWheelInfo_get_m_worldTransform,_IDL);
DEFINE_PRIM(_IDL,btWheelInfo_set_m_worldTransform,_IDL _IDL);

HL_PRIM _ref(btVector3)* HL_NAME(btWheelInfo_get_m_wheelDirectionCS)( _ref(btWheelInfo)* _this ) {
	return alloc_ref(new btVector3(_unref(_this)->m_wheelDirectionCS),btVector3);
}
HL_PRIM _ref(btVector3)* HL_NAME(btWheelInfo_set_m_wheelDirectionCS)( _ref(btWheelInfo)* _this, _ref(btVector3)* value ) {
	_unref(_this)->m_wheelDirectionCS = *_unref(value);
	return value;
}
DEFINE_PRIM(_IDL,btWheelInfo_get_m_wheelDirectionCS,_IDL);
DEFINE_PRIM(_IDL,btWheelInfo_set_m_wheelDirectionCS,_IDL _IDL);

HL_PRIM _ref(btVector3)* HL_NAME(btWheelInfo_get_m_wheelAxleCS)( _ref(btWheelInfo)* _this ) {
	return alloc_ref(new btVector3(_unref(_this)->m_wheelAxleCS),btVector3);
}
HL_PRIM _ref(btVector3)* HL_NAME(btWheelInfo_set_m_wheelAxleCS)( _ref(btWheelInfo)* _this, _ref(btVector3)* value ) {
	_unref(_this)->m_wheelAxleCS = *_unref(value);
	return value;
}
DEFINE_PRIM(_IDL,btWheelInfo_get_m_wheelAxleCS,_IDL);
DEFINE_PRIM(_IDL,btWheelInfo_set_m_wheelAxleCS,_IDL _IDL);

HL_PRIM float HL_NAME(btWheelInfo_get_m_rotation)( _ref(btWheelInfo)* _this ) {
	return _unref(_this)->m_rotation;
}
HL_PRIM float HL_NAME(btWheelInfo_set_m_rotation)( _ref(btWheelInfo)* _this, float value ) {
	_unref(_this)->m_rotation = (value);
	return value;
}
DEFINE_PRIM(_F32,btWheelInfo_get_m_rotation,_IDL);
DEFINE_PRIM(_F32,btWheelInfo_set_m_rotation,_IDL _F32);

HL_PRIM float HL_NAME(btWheelInfo_get_m_deltaRotation)( _ref(btWheelInfo)* _this ) {
	return _unref(_this)->m_deltaRotation;
}
HL_PRIM float HL_NAME(btWheelInfo_set_m_deltaRotation)( _ref(btWheelInfo)* _this, float value ) {
	_unref(_this)->m_deltaRotation = (value);
	return value;
}
DEFINE_PRIM(_F32,btWheelInfo_get_m_deltaRotation,_IDL);
DEFINE_PRIM(_F32,btWheelInfo_set_m_deltaRotation,_IDL _F32);

HL_PRIM float HL_NAME(btWheelInfo_get_m_brake)( _ref(btWheelInfo)* _this ) {
	return _unref(_this)->m_brake;
}
HL_PRIM float HL_NAME(btWheelInfo_set_m_brake)( _ref(btWheelInfo)* _this, float value ) {
	_unref(_this)->m_brake = (value);
	return value;
}
DEFINE_PRIM(_F32,btWheelInfo_get_m_brake,_IDL);
DEFINE_PRIM(_F32,btWheelInfo_set_m_brake,_IDL _F32);

HL_PRIM float HL_NAME(btWheelInfo_get_m_clippedInvContactDotSuspension)( _ref(btWheelInfo)* _this ) {
	return _unref(_this)->m_clippedInvContactDotSuspension;
}
HL_PRIM float HL_NAME(btWheelInfo_set_m_clippedInvContactDotSuspension)( _ref(btWheelInfo)* _this, float value ) {
	_unref(_this)->m_clippedInvContactDotSuspension = (value);
	return value;
}
DEFINE_PRIM(_F32,btWheelInfo_get_m_clippedInvContactDotSuspension,_IDL);
DEFINE_PRIM(_F32,btWheelInfo_set_m_clippedInvContactDotSuspension,_IDL _F32);

HL_PRIM float HL_NAME(btWheelInfo_get_m_suspensionRelativeVelocity)( _ref(btWheelInfo)* _this ) {
	return _unref(_this)->m_suspensionRelativeVelocity;
}
HL_PRIM float HL_NAME(btWheelInfo_set_m_suspensionRelativeVelocity)( _ref(btWheelInfo)* _this, float value ) {
	_unref(_this)->m_suspensionRelativeVelocity = (value);
	return value;
}
DEFINE_PRIM(_F32,btWheelInfo_get_m_suspensionRelativeVelocity,_IDL);
DEFINE_PRIM(_F32,btWheelInfo_set_m_suspensionRelativeVelocity,_IDL _F32);

HL_PRIM float HL_NAME(btWheelInfo_get_m_skidInfo)( _ref(btWheelInfo)* _this ) {
	return _unref(_this)->m_skidInfo;
}
HL_PRIM float HL_NAME(btWheelInfo_set_m_skidInfo)( _ref(btWheelInfo)* _this, float value ) {
	_unref(_this)->m_skidInfo = (value);
	return value;
}
DEFINE_PRIM(_F32,btWheelInfo_get_m_skidInfo,_IDL);
DEFINE_PRIM(_F32,btWheelInfo_set_m_skidInfo,_IDL _F32);

HL_PRIM void HL_NAME(btActionInterface_updateAction2)(_ref(btActionInterface)* _this, _ref(btCollisionWorld)* collisionWorld, float deltaTimeStep) {
	_unref(_this)->updateAction(_unref(collisionWorld), deltaTimeStep);
}
DEFINE_PRIM(_VOID, btActionInterface_updateAction2, _IDL _IDL _F32);

HL_PRIM _ref(btKinematicCharacterController)* HL_NAME(btKinematicCharacterController_new4)(_ref(btPairCachingGhostObject)* ghostObject, _ref(btConvexShape)* convexShape, float stepHeight, _ref(btVector3)* upAxis) {
	if( !upAxis )
		return alloc_ref((new btKinematicCharacterController(_unref(ghostObject), _unref(convexShape), stepHeight)),btKinematicCharacterController);
	else
		return alloc_ref((new btKinematicCharacterController(_unref(ghostObject), _unref(convexShape), stepHeight, *_unref(upAxis))),btKinematicCharacterController);
}
DEFINE_PRIM(_IDL, btKinematicCharacterController_new4, _IDL _IDL _F32 _IDL);

HL_PRIM void HL_NAME(btKinematicCharacterController_setUp1)(_ref(btKinematicCharacterController)* _this, _ref(btVector3)* axis) {
	_unref(_this)->setUp(*_unref(axis));
}
DEFINE_PRIM(_VOID, btKinematicCharacterController_setUp1, _IDL _IDL);

HL_PRIM void HL_NAME(btKinematicCharacterController_setWalkDirection1)(_ref(btKinematicCharacterController)* _this, _ref(btVector3)* walkDirection) {
	_unref(_this)->setWalkDirection(*_unref(walkDirection));
}
DEFINE_PRIM(_VOID, btKinematicCharacterController_setWalkDirection1, _IDL _IDL);

HL_PRIM void HL_NAME(btKinematicCharacterController_setVelocityForTimeInterval2)(_ref(btKinematicCharacterController)* _this, _ref(btVector3)* velocity, float timeInterval) {
	_unref(_this)->setVelocityForTimeInterval(*_unref(velocity), timeInterval);
}
DEFINE_PRIM(_VOID, btKinematicCharacterController_setVelocityForTimeInterval2, _IDL _IDL _F32);

HL_PRIM void HL_NAME(btKinematicCharacterController_warp1)(_ref(btKinematicCharacterController)* _this, _ref(btVector3)* origin) {
	_unref(_this)->warp(*_unref(origin));
}
DEFINE_PRIM(_VOID, btKinematicCharacterController_warp1, _IDL _IDL);

HL_PRIM void HL_NAME(btKinematicCharacterController_preStep1)(_ref(btKinematicCharacterController)* _this, _ref(btCollisionWorld)* collisionWorld) {
	_unref(_this)->preStep(_unref(collisionWorld));
}
DEFINE_PRIM(_VOID, btKinematicCharacterController_preStep1, _IDL _IDL);

HL_PRIM void HL_NAME(btKinematicCharacterController_playerStep2)(_ref(btKinematicCharacterController)* _this, _ref(btCollisionWorld)* collisionWorld, float dt) {
	_unref(_this)->playerStep(_unref(collisionWorld), dt);
}
DEFINE_PRIM(_VOID, btKinematicCharacterController_playerStep2, _IDL _IDL _F32);

HL_PRIM void HL_NAME(btKinematicCharacterController_setFallSpeed1)(_ref(btKinematicCharacterController)* _this, float fallSpeed) {
	_unref(_this)->setFallSpeed(fallSpeed);
}
DEFINE_PRIM(_VOID, btKinematicCharacterController_setFallSpeed1, _IDL _F32);

HL_PRIM void HL_NAME(btKinematicCharacterController_setJumpSpeed1)(_ref(btKinematicCharacterController)* _this, float jumpSpeed) {
	_unref(_this)->setJumpSpeed(jumpSpeed);
}
DEFINE_PRIM(_VOID, btKinematicCharacterController_setJumpSpeed1, _IDL _F32);

HL_PRIM void HL_NAME(btKinematicCharacterController_setMaxJumpHeight1)(_ref(btKinematicCharacterController)* _this, float maxJumpHeight) {
	_unref(_this)->setMaxJumpHeight(maxJumpHeight);
}
DEFINE_PRIM(_VOID, btKinematicCharacterController_setMaxJumpHeight1, _IDL _F32);

HL_PRIM bool HL_NAME(btKinematicCharacterController_canJump0)(_ref(btKinematicCharacterController)* _this) {
	return _unref(_this)->canJump();
}
DEFINE_PRIM(_BOOL, btKinematicCharacterController_canJump0, _IDL);

HL_PRIM void HL_NAME(btKinematicCharacterController_jump0)(_ref(btKinematicCharacterController)* _this) {
	_unref(_this)->jump();
}
DEFINE_PRIM(_VOID, btKinematicCharacterController_jump0, _IDL);

HL_PRIM void HL_NAME(btKinematicCharacterController_setGravity1)(_ref(btKinematicCharacterController)* _this, _ref(btVector3)* gravity) {
	_unref(_this)->setGravity(*_unref(gravity));
}
DEFINE_PRIM(_VOID, btKinematicCharacterController_setGravity1, _IDL _IDL);

HL_PRIM _ref(btVector3)* HL_NAME(btKinematicCharacterController_getGravity0)(_ref(btKinematicCharacterController)* _this) {
	return alloc_ref(new btVector3(_unref(_this)->getGravity()),btVector3);
}
DEFINE_PRIM(_IDL, btKinematicCharacterController_getGravity0, _IDL);

HL_PRIM void HL_NAME(btKinematicCharacterController_setMaxSlope1)(_ref(btKinematicCharacterController)* _this, float slopeRadians) {
	_unref(_this)->setMaxSlope(slopeRadians);
}
DEFINE_PRIM(_VOID, btKinematicCharacterController_setMaxSlope1, _IDL _F32);

HL_PRIM float HL_NAME(btKinematicCharacterController_getMaxSlope0)(_ref(btKinematicCharacterController)* _this) {
	return _unref(_this)->getMaxSlope();
}
DEFINE_PRIM(_F32, btKinematicCharacterController_getMaxSlope0, _IDL);

HL_PRIM _ref(btPairCachingGhostObject)* HL_NAME(btKinematicCharacterController_getGhostObject0)(_ref(btKinematicCharacterController)* _this) {
	return alloc_ref((_unref(_this)->getGhostObject()),btPairCachingGhostObject);
}
DEFINE_PRIM(_IDL, btKinematicCharacterController_getGhostObject0, _IDL);

HL_PRIM void HL_NAME(btKinematicCharacterController_setUseGhostSweepTest1)(_ref(btKinematicCharacterController)* _this, bool useGhostObjectSweepTest) {
	_unref(_this)->setUseGhostSweepTest(useGhostObjectSweepTest);
}
DEFINE_PRIM(_VOID, btKinematicCharacterController_setUseGhostSweepTest1, _IDL _BOOL);

HL_PRIM bool HL_NAME(btKinematicCharacterController_onGround0)(_ref(btKinematicCharacterController)* _this) {
	return _unref(_this)->onGround();
}
DEFINE_PRIM(_BOOL, btKinematicCharacterController_onGround0, _IDL);

HL_PRIM _ref(btRaycastVehicle)* HL_NAME(btRaycastVehicle_new3)(_ref(btRaycastVehicle::btVehicleTuning)* tuning, _ref(btRigidBody)* chassis, _ref(btVehicleRaycaster)* raycaster) {
	return alloc_ref((new btRaycastVehicle(*_unref(tuning), _unref(chassis), _unref(raycaster))),btRaycastVehicle);
}
DEFINE_PRIM(_IDL, btRaycastVehicle_new3, _IDL _IDL _IDL);

HL_PRIM void HL_NAME(btRaycastVehicle_applyEngineForce2)(_ref(btRaycastVehicle)* _this, float force, int wheel) {
	_unref(_this)->applyEngineForce(force, wheel);
}
DEFINE_PRIM(_VOID, btRaycastVehicle_applyEngineForce2, _IDL _F32 _I32);

HL_PRIM void HL_NAME(btRaycastVehicle_setSteeringValue2)(_ref(btRaycastVehicle)* _this, float steering, int wheel) {
	_unref(_this)->setSteeringValue(steering, wheel);
}
DEFINE_PRIM(_VOID, btRaycastVehicle_setSteeringValue2, _IDL _F32 _I32);

HL_PRIM HL_CONST _ref(btTransform)* HL_NAME(btRaycastVehicle_getWheelTransformWS1)(_ref(btRaycastVehicle)* _this, int wheelIndex) {
	return alloc_ref(new btTransform(_unref(_this)->getWheelTransformWS(wheelIndex)),btTransform);
}
DEFINE_PRIM(_IDL, btRaycastVehicle_getWheelTransformWS1, _IDL _I32);

HL_PRIM void HL_NAME(btRaycastVehicle_updateWheelTransform2)(_ref(btRaycastVehicle)* _this, int wheelIndex, bool interpolatedTransform) {
	_unref(_this)->updateWheelTransform(wheelIndex, interpolatedTransform);
}
DEFINE_PRIM(_VOID, btRaycastVehicle_updateWheelTransform2, _IDL _I32 _BOOL);

HL_PRIM _ref(btWheelInfo)* HL_NAME(btRaycastVehicle_addWheel7)(_ref(btRaycastVehicle)* _this, _ref(btVector3)* connectionPointCS0, _ref(btVector3)* wheelDirectionCS0, _ref(btVector3)* wheelAxleCS, float suspensionRestLength, float wheelRadius, _ref(btRaycastVehicle::btVehicleTuning)* tuning, bool isFrontWheel) {
	return alloc_ref(new btWheelInfo(_unref(_this)->addWheel(*_unref(connectionPointCS0), *_unref(wheelDirectionCS0), *_unref(wheelAxleCS), suspensionRestLength, wheelRadius, *_unref(tuning), isFrontWheel)),btWheelInfo);
}
DEFINE_PRIM(_IDL, btRaycastVehicle_addWheel7, _IDL _IDL _IDL _IDL _F32 _F32 _IDL _BOOL);

HL_PRIM int HL_NAME(btRaycastVehicle_getNumWheels0)(_ref(btRaycastVehicle)* _this) {
	return _unref(_this)->getNumWheels();
}
DEFINE_PRIM(_I32, btRaycastVehicle_getNumWheels0, _IDL);

HL_PRIM _ref(btRigidBody)* HL_NAME(btRaycastVehicle_getRigidBody0)(_ref(btRaycastVehicle)* _this) {
	return alloc_ref((_unref(_this)->getRigidBody()),btRigidBody);
}
DEFINE_PRIM(_IDL, btRaycastVehicle_getRigidBody0, _IDL);

HL_PRIM _ref(btWheelInfo)* HL_NAME(btRaycastVehicle_getWheelInfo1)(_ref(btRaycastVehicle)* _this, int index) {
	return alloc_ref(new btWheelInfo(_unref(_this)->getWheelInfo(index)),btWheelInfo);
}
DEFINE_PRIM(_IDL, btRaycastVehicle_getWheelInfo1, _IDL _I32);

HL_PRIM void HL_NAME(btRaycastVehicle_setBrake2)(_ref(btRaycastVehicle)* _this, float brake, int wheelIndex) {
	_unref(_this)->setBrake(brake, wheelIndex);
}
DEFINE_PRIM(_VOID, btRaycastVehicle_setBrake2, _IDL _F32 _I32);

HL_PRIM void HL_NAME(btRaycastVehicle_setCoordinateSystem3)(_ref(btRaycastVehicle)* _this, int rightIndex, int upIndex, int forwardIndex) {
	_unref(_this)->setCoordinateSystem(rightIndex, upIndex, forwardIndex);
}
DEFINE_PRIM(_VOID, btRaycastVehicle_setCoordinateSystem3, _IDL _I32 _I32 _I32);

HL_PRIM float HL_NAME(btRaycastVehicle_getCurrentSpeedKmHour0)(_ref(btRaycastVehicle)* _this) {
	return _unref(_this)->getCurrentSpeedKmHour();
}
DEFINE_PRIM(_F32, btRaycastVehicle_getCurrentSpeedKmHour0, _IDL);

HL_PRIM HL_CONST _ref(btTransform)* HL_NAME(btRaycastVehicle_getChassisWorldTransform0)(_ref(btRaycastVehicle)* _this) {
	return alloc_ref(new btTransform(_unref(_this)->getChassisWorldTransform()),btTransform);
}
DEFINE_PRIM(_IDL, btRaycastVehicle_getChassisWorldTransform0, _IDL);

HL_PRIM float HL_NAME(btRaycastVehicle_rayCast1)(_ref(btRaycastVehicle)* _this, _ref(btWheelInfo)* wheel) {
	return _unref(_this)->rayCast(*_unref(wheel));
}
DEFINE_PRIM(_F32, btRaycastVehicle_rayCast1, _IDL _IDL);

HL_PRIM void HL_NAME(btRaycastVehicle_updateVehicle1)(_ref(btRaycastVehicle)* _this, float step) {
	_unref(_this)->updateVehicle(step);
}
DEFINE_PRIM(_VOID, btRaycastVehicle_updateVehicle1, _IDL _F32);

HL_PRIM void HL_NAME(btRaycastVehicle_resetSuspension0)(_ref(btRaycastVehicle)* _this) {
	_unref(_this)->resetSuspension();
}
DEFINE_PRIM(_VOID, btRaycastVehicle_resetSuspension0, _IDL);

HL_PRIM float HL_NAME(btRaycastVehicle_getSteeringValue1)(_ref(btRaycastVehicle)* _this, int wheel) {
	return _unref(_this)->getSteeringValue(wheel);
}
DEFINE_PRIM(_F32, btRaycastVehicle_getSteeringValue1, _IDL _I32);

HL_PRIM void HL_NAME(btRaycastVehicle_updateWheelTransformsWS2)(_ref(btRaycastVehicle)* _this, _ref(btWheelInfo)* wheel, _OPT(bool) interpolatedTransform) {
	if( !interpolatedTransform )
		_unref(_this)->updateWheelTransformsWS(*_unref(wheel));
	else
		_unref(_this)->updateWheelTransformsWS(*_unref(wheel), _GET_OPT(interpolatedTransform,b));
}
DEFINE_PRIM(_VOID, btRaycastVehicle_updateWheelTransformsWS2, _IDL _IDL _NULL(_BOOL));

HL_PRIM void HL_NAME(btRaycastVehicle_setPitchControl1)(_ref(btRaycastVehicle)* _this, float pitch) {
	_unref(_this)->setPitchControl(pitch);
}
DEFINE_PRIM(_VOID, btRaycastVehicle_setPitchControl1, _IDL _F32);

HL_PRIM void HL_NAME(btRaycastVehicle_updateSuspension1)(_ref(btRaycastVehicle)* _this, float deltaTime) {
	_unref(_this)->updateSuspension(deltaTime);
}
DEFINE_PRIM(_VOID, btRaycastVehicle_updateSuspension1, _IDL _F32);

HL_PRIM void HL_NAME(btRaycastVehicle_updateFriction1)(_ref(btRaycastVehicle)* _this, float timeStep) {
	_unref(_this)->updateFriction(timeStep);
}
DEFINE_PRIM(_VOID, btRaycastVehicle_updateFriction1, _IDL _F32);

HL_PRIM int HL_NAME(btRaycastVehicle_getRightAxis0)(_ref(btRaycastVehicle)* _this) {
	return _unref(_this)->getRightAxis();
}
DEFINE_PRIM(_I32, btRaycastVehicle_getRightAxis0, _IDL);

HL_PRIM int HL_NAME(btRaycastVehicle_getUpAxis0)(_ref(btRaycastVehicle)* _this) {
	return _unref(_this)->getUpAxis();
}
DEFINE_PRIM(_I32, btRaycastVehicle_getUpAxis0, _IDL);

HL_PRIM int HL_NAME(btRaycastVehicle_getForwardAxis0)(_ref(btRaycastVehicle)* _this) {
	return _unref(_this)->getForwardAxis();
}
DEFINE_PRIM(_I32, btRaycastVehicle_getForwardAxis0, _IDL);

HL_PRIM _ref(btVector3)* HL_NAME(btRaycastVehicle_getForwardVector0)(_ref(btRaycastVehicle)* _this) {
	return alloc_ref(new btVector3(_unref(_this)->getForwardVector()),btVector3);
}
DEFINE_PRIM(_IDL, btRaycastVehicle_getForwardVector0, _IDL);

HL_PRIM int HL_NAME(btRaycastVehicle_getUserConstraintType0)(_ref(btRaycastVehicle)* _this) {
	return _unref(_this)->getUserConstraintType();
}
DEFINE_PRIM(_I32, btRaycastVehicle_getUserConstraintType0, _IDL);

HL_PRIM void HL_NAME(btRaycastVehicle_setUserConstraintType1)(_ref(btRaycastVehicle)* _this, int userConstraintType) {
	_unref(_this)->setUserConstraintType(userConstraintType);
}
DEFINE_PRIM(_VOID, btRaycastVehicle_setUserConstraintType1, _IDL _I32);

HL_PRIM void HL_NAME(btRaycastVehicle_setUserConstraintId1)(_ref(btRaycastVehicle)* _this, int uid) {
	_unref(_this)->setUserConstraintId(uid);
}
DEFINE_PRIM(_VOID, btRaycastVehicle_setUserConstraintId1, _IDL _I32);

HL_PRIM int HL_NAME(btRaycastVehicle_getUserConstraintId0)(_ref(btRaycastVehicle)* _this) {
	return _unref(_this)->getUserConstraintId();
}
DEFINE_PRIM(_I32, btRaycastVehicle_getUserConstraintId0, _IDL);

HL_PRIM _ref(btGhostObject)* HL_NAME(btGhostObject_new0)() {
	return alloc_ref((new btGhostObject()),btGhostObject);
}
DEFINE_PRIM(_IDL, btGhostObject_new0,);

HL_PRIM int HL_NAME(btGhostObject_getNumOverlappingObjects0)(_ref(btGhostObject)* _this) {
	return _unref(_this)->getNumOverlappingObjects();
}
DEFINE_PRIM(_I32, btGhostObject_getNumOverlappingObjects0, _IDL);

HL_PRIM _ref(btCollisionObject)* HL_NAME(btGhostObject_getOverlappingObject1)(_ref(btGhostObject)* _this, int index) {
	return alloc_ref((_unref(_this)->getOverlappingObject(index)),btCollisionObject);
}
DEFINE_PRIM(_IDL, btGhostObject_getOverlappingObject1, _IDL _I32);

HL_PRIM _ref(btPairCachingGhostObject)* HL_NAME(btPairCachingGhostObject_new0)() {
	return alloc_ref((new btPairCachingGhostObject()),btPairCachingGhostObject);
}
DEFINE_PRIM(_IDL, btPairCachingGhostObject_new0,);

HL_PRIM _ref(btGhostPairCallback)* HL_NAME(btGhostPairCallback_new0)() {
	return alloc_ref((new btGhostPairCallback()),btGhostPairCallback);
}
DEFINE_PRIM(_IDL, btGhostPairCallback_new0,);

HL_PRIM _ref(btSoftBodyWorldInfo)* HL_NAME(btSoftBodyWorldInfo_new0)() {
	return alloc_ref((new btSoftBodyWorldInfo()),btSoftBodyWorldInfo);
}
DEFINE_PRIM(_IDL, btSoftBodyWorldInfo_new0,);

HL_PRIM float HL_NAME(btSoftBodyWorldInfo_get_air_density)( _ref(btSoftBodyWorldInfo)* _this ) {
	return _unref(_this)->air_density;
}
HL_PRIM float HL_NAME(btSoftBodyWorldInfo_set_air_density)( _ref(btSoftBodyWorldInfo)* _this, float value ) {
	_unref(_this)->air_density = (value);
	return value;
}
DEFINE_PRIM(_F32,btSoftBodyWorldInfo_get_air_density,_IDL);
DEFINE_PRIM(_F32,btSoftBodyWorldInfo_set_air_density,_IDL _F32);

HL_PRIM float HL_NAME(btSoftBodyWorldInfo_get_water_density)( _ref(btSoftBodyWorldInfo)* _this ) {
	return _unref(_this)->water_density;
}
HL_PRIM float HL_NAME(btSoftBodyWorldInfo_set_water_density)( _ref(btSoftBodyWorldInfo)* _this, float value ) {
	_unref(_this)->water_density = (value);
	return value;
}
DEFINE_PRIM(_F32,btSoftBodyWorldInfo_get_water_density,_IDL);
DEFINE_PRIM(_F32,btSoftBodyWorldInfo_set_water_density,_IDL _F32);

HL_PRIM float HL_NAME(btSoftBodyWorldInfo_get_water_offset)( _ref(btSoftBodyWorldInfo)* _this ) {
	return _unref(_this)->water_offset;
}
HL_PRIM float HL_NAME(btSoftBodyWorldInfo_set_water_offset)( _ref(btSoftBodyWorldInfo)* _this, float value ) {
	_unref(_this)->water_offset = (value);
	return value;
}
DEFINE_PRIM(_F32,btSoftBodyWorldInfo_get_water_offset,_IDL);
DEFINE_PRIM(_F32,btSoftBodyWorldInfo_set_water_offset,_IDL _F32);

HL_PRIM float HL_NAME(btSoftBodyWorldInfo_get_m_maxDisplacement)( _ref(btSoftBodyWorldInfo)* _this ) {
	return _unref(_this)->m_maxDisplacement;
}
HL_PRIM float HL_NAME(btSoftBodyWorldInfo_set_m_maxDisplacement)( _ref(btSoftBodyWorldInfo)* _this, float value ) {
	_unref(_this)->m_maxDisplacement = (value);
	return value;
}
DEFINE_PRIM(_F32,btSoftBodyWorldInfo_get_m_maxDisplacement,_IDL);
DEFINE_PRIM(_F32,btSoftBodyWorldInfo_set_m_maxDisplacement,_IDL _F32);

HL_PRIM _ref(btVector3)* HL_NAME(btSoftBodyWorldInfo_get_water_normal)( _ref(btSoftBodyWorldInfo)* _this ) {
	return alloc_ref(new btVector3(_unref(_this)->water_normal),btVector3);
}
HL_PRIM _ref(btVector3)* HL_NAME(btSoftBodyWorldInfo_set_water_normal)( _ref(btSoftBodyWorldInfo)* _this, _ref(btVector3)* value ) {
	_unref(_this)->water_normal = *_unref(value);
	return value;
}
DEFINE_PRIM(_IDL,btSoftBodyWorldInfo_get_water_normal,_IDL);
DEFINE_PRIM(_IDL,btSoftBodyWorldInfo_set_water_normal,_IDL _IDL);

HL_PRIM _ref(btBroadphaseInterface)* HL_NAME(btSoftBodyWorldInfo_get_m_broadphase)( _ref(btSoftBodyWorldInfo)* _this ) {
	return alloc_ref(_unref(_this)->m_broadphase,btBroadphaseInterface);
}
HL_PRIM _ref(btBroadphaseInterface)* HL_NAME(btSoftBodyWorldInfo_set_m_broadphase)( _ref(btSoftBodyWorldInfo)* _this, _ref(btBroadphaseInterface)* value ) {
	_unref(_this)->m_broadphase = _unref(value);
	return value;
}
DEFINE_PRIM(_IDL,btSoftBodyWorldInfo_get_m_broadphase,_IDL);
DEFINE_PRIM(_IDL,btSoftBodyWorldInfo_set_m_broadphase,_IDL _IDL);

HL_PRIM _ref(btDispatcher)* HL_NAME(btSoftBodyWorldInfo_get_m_dispatcher)( _ref(btSoftBodyWorldInfo)* _this ) {
	return alloc_ref(_unref(_this)->m_dispatcher,btDispatcher);
}
HL_PRIM _ref(btDispatcher)* HL_NAME(btSoftBodyWorldInfo_set_m_dispatcher)( _ref(btSoftBodyWorldInfo)* _this, _ref(btDispatcher)* value ) {
	_unref(_this)->m_dispatcher = _unref(value);
	return value;
}
DEFINE_PRIM(_IDL,btSoftBodyWorldInfo_get_m_dispatcher,_IDL);
DEFINE_PRIM(_IDL,btSoftBodyWorldInfo_set_m_dispatcher,_IDL _IDL);

HL_PRIM _ref(btVector3)* HL_NAME(btSoftBodyWorldInfo_get_m_gravity)( _ref(btSoftBodyWorldInfo)* _this ) {
	return alloc_ref(new btVector3(_unref(_this)->m_gravity),btVector3);
}
HL_PRIM _ref(btVector3)* HL_NAME(btSoftBodyWorldInfo_set_m_gravity)( _ref(btSoftBodyWorldInfo)* _this, _ref(btVector3)* value ) {
	_unref(_this)->m_gravity = *_unref(value);
	return value;
}
DEFINE_PRIM(_IDL,btSoftBodyWorldInfo_get_m_gravity,_IDL);
DEFINE_PRIM(_IDL,btSoftBodyWorldInfo_set_m_gravity,_IDL _IDL);

HL_PRIM _ref(btVector3)* HL_NAME(Node_get_m_x)( _ref(btSoftBody::Node)* _this ) {
	return alloc_ref(new btVector3(_unref(_this)->m_x),btVector3);
}
HL_PRIM _ref(btVector3)* HL_NAME(Node_set_m_x)( _ref(btSoftBody::Node)* _this, _ref(btVector3)* value ) {
	_unref(_this)->m_x = *_unref(value);
	return value;
}
DEFINE_PRIM(_IDL,Node_get_m_x,_IDL);
DEFINE_PRIM(_IDL,Node_set_m_x,_IDL _IDL);

HL_PRIM _ref(btVector3)* HL_NAME(Node_get_m_n)( _ref(btSoftBody::Node)* _this ) {
	return alloc_ref(new btVector3(_unref(_this)->m_n),btVector3);
}
HL_PRIM _ref(btVector3)* HL_NAME(Node_set_m_n)( _ref(btSoftBody::Node)* _this, _ref(btVector3)* value ) {
	_unref(_this)->m_n = *_unref(value);
	return value;
}
DEFINE_PRIM(_IDL,Node_get_m_n,_IDL);
DEFINE_PRIM(_IDL,Node_set_m_n,_IDL _IDL);

HL_PRIM HL_CONST int HL_NAME(tNodeArray_size0)(_ref(btSoftBody::tNodeArray)* _this) {
	return _unref(_this)->size();
}
DEFINE_PRIM(_I32, tNodeArray_size0, _IDL);

HL_PRIM HL_CONST _ref(btSoftBody::Node)* HL_NAME(tNodeArray_at1)(_ref(btSoftBody::tNodeArray)* _this, int n) {
	return alloc_ref(new btSoftBody::Node(_unref(_this)->at(n)),Node);
}
DEFINE_PRIM(_IDL, tNodeArray_at1, _IDL _I32);

HL_PRIM float HL_NAME(Material_get_m_kLST)( _ref(btSoftBody::Material)* _this ) {
	return _unref(_this)->m_kLST;
}
HL_PRIM float HL_NAME(Material_set_m_kLST)( _ref(btSoftBody::Material)* _this, float value ) {
	_unref(_this)->m_kLST = (value);
	return value;
}
DEFINE_PRIM(_F32,Material_get_m_kLST,_IDL);
DEFINE_PRIM(_F32,Material_set_m_kLST,_IDL _F32);

HL_PRIM float HL_NAME(Material_get_m_kAST)( _ref(btSoftBody::Material)* _this ) {
	return _unref(_this)->m_kAST;
}
HL_PRIM float HL_NAME(Material_set_m_kAST)( _ref(btSoftBody::Material)* _this, float value ) {
	_unref(_this)->m_kAST = (value);
	return value;
}
DEFINE_PRIM(_F32,Material_get_m_kAST,_IDL);
DEFINE_PRIM(_F32,Material_set_m_kAST,_IDL _F32);

HL_PRIM float HL_NAME(Material_get_m_kVST)( _ref(btSoftBody::Material)* _this ) {
	return _unref(_this)->m_kVST;
}
HL_PRIM float HL_NAME(Material_set_m_kVST)( _ref(btSoftBody::Material)* _this, float value ) {
	_unref(_this)->m_kVST = (value);
	return value;
}
DEFINE_PRIM(_F32,Material_get_m_kVST,_IDL);
DEFINE_PRIM(_F32,Material_set_m_kVST,_IDL _F32);

HL_PRIM int HL_NAME(Material_get_m_flags)( _ref(btSoftBody::Material)* _this ) {
	return _unref(_this)->m_flags;
}
HL_PRIM int HL_NAME(Material_set_m_flags)( _ref(btSoftBody::Material)* _this, int value ) {
	_unref(_this)->m_flags = (value);
	return value;
}
DEFINE_PRIM(_I32,Material_get_m_flags,_IDL);
DEFINE_PRIM(_I32,Material_set_m_flags,_IDL _I32);

HL_PRIM HL_CONST int HL_NAME(tMaterialArray_size0)(_ref(btSoftBody::tMaterialArray)* _this) {
	return _unref(_this)->size();
}
DEFINE_PRIM(_I32, tMaterialArray_size0, _IDL);

HL_PRIM _ref(btSoftBody::Material)* HL_NAME(tMaterialArray_at1)(_ref(btSoftBody::tMaterialArray)* _this, int n) {
	return alloc_ref((_unref(_this)->at(n)),Material);
}
DEFINE_PRIM(_IDL, tMaterialArray_at1, _IDL _I32);

HL_PRIM float HL_NAME(Config_get_kVCF)( _ref(btSoftBody::Config)* _this ) {
	return _unref(_this)->kVCF;
}
HL_PRIM float HL_NAME(Config_set_kVCF)( _ref(btSoftBody::Config)* _this, float value ) {
	_unref(_this)->kVCF = (value);
	return value;
}
DEFINE_PRIM(_F32,Config_get_kVCF,_IDL);
DEFINE_PRIM(_F32,Config_set_kVCF,_IDL _F32);

HL_PRIM float HL_NAME(Config_get_kDP)( _ref(btSoftBody::Config)* _this ) {
	return _unref(_this)->kDP;
}
HL_PRIM float HL_NAME(Config_set_kDP)( _ref(btSoftBody::Config)* _this, float value ) {
	_unref(_this)->kDP = (value);
	return value;
}
DEFINE_PRIM(_F32,Config_get_kDP,_IDL);
DEFINE_PRIM(_F32,Config_set_kDP,_IDL _F32);

HL_PRIM float HL_NAME(Config_get_kDG)( _ref(btSoftBody::Config)* _this ) {
	return _unref(_this)->kDG;
}
HL_PRIM float HL_NAME(Config_set_kDG)( _ref(btSoftBody::Config)* _this, float value ) {
	_unref(_this)->kDG = (value);
	return value;
}
DEFINE_PRIM(_F32,Config_get_kDG,_IDL);
DEFINE_PRIM(_F32,Config_set_kDG,_IDL _F32);

HL_PRIM float HL_NAME(Config_get_kLF)( _ref(btSoftBody::Config)* _this ) {
	return _unref(_this)->kLF;
}
HL_PRIM float HL_NAME(Config_set_kLF)( _ref(btSoftBody::Config)* _this, float value ) {
	_unref(_this)->kLF = (value);
	return value;
}
DEFINE_PRIM(_F32,Config_get_kLF,_IDL);
DEFINE_PRIM(_F32,Config_set_kLF,_IDL _F32);

HL_PRIM float HL_NAME(Config_get_kPR)( _ref(btSoftBody::Config)* _this ) {
	return _unref(_this)->kPR;
}
HL_PRIM float HL_NAME(Config_set_kPR)( _ref(btSoftBody::Config)* _this, float value ) {
	_unref(_this)->kPR = (value);
	return value;
}
DEFINE_PRIM(_F32,Config_get_kPR,_IDL);
DEFINE_PRIM(_F32,Config_set_kPR,_IDL _F32);

HL_PRIM float HL_NAME(Config_get_kVC)( _ref(btSoftBody::Config)* _this ) {
	return _unref(_this)->kVC;
}
HL_PRIM float HL_NAME(Config_set_kVC)( _ref(btSoftBody::Config)* _this, float value ) {
	_unref(_this)->kVC = (value);
	return value;
}
DEFINE_PRIM(_F32,Config_get_kVC,_IDL);
DEFINE_PRIM(_F32,Config_set_kVC,_IDL _F32);

HL_PRIM float HL_NAME(Config_get_kDF)( _ref(btSoftBody::Config)* _this ) {
	return _unref(_this)->kDF;
}
HL_PRIM float HL_NAME(Config_set_kDF)( _ref(btSoftBody::Config)* _this, float value ) {
	_unref(_this)->kDF = (value);
	return value;
}
DEFINE_PRIM(_F32,Config_get_kDF,_IDL);
DEFINE_PRIM(_F32,Config_set_kDF,_IDL _F32);

HL_PRIM float HL_NAME(Config_get_kMT)( _ref(btSoftBody::Config)* _this ) {
	return _unref(_this)->kMT;
}
HL_PRIM float HL_NAME(Config_set_kMT)( _ref(btSoftBody::Config)* _this, float value ) {
	_unref(_this)->kMT = (value);
	return value;
}
DEFINE_PRIM(_F32,Config_get_kMT,_IDL);
DEFINE_PRIM(_F32,Config_set_kMT,_IDL _F32);

HL_PRIM float HL_NAME(Config_get_kCHR)( _ref(btSoftBody::Config)* _this ) {
	return _unref(_this)->kCHR;
}
HL_PRIM float HL_NAME(Config_set_kCHR)( _ref(btSoftBody::Config)* _this, float value ) {
	_unref(_this)->kCHR = (value);
	return value;
}
DEFINE_PRIM(_F32,Config_get_kCHR,_IDL);
DEFINE_PRIM(_F32,Config_set_kCHR,_IDL _F32);

HL_PRIM float HL_NAME(Config_get_kKHR)( _ref(btSoftBody::Config)* _this ) {
	return _unref(_this)->kKHR;
}
HL_PRIM float HL_NAME(Config_set_kKHR)( _ref(btSoftBody::Config)* _this, float value ) {
	_unref(_this)->kKHR = (value);
	return value;
}
DEFINE_PRIM(_F32,Config_get_kKHR,_IDL);
DEFINE_PRIM(_F32,Config_set_kKHR,_IDL _F32);

HL_PRIM float HL_NAME(Config_get_kSHR)( _ref(btSoftBody::Config)* _this ) {
	return _unref(_this)->kSHR;
}
HL_PRIM float HL_NAME(Config_set_kSHR)( _ref(btSoftBody::Config)* _this, float value ) {
	_unref(_this)->kSHR = (value);
	return value;
}
DEFINE_PRIM(_F32,Config_get_kSHR,_IDL);
DEFINE_PRIM(_F32,Config_set_kSHR,_IDL _F32);

HL_PRIM float HL_NAME(Config_get_kAHR)( _ref(btSoftBody::Config)* _this ) {
	return _unref(_this)->kAHR;
}
HL_PRIM float HL_NAME(Config_set_kAHR)( _ref(btSoftBody::Config)* _this, float value ) {
	_unref(_this)->kAHR = (value);
	return value;
}
DEFINE_PRIM(_F32,Config_get_kAHR,_IDL);
DEFINE_PRIM(_F32,Config_set_kAHR,_IDL _F32);

HL_PRIM float HL_NAME(Config_get_kSRHR_CL)( _ref(btSoftBody::Config)* _this ) {
	return _unref(_this)->kSRHR_CL;
}
HL_PRIM float HL_NAME(Config_set_kSRHR_CL)( _ref(btSoftBody::Config)* _this, float value ) {
	_unref(_this)->kSRHR_CL = (value);
	return value;
}
DEFINE_PRIM(_F32,Config_get_kSRHR_CL,_IDL);
DEFINE_PRIM(_F32,Config_set_kSRHR_CL,_IDL _F32);

HL_PRIM float HL_NAME(Config_get_kSKHR_CL)( _ref(btSoftBody::Config)* _this ) {
	return _unref(_this)->kSKHR_CL;
}
HL_PRIM float HL_NAME(Config_set_kSKHR_CL)( _ref(btSoftBody::Config)* _this, float value ) {
	_unref(_this)->kSKHR_CL = (value);
	return value;
}
DEFINE_PRIM(_F32,Config_get_kSKHR_CL,_IDL);
DEFINE_PRIM(_F32,Config_set_kSKHR_CL,_IDL _F32);

HL_PRIM float HL_NAME(Config_get_kSSHR_CL)( _ref(btSoftBody::Config)* _this ) {
	return _unref(_this)->kSSHR_CL;
}
HL_PRIM float HL_NAME(Config_set_kSSHR_CL)( _ref(btSoftBody::Config)* _this, float value ) {
	_unref(_this)->kSSHR_CL = (value);
	return value;
}
DEFINE_PRIM(_F32,Config_get_kSSHR_CL,_IDL);
DEFINE_PRIM(_F32,Config_set_kSSHR_CL,_IDL _F32);

HL_PRIM float HL_NAME(Config_get_kSR_SPLT_CL)( _ref(btSoftBody::Config)* _this ) {
	return _unref(_this)->kSR_SPLT_CL;
}
HL_PRIM float HL_NAME(Config_set_kSR_SPLT_CL)( _ref(btSoftBody::Config)* _this, float value ) {
	_unref(_this)->kSR_SPLT_CL = (value);
	return value;
}
DEFINE_PRIM(_F32,Config_get_kSR_SPLT_CL,_IDL);
DEFINE_PRIM(_F32,Config_set_kSR_SPLT_CL,_IDL _F32);

HL_PRIM float HL_NAME(Config_get_kSK_SPLT_CL)( _ref(btSoftBody::Config)* _this ) {
	return _unref(_this)->kSK_SPLT_CL;
}
HL_PRIM float HL_NAME(Config_set_kSK_SPLT_CL)( _ref(btSoftBody::Config)* _this, float value ) {
	_unref(_this)->kSK_SPLT_CL = (value);
	return value;
}
DEFINE_PRIM(_F32,Config_get_kSK_SPLT_CL,_IDL);
DEFINE_PRIM(_F32,Config_set_kSK_SPLT_CL,_IDL _F32);

HL_PRIM float HL_NAME(Config_get_kSS_SPLT_CL)( _ref(btSoftBody::Config)* _this ) {
	return _unref(_this)->kSS_SPLT_CL;
}
HL_PRIM float HL_NAME(Config_set_kSS_SPLT_CL)( _ref(btSoftBody::Config)* _this, float value ) {
	_unref(_this)->kSS_SPLT_CL = (value);
	return value;
}
DEFINE_PRIM(_F32,Config_get_kSS_SPLT_CL,_IDL);
DEFINE_PRIM(_F32,Config_set_kSS_SPLT_CL,_IDL _F32);

HL_PRIM float HL_NAME(Config_get_maxvolume)( _ref(btSoftBody::Config)* _this ) {
	return _unref(_this)->maxvolume;
}
HL_PRIM float HL_NAME(Config_set_maxvolume)( _ref(btSoftBody::Config)* _this, float value ) {
	_unref(_this)->maxvolume = (value);
	return value;
}
DEFINE_PRIM(_F32,Config_get_maxvolume,_IDL);
DEFINE_PRIM(_F32,Config_set_maxvolume,_IDL _F32);

HL_PRIM float HL_NAME(Config_get_timescale)( _ref(btSoftBody::Config)* _this ) {
	return _unref(_this)->timescale;
}
HL_PRIM float HL_NAME(Config_set_timescale)( _ref(btSoftBody::Config)* _this, float value ) {
	_unref(_this)->timescale = (value);
	return value;
}
DEFINE_PRIM(_F32,Config_get_timescale,_IDL);
DEFINE_PRIM(_F32,Config_set_timescale,_IDL _F32);

HL_PRIM int HL_NAME(Config_get_viterations)( _ref(btSoftBody::Config)* _this ) {
	return _unref(_this)->viterations;
}
HL_PRIM int HL_NAME(Config_set_viterations)( _ref(btSoftBody::Config)* _this, int value ) {
	_unref(_this)->viterations = (value);
	return value;
}
DEFINE_PRIM(_I32,Config_get_viterations,_IDL);
DEFINE_PRIM(_I32,Config_set_viterations,_IDL _I32);

HL_PRIM int HL_NAME(Config_get_piterations)( _ref(btSoftBody::Config)* _this ) {
	return _unref(_this)->piterations;
}
HL_PRIM int HL_NAME(Config_set_piterations)( _ref(btSoftBody::Config)* _this, int value ) {
	_unref(_this)->piterations = (value);
	return value;
}
DEFINE_PRIM(_I32,Config_get_piterations,_IDL);
DEFINE_PRIM(_I32,Config_set_piterations,_IDL _I32);

HL_PRIM int HL_NAME(Config_get_diterations)( _ref(btSoftBody::Config)* _this ) {
	return _unref(_this)->diterations;
}
HL_PRIM int HL_NAME(Config_set_diterations)( _ref(btSoftBody::Config)* _this, int value ) {
	_unref(_this)->diterations = (value);
	return value;
}
DEFINE_PRIM(_I32,Config_get_diterations,_IDL);
DEFINE_PRIM(_I32,Config_set_diterations,_IDL _I32);

HL_PRIM int HL_NAME(Config_get_citerations)( _ref(btSoftBody::Config)* _this ) {
	return _unref(_this)->citerations;
}
HL_PRIM int HL_NAME(Config_set_citerations)( _ref(btSoftBody::Config)* _this, int value ) {
	_unref(_this)->citerations = (value);
	return value;
}
DEFINE_PRIM(_I32,Config_get_citerations,_IDL);
DEFINE_PRIM(_I32,Config_set_citerations,_IDL _I32);

HL_PRIM int HL_NAME(Config_get_collisions)( _ref(btSoftBody::Config)* _this ) {
	return _unref(_this)->collisions;
}
HL_PRIM int HL_NAME(Config_set_collisions)( _ref(btSoftBody::Config)* _this, int value ) {
	_unref(_this)->collisions = (value);
	return value;
}
DEFINE_PRIM(_I32,Config_get_collisions,_IDL);
DEFINE_PRIM(_I32,Config_set_collisions,_IDL _I32);

HL_PRIM _ref(btSoftBody)* HL_NAME(btSoftBody_new4)(_ref(btSoftBodyWorldInfo)* worldInfo, int node_count, _ref(btVector3)* x, float* m) {
	return alloc_ref((new btSoftBody(_unref(worldInfo), node_count, _unref(x), m)),btSoftBody);
}
DEFINE_PRIM(_IDL, btSoftBody_new4, _IDL _I32 _IDL _BYTES);

HL_PRIM _ref(btSoftBody)* HL_NAME(btSoftBody_new1)(_ref(btSoftBodyWorldInfo)* worldInfo) {
	return alloc_ref((new btSoftBody(_unref(worldInfo))),btSoftBody);
}
DEFINE_PRIM(_IDL, btSoftBody_new1, _IDL);

HL_PRIM void HL_NAME(btSoftBody_updateBounds0)(_ref(btSoftBody)* _this) {
	_unref(_this)->updateBounds();
}
DEFINE_PRIM(_VOID, btSoftBody_updateBounds0, _IDL);

HL_PRIM _ref(btSoftBody::Config)* HL_NAME(btSoftBody_get_m_cfg)( _ref(btSoftBody)* _this ) {
	return alloc_ref(new btSoftBody::Config(_unref(_this)->m_cfg),Config);
}
HL_PRIM _ref(btSoftBody::Config)* HL_NAME(btSoftBody_set_m_cfg)( _ref(btSoftBody)* _this, _ref(btSoftBody::Config)* value ) {
	_unref(_this)->m_cfg = *_unref(value);
	return value;
}
DEFINE_PRIM(_IDL,btSoftBody_get_m_cfg,_IDL);
DEFINE_PRIM(_IDL,btSoftBody_set_m_cfg,_IDL _IDL);

HL_PRIM _ref(btSoftBody::tNodeArray)* HL_NAME(btSoftBody_get_m_nodes)( _ref(btSoftBody)* _this ) {
	return alloc_ref(new btSoftBody::tNodeArray(_unref(_this)->m_nodes),tNodeArray);
}
HL_PRIM _ref(btSoftBody::tNodeArray)* HL_NAME(btSoftBody_set_m_nodes)( _ref(btSoftBody)* _this, _ref(btSoftBody::tNodeArray)* value ) {
	_unref(_this)->m_nodes = *_unref(value);
	return value;
}
DEFINE_PRIM(_IDL,btSoftBody_get_m_nodes,_IDL);
DEFINE_PRIM(_IDL,btSoftBody_set_m_nodes,_IDL _IDL);

HL_PRIM _ref(btSoftBody::tMaterialArray)* HL_NAME(btSoftBody_get_m_materials)( _ref(btSoftBody)* _this ) {
	return alloc_ref(new btSoftBody::tMaterialArray(_unref(_this)->m_materials),tMaterialArray);
}
HL_PRIM _ref(btSoftBody::tMaterialArray)* HL_NAME(btSoftBody_set_m_materials)( _ref(btSoftBody)* _this, _ref(btSoftBody::tMaterialArray)* value ) {
	_unref(_this)->m_materials = *_unref(value);
	return value;
}
DEFINE_PRIM(_IDL,btSoftBody_get_m_materials,_IDL);
DEFINE_PRIM(_IDL,btSoftBody_set_m_materials,_IDL _IDL);

HL_PRIM HL_CONST bool HL_NAME(btSoftBody_checkLink2)(_ref(btSoftBody)* _this, int node0, int node1) {
	return _unref(_this)->checkLink(node0, node1);
}
DEFINE_PRIM(_BOOL, btSoftBody_checkLink2, _IDL _I32 _I32);

HL_PRIM HL_CONST bool HL_NAME(btSoftBody_checkFace3)(_ref(btSoftBody)* _this, int node0, int node1, int node2) {
	return _unref(_this)->checkFace(node0, node1, node2);
}
DEFINE_PRIM(_BOOL, btSoftBody_checkFace3, _IDL _I32 _I32 _I32);

HL_PRIM _ref(btSoftBody::Material)* HL_NAME(btSoftBody_appendMaterial0)(_ref(btSoftBody)* _this) {
	return alloc_ref((_unref(_this)->appendMaterial()),Material);
}
DEFINE_PRIM(_IDL, btSoftBody_appendMaterial0, _IDL);

HL_PRIM void HL_NAME(btSoftBody_appendNode2)(_ref(btSoftBody)* _this, _ref(btVector3)* x, float m) {
	_unref(_this)->appendNode(*_unref(x), m);
}
DEFINE_PRIM(_VOID, btSoftBody_appendNode2, _IDL _IDL _F32);

HL_PRIM void HL_NAME(btSoftBody_appendLink4)(_ref(btSoftBody)* _this, int node0, int node1, _ref(btSoftBody::Material)* mat, bool bcheckexist) {
	_unref(_this)->appendLink(node0, node1, _unref(mat), bcheckexist);
}
DEFINE_PRIM(_VOID, btSoftBody_appendLink4, _IDL _I32 _I32 _IDL _BOOL);

HL_PRIM void HL_NAME(btSoftBody_appendFace4)(_ref(btSoftBody)* _this, int node0, int node1, int node2, _ref(btSoftBody::Material)* mat) {
	_unref(_this)->appendFace(node0, node1, node2, _unref(mat));
}
DEFINE_PRIM(_VOID, btSoftBody_appendFace4, _IDL _I32 _I32 _I32 _IDL);

HL_PRIM void HL_NAME(btSoftBody_appendTetra5)(_ref(btSoftBody)* _this, int node0, int node1, int node2, int node3, _ref(btSoftBody::Material)* mat) {
	_unref(_this)->appendTetra(node0, node1, node2, node3, _unref(mat));
}
DEFINE_PRIM(_VOID, btSoftBody_appendTetra5, _IDL _I32 _I32 _I32 _I32 _IDL);

HL_PRIM void HL_NAME(btSoftBody_appendAnchor4)(_ref(btSoftBody)* _this, int node, _ref(btRigidBody)* body, bool disableCollisionBetweenLinkedBodies, float influence) {
	_unref(_this)->appendAnchor(node, _unref(body), disableCollisionBetweenLinkedBodies, influence);
}
DEFINE_PRIM(_VOID, btSoftBody_appendAnchor4, _IDL _I32 _IDL _BOOL _F32);

HL_PRIM HL_CONST float HL_NAME(btSoftBody_getTotalMass0)(_ref(btSoftBody)* _this) {
	return _unref(_this)->getTotalMass();
}
DEFINE_PRIM(_F32, btSoftBody_getTotalMass0, _IDL);

HL_PRIM void HL_NAME(btSoftBody_setTotalMass2)(_ref(btSoftBody)* _this, float mass, bool fromfaces) {
	_unref(_this)->setTotalMass(mass, fromfaces);
}
DEFINE_PRIM(_VOID, btSoftBody_setTotalMass2, _IDL _F32 _BOOL);

HL_PRIM void HL_NAME(btSoftBody_setMass2)(_ref(btSoftBody)* _this, int node, float mass) {
	_unref(_this)->setMass(node, mass);
}
DEFINE_PRIM(_VOID, btSoftBody_setMass2, _IDL _I32 _F32);

HL_PRIM void HL_NAME(btSoftBody_transform1)(_ref(btSoftBody)* _this, _ref(btTransform)* trs) {
	_unref(_this)->transform(*_unref(trs));
}
DEFINE_PRIM(_VOID, btSoftBody_transform1, _IDL _IDL);

HL_PRIM void HL_NAME(btSoftBody_translate1)(_ref(btSoftBody)* _this, _ref(btVector3)* trs) {
	_unref(_this)->translate(*_unref(trs));
}
DEFINE_PRIM(_VOID, btSoftBody_translate1, _IDL _IDL);

HL_PRIM void HL_NAME(btSoftBody_rotate1)(_ref(btSoftBody)* _this, _ref(btQuaternion)* rot) {
	_unref(_this)->rotate(*_unref(rot));
}
DEFINE_PRIM(_VOID, btSoftBody_rotate1, _IDL _IDL);

HL_PRIM void HL_NAME(btSoftBody_scale1)(_ref(btSoftBody)* _this, _ref(btVector3)* scl) {
	_unref(_this)->scale(*_unref(scl));
}
DEFINE_PRIM(_VOID, btSoftBody_scale1, _IDL _IDL);

HL_PRIM int HL_NAME(btSoftBody_generateClusters2)(_ref(btSoftBody)* _this, int k, _OPT(int) maxiterations) {
	if( !maxiterations )
		return _unref(_this)->generateClusters(k);
	else
		return _unref(_this)->generateClusters(k, _GET_OPT(maxiterations,i));
}
DEFINE_PRIM(_I32, btSoftBody_generateClusters2, _IDL _I32 _NULL(_I32));

HL_PRIM _ref(btSoftBody)* HL_NAME(btSoftBody_upcast1)(_ref(btSoftBody)* _this, _ref(btCollisionObject)* colObj) {
	return alloc_ref((_unref(_this)->upcast(_unref(colObj))),btSoftBody);
}
DEFINE_PRIM(_IDL, btSoftBody_upcast1, _IDL _IDL);

HL_PRIM _ref(btSoftBodyRigidBodyCollisionConfiguration)* HL_NAME(btSoftBodyRigidBodyCollisionConfiguration_new1)(_ref(btDefaultCollisionConstructionInfo)* info) {
	if( !info )
		return alloc_ref((new btSoftBodyRigidBodyCollisionConfiguration()),btSoftBodyRigidBodyCollisionConfiguration);
	else
		return alloc_ref((new btSoftBodyRigidBodyCollisionConfiguration(*_unref(info))),btSoftBodyRigidBodyCollisionConfiguration);
}
DEFINE_PRIM(_IDL, btSoftBodyRigidBodyCollisionConfiguration_new1, _IDL);

HL_PRIM _ref(btDefaultSoftBodySolver)* HL_NAME(btDefaultSoftBodySolver_new0)() {
	return alloc_ref((new btDefaultSoftBodySolver()),btDefaultSoftBodySolver);
}
DEFINE_PRIM(_IDL, btDefaultSoftBodySolver_new0,);

HL_PRIM HL_CONST int HL_NAME(btSoftBodyArray_size0)(_ref(btSoftBodyArray)* _this) {
	return _unref(_this)->size();
}
DEFINE_PRIM(_I32, btSoftBodyArray_size0, _IDL);

HL_PRIM HL_CONST _ref(btSoftBody)* HL_NAME(btSoftBodyArray_at1)(_ref(btSoftBodyArray)* _this, int n) {
	return alloc_ref_const((_unref(_this)->at(n)),btSoftBody);
}
DEFINE_PRIM(_IDL, btSoftBodyArray_at1, _IDL _I32);

HL_PRIM _ref(btSoftRigidDynamicsWorld)* HL_NAME(btSoftRigidDynamicsWorld_new5)(_ref(btDispatcher)* dispatcher, _ref(btBroadphaseInterface)* pairCache, _ref(btConstraintSolver)* constraintSolver, _ref(btCollisionConfiguration)* collisionConfiguration, _ref(btSoftBodySolver)* softBodySolver) {
	return alloc_ref((new btSoftRigidDynamicsWorld(_unref(dispatcher), _unref(pairCache), _unref(constraintSolver), _unref(collisionConfiguration), _unref(softBodySolver))),btSoftRigidDynamicsWorld);
}
DEFINE_PRIM(_IDL, btSoftRigidDynamicsWorld_new5, _IDL _IDL _IDL _IDL _IDL);

HL_PRIM void HL_NAME(btSoftRigidDynamicsWorld_addSoftBody3)(_ref(btSoftRigidDynamicsWorld)* _this, _ref(btSoftBody)* body, short collisionFilterGroup, short collisionFilterMask) {
	_unref(_this)->addSoftBody(_unref(body), collisionFilterGroup, collisionFilterMask);
}
DEFINE_PRIM(_VOID, btSoftRigidDynamicsWorld_addSoftBody3, _IDL _IDL _I16 _I16);

HL_PRIM void HL_NAME(btSoftRigidDynamicsWorld_removeSoftBody1)(_ref(btSoftRigidDynamicsWorld)* _this, _ref(btSoftBody)* body) {
	_unref(_this)->removeSoftBody(_unref(body));
}
DEFINE_PRIM(_VOID, btSoftRigidDynamicsWorld_removeSoftBody1, _IDL _IDL);

HL_PRIM void HL_NAME(btSoftRigidDynamicsWorld_removeCollisionObject1)(_ref(btSoftRigidDynamicsWorld)* _this, _ref(btCollisionObject)* collisionObject) {
	_unref(_this)->removeCollisionObject(_unref(collisionObject));
}
DEFINE_PRIM(_VOID, btSoftRigidDynamicsWorld_removeCollisionObject1, _IDL _IDL);

HL_PRIM _ref(btSoftBodyWorldInfo)* HL_NAME(btSoftRigidDynamicsWorld_getWorldInfo0)(_ref(btSoftRigidDynamicsWorld)* _this) {
	return alloc_ref(new btSoftBodyWorldInfo(_unref(_this)->getWorldInfo()),btSoftBodyWorldInfo);
}
DEFINE_PRIM(_IDL, btSoftRigidDynamicsWorld_getWorldInfo0, _IDL);

HL_PRIM _ref(btSoftBodyArray)* HL_NAME(btSoftRigidDynamicsWorld_getSoftBodyArray0)(_ref(btSoftRigidDynamicsWorld)* _this) {
	return alloc_ref(new btSoftBodyArray(_unref(_this)->getSoftBodyArray()),btSoftBodyArray);
}
DEFINE_PRIM(_IDL, btSoftRigidDynamicsWorld_getSoftBodyArray0, _IDL);

HL_PRIM _ref(btSoftBodyHelpers)* HL_NAME(btSoftBodyHelpers_new0)() {
	return alloc_ref((new btSoftBodyHelpers()),btSoftBodyHelpers);
}
DEFINE_PRIM(_IDL, btSoftBodyHelpers_new0,);

HL_PRIM _ref(btSoftBody)* HL_NAME(btSoftBodyHelpers_CreateRope5)(_ref(btSoftBodyHelpers)* _this, _ref(btSoftBodyWorldInfo)* worldInfo, _ref(btVector3)* from, _ref(btVector3)* to, int res, int fixeds) {
	return alloc_ref((_unref(_this)->CreateRope(*_unref(worldInfo), *_unref(from), *_unref(to), res, fixeds)),btSoftBody);
}
DEFINE_PRIM(_IDL, btSoftBodyHelpers_CreateRope5, _IDL _IDL _IDL _IDL _I32 _I32);

HL_PRIM _ref(btSoftBody)* HL_NAME(btSoftBodyHelpers_CreatePatch9)(_ref(btSoftBodyHelpers)* _this, _ref(btSoftBodyWorldInfo)* worldInfo, _ref(btVector3)* corner00, _ref(btVector3)* corner10, _ref(btVector3)* corner01, _ref(btVector3)* corner11, int resx, int resy, int fixeds, bool gendiags) {
	return alloc_ref((_unref(_this)->CreatePatch(*_unref(worldInfo), *_unref(corner00), *_unref(corner10), *_unref(corner01), *_unref(corner11), resx, resy, fixeds, gendiags)),btSoftBody);
}
DEFINE_PRIM(_IDL, btSoftBodyHelpers_CreatePatch9, _IDL _IDL _IDL _IDL _IDL _IDL _I32 _I32 _I32 _BOOL);

HL_PRIM _ref(btSoftBody)* HL_NAME(btSoftBodyHelpers_CreatePatchUV10)(_ref(btSoftBodyHelpers)* _this, _ref(btSoftBodyWorldInfo)* worldInfo, _ref(btVector3)* corner00, _ref(btVector3)* corner10, _ref(btVector3)* corner01, _ref(btVector3)* corner11, int resx, int resy, int fixeds, bool gendiags, float* tex_coords) {
	return alloc_ref((_unref(_this)->CreatePatchUV(*_unref(worldInfo), *_unref(corner00), *_unref(corner10), *_unref(corner01), *_unref(corner11), resx, resy, fixeds, gendiags, tex_coords)),btSoftBody);
}
DEFINE_PRIM(_IDL, btSoftBodyHelpers_CreatePatchUV10, _IDL _IDL _IDL _IDL _IDL _IDL _I32 _I32 _I32 _BOOL _BYTES);

HL_PRIM _ref(btSoftBody)* HL_NAME(btSoftBodyHelpers_CreateEllipsoid4)(_ref(btSoftBodyHelpers)* _this, _ref(btSoftBodyWorldInfo)* worldInfo, _ref(btVector3)* center, _ref(btVector3)* radius, int res) {
	return alloc_ref((_unref(_this)->CreateEllipsoid(*_unref(worldInfo), *_unref(center), *_unref(radius), res)),btSoftBody);
}
DEFINE_PRIM(_IDL, btSoftBodyHelpers_CreateEllipsoid4, _IDL _IDL _IDL _IDL _I32);

HL_PRIM _ref(btSoftBody)* HL_NAME(btSoftBodyHelpers_CreateFromTriMesh5)(_ref(btSoftBodyHelpers)* _this, _ref(btSoftBodyWorldInfo)* worldInfo, float* vertices, int* triangles, int ntriangles, bool randomizeConstraints) {
	return alloc_ref((_unref(_this)->CreateFromTriMesh(*_unref(worldInfo), vertices, triangles, ntriangles, randomizeConstraints)),btSoftBody);
}
DEFINE_PRIM(_IDL, btSoftBodyHelpers_CreateFromTriMesh5, _IDL _IDL _BYTES _BYTES _I32 _BOOL);

HL_PRIM _ref(btSoftBody)* HL_NAME(btSoftBodyHelpers_CreateFromConvexHull4)(_ref(btSoftBodyHelpers)* _this, _ref(btSoftBodyWorldInfo)* worldInfo, _ref(btVector3)* vertices, int nvertices, bool randomizeConstraints) {
	return alloc_ref((_unref(_this)->CreateFromConvexHull(*_unref(worldInfo), _unref(vertices), nvertices, randomizeConstraints)),btSoftBody);
}
DEFINE_PRIM(_IDL, btSoftBodyHelpers_CreateFromConvexHull4, _IDL _IDL _IDL _I32 _BOOL);

//Custom Int Array

static void finalize_btIntArray( _ref(btIntArray)* _this ) { free_ref(_this); }
HL_PRIM void HL_NAME(btIntArray_delete)(_ref(btIntArray)* _this) {
	free_ref(_this);
}
DEFINE_PRIM(_VOID, btIntArray_delete, _IDL);

HL_PRIM _ref(btIntArray)* HL_NAME(btIntArray_new1)(int num) {
	return alloc_ref((new btIntArray(num)),btIntArray);
}
DEFINE_PRIM(_IDL, btIntArray_new1, _I16);

HL_PRIM int HL_NAME(btIntArray_set2)(_ref(btIntArray)* _this, int pos, int value) {
	return _unref(_this)->set(pos, value);
}
DEFINE_PRIM(_I16, btIntArray_set2, _IDL _I16 _I16);

HL_PRIM int HL_NAME(btIntArray_size0)(_ref(btIntArray)* _this) {
	return _unref(_this)->size();
}
DEFINE_PRIM(_I16, btIntArray_size0, _IDL);

HL_PRIM int* HL_NAME(btIntArray_get_raw)(_ref(btIntArray)* _this) {
	return _unref(_this)->raw;
}
DEFINE_PRIM(_BYTES, btIntArray_get_raw, _IDL);

HL_PRIM int HL_NAME(btIntArray_at1)(_ref(btIntArray)* _this, int pos) {
	return _unref(_this)->at(pos);
}
DEFINE_PRIM(_I16, btIntArray_at1, _IDL _I16);

//Custom Float Array

static void finalize_btFloatArray( _ref(btFloatArray)* _this ) { free_ref(_this); }
HL_PRIM void HL_NAME(btFloatArray_delete)(_ref(btFloatArray)* _this) {
	free_ref(_this);
}
DEFINE_PRIM(_VOID, btFloatArray_delete, _IDL);

HL_PRIM _ref(btFloatArray)* HL_NAME(btFloatArray_new1)(int num) {
	return alloc_ref((new btFloatArray(num)),btFloatArray);
}
DEFINE_PRIM(_IDL, btFloatArray_new1, _I16);

HL_PRIM int HL_NAME(btFloatArray_set2)(_ref(btFloatArray)* _this, int pos, float value) {
	return _unref(_this)->set(pos, value);
}
DEFINE_PRIM(_I16, btFloatArray_set2, _IDL _I16 _F32);

HL_PRIM int HL_NAME(btFloatArray_size0)(_ref(btFloatArray)* _this) {
	return _unref(_this)->size();
}
DEFINE_PRIM(_I16, btFloatArray_size0, _IDL);

HL_PRIM float* HL_NAME(btFloatArray_get_raw)(_ref(btFloatArray)* _this) {
	return _unref(_this)->raw;
}
DEFINE_PRIM(_BYTES, btFloatArray_get_raw, _IDL);

HL_PRIM float HL_NAME(btFloatArray_at1)(_ref(btFloatArray)* _this, int pos) {
	return _unref(_this)->at(pos);
}
DEFINE_PRIM(_F32, btFloatArray_at1, _IDL _I16);

}
