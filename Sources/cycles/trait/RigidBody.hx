package cycles.trait;

#if WITH_PHYSICS
import haxebullet.Bullet;
#end
import lue.trait.Trait;
import lue.sys.Time;
import lue.math.Vec4;
import lue.node.Transform;
import lue.node.ModelNode;
import cycles.Root;

class RigidBody extends Trait {

#if (!WITH_PHYSICS)
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

	public var body:BtRigidBodyPointer = null;

	static var nextId = 0;
	public var id = 0;

	public var onCreated:Void->Void = null;

	public function new(mass:Float = 1, shape:Int = SHAPE_BOX, friction:Float = 0.5) {
		super();

		this.mass = mass;
		this.shape = shape;
		this.friction = friction;

		requestInit(init);
		requestLateUpdate(lateUpdate);
		requestRemove(removeFromWorld);
	}

	public function init() {
		transform = node.transform;
		physics = Root.physics;

		if (body != null) return;

		var _shape:BtCollisionShapePointer = null;
		var _shapeConvex:BtConvexHullShapePointer = null;

		if (shape == SHAPE_BOX) {
			_shape = BtBoxShape.create(BtVector3.create(
				transform.size.x / 2,
				transform.size.y / 2,
				transform.size.z / 2).value);
		}
		else if (shape == SHAPE_SPHERE) {
			_shape = BtSphereShape.create(transform.size.x / 2);
		}
		else if (shape == SHAPE_CONVEX_HULL || shape == SHAPE_MESH) { // Use convex hull for mesh for now
			_shapeConvex = BtConvexHullShape.create();
			addPointsToConvexHull(_shapeConvex);
		}
		else if (shape == SHAPE_CONE) {
			_shape = BtConeShapeZ.create(
				transform.size.x / 2, // Radius
				transform.size.z);	  // Height
		}
		else if (shape == SHAPE_CYLINDER) {
			_shape = BtCylinderShapeZ.create(BtVector3.create(
				transform.size.x / 2,
				transform.size.y / 2,
				transform.size.z / 2).value);
		}
		else if (shape == SHAPE_CAPSULE) {
			_shape = BtCapsuleShapeZ.create(
				(transform.size.x / 2),// * scaleX, // Radius
				transform.size.z);// * scaleZ); // Height
		}
		//else if (shape == SHAPE_TERRAIN) {
		//	throw "Terrain not yet supported, use static mesh instead.";
			/*
			var data:Array<Dynamic> = [];
			_shape = BtHeightfieldTerrainShape.create(3, 3, data, 1, -10, 10, 2, 0, true);
			*/
		//}
		else if (shape == SHAPE_STATIC_MESH || shape == SHAPE_TERRAIN) {
			var meshInterface = BtTriangleMesh.create(true, true);
			fillTriangleMesh(meshInterface);
			_shape = BtBvhTriangleMeshShape.create(meshInterface, true, true);
		}

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

		var _centerOfMassOffset = BtTransform.create();
		_centerOfMassOffset.value.setIdentity();
		var _motionState = BtDefaultMotionState.create(_transform.value, _centerOfMassOffset.value);
		var _inertia = BtVector3.create(0, 0, 0);

		if (_shapeConvex == null) {
			if (shape != SHAPE_STATIC_MESH && shape != SHAPE_TERRAIN) {
				_shape.value.calculateLocalInertia(mass, _inertia.value);
			}
			var _bodyCI = BtRigidBodyConstructionInfo.create(mass, _motionState, _shape, _inertia.value);
			body = BtRigidBody.create(_bodyCI.value);
			body.value.setFriction(friction);
			body.value.setRollingFriction(friction);
		}
		else {
			_shapeConvex.value.calculateLocalInertia(mass, _inertia.value);
			var _bodyCI = BtRigidBodyConstructionInfo.create(mass, _motionState, _shapeConvex, _inertia.value);
			body = BtRigidBody.create(_bodyCI.value);
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

	function lateUpdate() {
		var trans = body.value.getWorldTransform();
		var p = trans.getOrigin();
		var q = trans.getRotation();
		transform.pos.set(p.x(), p.y(), p.z());
		transform.rot.set(q.x(), q.y(), q.z(), q.w());

		transform.dirty = true;
		transform.update();
	}

	public inline function removeFromWorld() {
		physics.removeRigidBody(this);
	}

	public inline function activate() {
		body.value.activate(false);
	}

	public inline function disableGravity() {
		// TODO: use setGravity instead
		setLinearFactor(0, 0, 0);
		setAngularFactor(0, 0, 0);
	}

	/*public inline function setGravity(v:Vec4) {
		body.value.setGravity(BtVector3.create(v.x, v.y, v.z).value);
	}*/

	/*public inline function setActivationState(newState:Int) {
		body.value.setActivationState(newState);
	}*/

	public inline function applyImpulse(impulse:Vec4, pos:Vec4 = null) {
		if (pos == null) {
			body.value.applyCentralImpulse(BtVector3.create(impulse.x, impulse.y, impulse.z).value);
		}
		else {
			body.value.applyImpulse(BtVector3.create(impulse.x, impulse.y, impulse.z).value,
									BtVector3.create(pos.x, pos.y, pos.z).value);
		}
	}

	public inline function setLinearFactor(x:Float, y:Float, z:Float) {
		body.value.setLinearFactor(BtVector3.create(x, y, z).value);
	}

	public inline function setAngularFactor(x:Float, y:Float, z:Float) {
		body.value.setAngularFactor(BtVector3.create(x, y, z).value);
	}

	// public inline function getLinearVelocity():BtVector3 {
	// 	return body.value.getLinearVelocity(); // Unable to compile in cpp
	// }

	public inline function setLinearVelocity(x:Float, y:Float, z:Float) {
		body.value.setLinearVelocity(BtVector3.create(x, y, z).value);
	}

	// public inline function getAngularVelocity():BtVector3 {
	// 	return body.value.getAngularVelocity();
	// }

	public inline function setAngularVelocity(x:Float, y:Float, z:Float) {
		body.value.setAngularVelocity(BtVector3.create(x, y, z).value);
	}

	public function syncTransform() {
		var trans = BtTransform.create();
		trans.value.setOrigin(BtVector3.create(transform.pos.x, transform.pos.y, transform.pos.z).value);
		trans.value.setRotation(BtQuaternion.create(transform.rot.x, transform.rot.y, transform.rot.z, transform.rot.w).value);
		body.value.setCenterOfMassTransform(trans.value);
	}

	function addPointsToConvexHull(shape:BtConvexHullShapePointer) {
		var positions = cast(node, ModelNode).resource.geometry.positions;

		for (i in 0...Std.int(positions.length / 3)) {
			#if js
			shape.addPoint(BtVector3.create(positions[i * 3], positions[i * 3 + 1], positions[i * 3 + 2]).value, true);
			#elseif cpp
			shape.value.addPoint(BtVector3.create(positions[i * 3], positions[i * 3 + 1], positions[i * 3 + 2]).value, true);
			#end
		}
	}

	function fillTriangleMesh(triangleMesh:BtTriangleMeshPointer) {
		var positions = cast(node, ModelNode).resource.geometry.positions;
		var indices = cast(node, ModelNode).resource.geometry.indices;

		for (i in 0...Std.int(indices[0].length / 3)) {
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
		}
	}
#end
}
