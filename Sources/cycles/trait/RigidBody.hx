package cycles.trait;

#if WITH_PHYSICS
import haxebullet.Bullet;
#end
import lue.Trait;
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
	public var collisionMargin:Float;

	public var body:BtRigidBodyPointer = null;
	public var bodyCreated = false;
	public var shapeConvexCreated: Bool;

	static var nextId = 0;
	public var id = 0;

	public var onCreated:Void->Void = null;

	public function new(mass = 1.0, shape = SHAPE_BOX, friction = 0.5, collisionMargin = 0.06) {
		super();

		this.mass = mass;
		this.shape = shape;
		this.friction = friction;
		this.collisionMargin = collisionMargin;

		requestInit(init);
		requestLateUpdate(lateUpdate);
		requestRemove(removeFromWorld);
	}
	
	inline function withMargin(f:Float) {
		return f - f * collisionMargin;
	}

	public function init() {
		
		transform = node.transform;
		physics = Root.physics;

		if (bodyCreated) return;
		bodyCreated = true;

		var _shape:BtCollisionShapePointer = null;
		var _shapeConvex:BtConvexHullShapePointer = null;
		shapeConvexCreated = false;
		var _inertia = BtVector3.create(0, 0, 0);

		if (shape == SHAPE_BOX) {
			_shape = BtBoxShape.create(BtVector3.create(
				withMargin(transform.size.x / 2),
				withMargin(transform.size.y / 2),
				withMargin(transform.size.z / 2)).value);
		}
		else if (shape == SHAPE_SPHERE) {
			_shape = BtSphereShape.create(withMargin(transform.size.x / 2));
		}
		else if (shape == SHAPE_CONVEX_HULL || shape == SHAPE_MESH) { // Use convex hull for mesh for now
			_shapeConvex = BtConvexHullShape.create();
			shapeConvexCreated = true;
			addPointsToConvexHull(_shapeConvex);
		}
		else if (shape == SHAPE_CONE) {
			_shape = BtConeShapeZ.create(
				withMargin(transform.size.x / 2), // Radius
				withMargin(transform.size.z));	  // Height
		}
		else if (shape == SHAPE_CYLINDER) {
			_shape = BtCylinderShapeZ.create(BtVector3.create(
				withMargin(transform.size.x / 2),
				withMargin(transform.size.y / 2),
				withMargin(transform.size.z / 2)).value);
		}
		else if (shape == SHAPE_CAPSULE) {
			_shape = BtCapsuleShapeZ.create(
				withMargin(transform.size.x / 2),// * scaleX, // Radius
				withMargin(transform.size.z));// * scaleZ); // Height
		}
		//else if (shape == SHAPE_TERRAIN) {
			// var data:Array<Dynamic> = [];
			// _shape = BtHeightfieldTerrainShape.create(3, 3, data, 1, -10, 10, 2, 0, true);
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

		if (!shapeConvexCreated) {
			if (shape != SHAPE_STATIC_MESH && shape != SHAPE_TERRAIN) {
				_shape.ptr.calculateLocalInertia(mass, _inertia.value);
			}
			var _bodyCI = BtRigidBodyConstructionInfo.create(mass, _motionState, _shape, _inertia.value);
			body = BtRigidBody.create(_bodyCI.value);
			body.ptr.setFriction(friction);
			body.ptr.setRollingFriction(friction);
		}
		else {
			_shapeConvex.ptr.calculateLocalInertia(mass, _inertia.value);
			var _bodyCI = BtRigidBodyConstructionInfo.create(mass, _motionState, _shapeConvex, _inertia.value);
			body = BtRigidBody.create(_bodyCI.value);
		}

		id = nextId;
		nextId++;

		#if js
		//body.setUserIndex(nextId);
		untyped body.userIndex = id;
		#elseif cpp
		body.ptr.setUserIndex(id);
		#end

		physics.addRigidBody(this);

		if (onCreated != null) onCreated();
	}

	function lateUpdate() {
		var trans = body.ptr.getWorldTransform();
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

	public function activate() {
		body.ptr.activate(false);
	}

	public function disableGravity() {
		// TODO: use setGravity instead
		setLinearFactor(0, 0, 0);
		setAngularFactor(0, 0, 0);
	}

	/*public function setGravity(v:Vec4) {
		body.ptr.setGravity(BtVector3.create(v.x, v.y, v.z).value);
	}*/

	/*public function setActivationState(newState:Int) {
		body.ptr.setActivationState(newState);
	}*/

	public function applyImpulse(impulse:Vec4, pos:Vec4 = null) {
		if (pos == null) {
			body.ptr.applyCentralImpulse(BtVector3.create(impulse.x, impulse.y, impulse.z).value);
		}
		else {
			body.ptr.applyImpulse(BtVector3.create(impulse.x, impulse.y, impulse.z).value,
								  BtVector3.create(pos.x, pos.y, pos.z).value);
		}
	}

	public function setLinearFactor(x:Float, y:Float, z:Float) {
		body.ptr.setLinearFactor(BtVector3.create(x, y, z).value);
	}

	public function setAngularFactor(x:Float, y:Float, z:Float) {
		body.ptr.setAngularFactor(BtVector3.create(x, y, z).value);
	}

	public function getLinearVelocity():BtVector3 {
		return body.ptr.getLinearVelocity(); // Unable to compile in cpp
	}

	public function setLinearVelocity(x:Float, y:Float, z:Float) {
		body.ptr.setLinearVelocity(BtVector3.create(x, y, z).value);
	}

	// public function getAngularVelocity():BtVector3 {
	// 	return body.ptr.getAngularVelocity();
	// }

	public function setAngularVelocity(x:Float, y:Float, z:Float) {
		body.ptr.setAngularVelocity(BtVector3.create(x, y, z).value);
	}

	public function syncTransform() {
		var trans = BtTransform.create();
		trans.value.setOrigin(BtVector3.create(transform.pos.x, transform.pos.y, transform.pos.z).value);
		trans.value.setRotation(BtQuaternion.create(transform.rot.x, transform.rot.y, transform.rot.z, transform.rot.w).value);
		body.ptr.setCenterOfMassTransform(trans.value);
	}

	function addPointsToConvexHull(shape:BtConvexHullShapePointer) {
		var positions = cast(node, ModelNode).resource.geometry.positions;

		for (i in 0...Std.int(positions.length / 3)) {
			#if js
			shape.addPoint(BtVector3.create(positions[i * 3], positions[i * 3 + 1], positions[i * 3 + 2]).value, true);
			#elseif cpp
			shape.ptr.addPoint(BtVector3.create(positions[i * 3], positions[i * 3 + 1], positions[i * 3 + 2]).value, true);
			#end
		}
	}

	function fillTriangleMesh(triangleMesh:BtTriangleMeshPointer) {
		var positions = cast(node, ModelNode).resource.geometry.positions;
		var indices = cast(node, ModelNode).resource.geometry.indices;

		for (i in 0...Std.int(indices[0].length / 3)) {
			triangleMesh.ptr.addTriangle(
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
