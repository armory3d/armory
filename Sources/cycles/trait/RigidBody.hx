package cycles.trait;

import haxebullet.Bullet;
import lue.trait.Trait;
import lue.sys.Time;
import lue.math.Vec3;
import lue.node.Transform;
import lue.node.ModelNode;
import cycles.Root;

class RigidBody extends Trait {

#if (!js && !cpp)
	public function new() { super(); }
#else

	public static inline var SHAPE_BOX = 0;
	public static inline var SHAPE_SPHERE = 1;
	public static inline var SHAPE_CONVEX_HULL = 2;
	public static inline var SHAPE_MESH = 3;
	public static inline var SHAPE_CONE = 4;
	public static inline var SHAPE_CYLINDER = 5;
	public static inline var SHAPE_CAPSULE = 6;
	public static inline var SHAPE_TERRAIN = 7;
	public static inline var SHAPE_STATIC_MESH = 8;
	var shape:Int;

	public var physics:PhysicsWorld;
	public var transform:Transform;

	public var mass:Float;
	public var friction:Float;

	#if js
	public var body:BtRigidBody = null;
	#elseif cpp
	public var body:cpp.Pointer<BtRigidBody> = null;
	#end

	static var nextId = 0;
	public var id = 0;

	public var onCreated:Void->Void = null;

	public function new(mass:Float = 1, shape:Int = SHAPE_BOX, friction:Float = 0.5) {
		super();

		this.mass = mass;
		this.shape = shape;
		this.friction = friction;

		requestInit(init);
		requestUpdate(update);
		requestRemove(removeFromWorld);
	}

	public function init() {
		transform = node.transform;
		physics = Root.physics;

		if (body != null) return;

		#if js
		var _shape:BtCollisionShape = null;
		var _shapeConvex:BtConvexHullShape = null;
		#elseif cpp
		var _shape:cpp.Pointer<BtCollisionShape> = null;
		var _shapeConvex:cpp.Pointer<BtConvexHullShape> = null;
		#end

		if (shape == SHAPE_BOX) {
			#if js
			_shape = new BtBoxShape(new BtVector3(
				transform.size.x / 2,
				transform.size.y / 2,
				transform.size.z / 2));
			#elseif cpp
			_shape = BtBoxShape.create(BtVector3.create(
				transform.size.x / 2,
				transform.size.y / 2,
				transform.size.z / 2).value);
			#end
		}
		else if (shape == SHAPE_SPHERE) {
			#if js
			_shape = new BtSphereShape(transform.size.x / 2);
			#elseif cpp
			_shape = BtSphereShape.create(transform.size.x / 2);
			#end
		}
		else if (shape == SHAPE_CONVEX_HULL || shape == SHAPE_MESH) { // Use convex hull for mesh for now
			#if js
			_shapeConvex = new BtConvexHullShape();
			#elseif cpp
			_shapeConvex = BtConvexHullShape.create();
			#end
			addPointsToConvexHull(_shapeConvex);
		}
		else if (shape == SHAPE_CONE) {
			#if js
			_shape = new BtConeShapeZ(
				transform.size.x / 2, // Radius
				transform.size.z);	  // Height
			#elseif cpp
			_shape = BtConeShapeZ.create(
				transform.size.x / 2,
				transform.size.z);
			#end
		}
		else if (shape == SHAPE_CYLINDER) {
			#if js
			_shape = new BtCylinderShapeZ(new BtVector3(
				transform.size.x / 2,
				transform.size.y / 2,
				transform.size.z / 2));
			#elseif cpp
			_shape = BtCylinderShapeZ.create(BtVector3.create(
				transform.size.x / 2,
				transform.size.y / 2,
				transform.size.z / 2).value);
			#end
		}
		else if (shape == SHAPE_CAPSULE) {
			#if js
			_shape = new BtCapsuleShapeZ(
				(transform.size.x / 2),// * scaleX, // Radius
				transform.size.z);// * scaleZ); // Height
			#elseif cpp
			_shape = BtCapsuleShapeZ.create(
				transform.size.x / 4,
				transform.size.z * 0.65);
			#end
		}
		//else if (shape == SHAPE_TERRAIN) {
		//	throw "Terrain not yet supported, use static mesh instead.";
			/*
			#if js
			var data:Array<Dynamic> = [];
			_shape = new BtHeightfieldTerrainShape(3, 3, data, 1, -10, 10, 2, 0, true);
			#elseif cpp
			var data:Array<Dynamic> = [];
			_shape = BtHeightfieldTerrainShape.create(3, 3, data, 1, -10, 10, 2, 0, true);
			#end*/
		//}
		else if (shape == SHAPE_STATIC_MESH || shape == SHAPE_TERRAIN) {
			#if js
			var meshInterface = new BtTriangleMesh(true, true);
			fillTriangleMesh(meshInterface);
			_shape = new BtBvhTriangleMeshShape(meshInterface, true, true);
			#elseif cpp
			var meshInterface = BtTriangleMesh.create(true, true);
			fillTriangleMesh(meshInterface);
			_shape = BtBvhTriangleMeshShape.create(meshInterface, true, true);
			#end
		}

		#if js
        var _transform = new BtTransform();
		_transform.setIdentity();
		_transform.setOrigin(new BtVector3(
			transform.pos.x,
			transform.pos.y,
			transform.pos.z));
		_transform.setRotation(new BtQuaternion(
			transform.rot.x,
			transform.rot.y,
			transform.rot.z,
			transform.rot.w));
		#elseif cpp
		var _transform = BtTransform.create();
		_transform.value.setIdentity();
		_transform.value.setOrigin(BtVector3.create(
			transform.pos.x,
			transform.pos.y,
			transform.pos.z).value);
		_transform.value.setRotation(BtQuaternion.create(
			transform.rot.x,
			transform.rot.y,
			transform.rot.z,
			transform.rot.w).value);
		#end

		#if js
		var _centerOfMassOffset = new BtTransform();
		_centerOfMassOffset.setIdentity();
		var _motionState = new BtDefaultMotionState(_transform, _centerOfMassOffset);
		var _inertia = new BtVector3(0, 0, 0);
		#elseif cpp
		var _centerOfMassOffset = BtTransform.create();
		_centerOfMassOffset.value.setIdentity();
		var _motionState = BtDefaultMotionState.create(_transform.value, _centerOfMassOffset.value);
		var _inertia = BtVector3.create(0, 0, 0);
		#end

		if (_shapeConvex == null) {
			#if js
			if (shape != SHAPE_STATIC_MESH && shape != SHAPE_TERRAIN) {
				_shape.calculateLocalInertia(mass, _inertia);
			}
			var _bodyCI = new BtRigidBodyConstructionInfo(mass, _motionState, _shape, _inertia);
			body = new BtRigidBody(_bodyCI);
			body.setFriction(friction);
			body.setRollingFriction(friction);
			#elseif cpp
			if (shape != SHAPE_STATIC_MESH && shape != SHAPE_TERRAIN) {
				_shape.value.calculateLocalInertia(mass, _inertia.value);
			}
			var _bodyCI = BtRigidBodyConstructionInfo.create(mass, _motionState, _shape, _inertia.value);
			body = BtRigidBody.create(_bodyCI.value);
			body.value.setFriction(friction);
			body.value.setRollingFriction(friction);
			#end
		}
		else {
			#if js
			_shapeConvex.calculateLocalInertia(mass, _inertia);
			var _bodyCI = new BtRigidBodyConstructionInfo(mass, _motionState, _shapeConvex, _inertia);
			body = new BtRigidBody(_bodyCI);
			#elseif cpp
			_shapeConvex.value.calculateLocalInertia(mass, _inertia.value);
			var _bodyCI = BtRigidBodyConstructionInfo.create(mass, _motionState, _shapeConvex, _inertia.value);
			body = BtRigidBody.create(_bodyCI.value);
			#end
		}

		id = nextId;
		nextId++;

		#if js
		//body.setUserIndex(nextId);
		untyped body.userIndex = id;
		#elseif cpp
		body.value.setUserIndex(id);
		#end

		physics.addRigidBody(this);

		if (onCreated != null) onCreated();
	}

	function update() {
		#if js
		var trans = body.getWorldTransform();
		#elseif cpp
		var trans = body.value.getWorldTransform();
		#end
		var p = trans.getOrigin();
		var q = trans.getRotation();
		transform.pos.set(p.x(), p.y(), p.z());
		transform.rot.set(q.x(), q.y(), q.z(), q.w());

		transform.dirty = true;
		transform.update();
	}

	public function removeFromWorld() {
		physics.removeRigidBody(this);
	}

	public inline function activate() {
		#if js
		body.activate(false);
		#elseif cpp
		body.value.activate(false);
		#end
	}

	public inline function disableGravity() {
		// TODO: use setGravity instead
		setLinearFactor(0, 0, 0);
		setAngularFactor(0, 0, 0);
	}

	/*public inline function setGravity(v:Vec3) {
		#if js
		body.setGravity(new BtVector3(v.x, v.y, v.z));
		#elseif cpp
		body.value.setGravity(BtVector3.create(v.x, v.y, v.z).value);
		#end
	}*/

	/*public inline function setActivationState(newState:Int) {
		#if js
		body.setActivationState(newState);
		#elseif cpp
		body.value.setActivationState(newState);
		#end
	}*/

	public inline function applyImpulse(impulse:Vec3, pos:Vec3 = null) {
		if (pos == null) {
			#if js
			body.applyCentralImpulse(new BtVector3(impulse.x, impulse.y, impulse.z));
			#elseif cpp
			body.value.applyCentralImpulse(BtVector3.create(impulse.x, impulse.y, impulse.z).value);
			#end
		}
		else {
			#if js
			body.applyImpulse(new BtVector3(impulse.x, impulse.y, impulse.z),
							  new BtVector3(pos.x, pos.y, pos.z));
			#elseif cpp
			body.value.applyImpulse(BtVector3.create(impulse.x, impulse.y, impulse.z).value,
									BtVector3.create(pos.x, pos.y, pos.z).value);
			#end
		}
	}

	public inline function setLinearFactor(x:Float, y:Float, z:Float) {
		#if js
		body.setLinearFactor(new BtVector3(x, y, z));
		#elseif cpp
		body.value.setLinearFactor(BtVector3.create(x, y, z).value);
		#end
	}

	public inline function setAngularFactor(x:Float, y:Float, z:Float) {
		#if js
		body.setAngularFactor(new BtVector3(x, y, z));
		#elseif cpp
		body.value.setAngularFactor(BtVector3.create(x, y, z).value);
		#end
	}

	// public inline function getLinearVelocity():BtVector3 {
	// 	#if js
	// 	return body.getLinearVelocity();
	// 	#elseif cpp // Unable to compile in cpp
	// 	return body.value.getLinearVelocity();
	// 	#end
	// }

	public inline function setLinearVelocity(x:Float, y:Float, z:Float) {
		#if js
		body.setLinearVelocity(new BtVector3(x, y, z));
		#elseif cpp
		body.value.setLinearVelocity(BtVector3.create(x, y, z).value);
		#end
	}

	// public inline function getAngularVelocity():BtVector3 {
	// 	#if js
	// 	return body.getAngularVelocity();
	// 	#elseif cpp
	// 	return body.value.getAngularVelocity();
	// 	#end
	// }

	public inline function setAngularVelocity(x:Float, y:Float, z:Float) {
		#if js
		body.setAngularVelocity(new BtVector3(x, y, z));
		#elseif cpp
		body.value.setAngularVelocity(BtVector3.create(x, y, z).value);
		#end
	}

	public function syncTransform() {
		#if js
		var trans = new BtTransform();
		trans.setOrigin(new BtVector3(transform.pos.x, transform.pos.y, transform.pos.z));
		trans.setRotation(new BtQuaternion(transform.rot.x, transform.rot.y, transform.rot.z, transform.rot.w));
		body.setCenterOfMassTransform(trans);
		#elseif cpp
		var trans = BtTransform.create();
		trans.value.setOrigin(BtVector3.create(transform.pos.x, transform.pos.y, transform.pos.z).value);
		trans.value.setRotation(BtQuaternion.create(transform.rot.x, transform.rot.y, transform.rot.z, transform.rot.w).value);
		body.value.setCenterOfMassTransform(trans.value);
		#end
	}

	#if cpp
	function addPointsToConvexHull(shape:cpp.Pointer<BtConvexHullShape>) {
	#else
	function addPointsToConvexHull(shape:BtConvexHullShape) {
	#end

		var positions = cast(node, ModelNode).resource.geometry.positions;

		for (i in 0...Std.int(positions.length / 3)) {
			#if js
			shape.addPoint(new BtVector3(positions[i * 3], positions[i * 3 + 1], positions[i * 3 + 2]), true);
			#elseif cpp
			shape.value.addPoint(BtVector3.create(positions[i * 3], positions[i * 3 + 1], positions[i * 3 + 2]).value, true);
			#end
		}
	}

	#if cpp
	function fillTriangleMesh(triangleMesh:cpp.Pointer<BtTriangleMesh>) {
	#else
	function fillTriangleMesh(triangleMesh:BtTriangleMesh) {
	#end

		var positions = cast(node, ModelNode).resource.geometry.positions;
		var indices = cast(node, ModelNode).resource.geometry.indices;

		for (i in 0...Std.int(indices[0].length / 3)) {
			#if js
			triangleMesh.addTriangle(
				new BtVector3(positions[indices[0][i * 3 + 0] * 3 + 0],
							  positions[indices[0][i * 3 + 0] * 3 + 1],
							  positions[indices[0][i * 3 + 0] * 3 + 2]),
				new BtVector3(positions[indices[0][i * 3 + 1] * 3 + 0],
							  positions[indices[0][i * 3 + 1] * 3 + 1],
							  positions[indices[0][i * 3 + 1] * 3 + 2]),
				new BtVector3(positions[indices[0][i * 3 + 2] * 3 + 0],
							  positions[indices[0][i * 3 + 2] * 3 + 1],
							  positions[indices[0][i * 3 + 2] * 3 + 2])
			);
			#elseif cpp
			triangleMesh.value.addTriangle(
				BtVector3.create(positions[indices[0][i * 3 + 0] * 3 + 0],
							  	 positions[indices[0][i * 3 + 0] * 3 + 1],
							  	 positions[indices[0][i * 3 + 0] * 3 + 2]).value,
				BtVector3.create(positions[indices[0][i * 3 + 1] * 3 + 0],
							  	 positions[indices[0][i * 3 + 1] * 3 + 1],
							  	 positions[indices[0][i * 3 + 1] * 3 + 2]).value,
				BtVector3.create(positions[indices[0][i * 3 + 2] * 3 + 0],
							  	 positions[indices[0][i * 3 + 2] * 3 + 1],
							  	 positions[indices[0][i * 3 + 2] * 3 + 2]).value
			);
			#end
		}
	}
#end
}
