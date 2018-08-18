package armory.trait.physics.bullet;

#if arm_bullet

import haxebullet.Bullet;
import iron.math.Vec4;
import iron.object.Transform;
import iron.object.MeshObject;

@:access(armory.trait.physics.bullet.PhysicsWorld)
class RigidBody extends iron.Trait {

	var shape:Shape;
	var _motionState:BtMotionStatePointer;
	var _shape:BtCollisionShapePointer;

	public var physics:PhysicsWorld;
	public var transform:Transform = null;

	public var mass:Float;
	public var friction:Float;
	public var restitution:Float;
	public var collisionMargin:Float;
	public var linearDamping:Float;
	public var angularDamping:Float;
	public var animated:Bool;
	var linearFactors:Array<Float>;
	var angularFactors:Array<Float>;
	var deactivationParams:Array<Float>;
	public var group = 1;
	public var trigger = false;
	var bodyScaleX:Float; // Transform scale at creation time
	var bodyScaleY:Float;
	var bodyScaleZ:Float;
	var currentScaleX:Float;
	var currentScaleY:Float;
	var currentScaleZ:Float;

	public var body:BtRigidBodyPointer = null;
	public var ready = false;

	static var nextId = 0;
	public var id = 0;

	public var onReady:Void->Void = null;
	public var onContact:Array<RigidBody->Void> = null;

	public function new(mass = 1.0, shape = Shape.Box, friction = 0.5, restitution = 0.0, collisionMargin = 0.0,
						linearDamping = 0.04, angularDamping = 0.1, animated = false,
						linearFactors:Array<Float> = null, angularFactors:Array<Float> = null,
						group = 1, trigger = false, deactivationParams:Array<Float> = null) {
		super();

		this.mass = mass;
		this.shape = shape;
		this.friction = friction;
		this.restitution = restitution;
		this.collisionMargin = collisionMargin;
		this.linearDamping = linearDamping;
		this.angularDamping = angularDamping;
		this.animated = animated;
		this.linearFactors = linearFactors;
		this.angularFactors = angularFactors;
		this.group = group;
		this.trigger = trigger;
		this.deactivationParams = deactivationParams;

		notifyOnAdd(init);
	}
	
	inline function withMargin(f:Float) {
		return f - f * collisionMargin;
	}

	public function notifyOnReady(f:Void->Void) {
		onReady = f;
		if (ready) onReady();
	}

	public function init() {
		if (ready) return;
		ready = true;

		if (!Std.is(object, MeshObject)) return; // No mesh data
		notifyOnLateUpdate(lateUpdate);
		notifyOnRemove(removeFromWorld);

		transform = object.transform;
		physics = armory.trait.physics.PhysicsWorld.active;

		_shape = null;
		if (shape == Shape.Box) {
			_shape = BtBoxShape.create(BtVector3.create(
				withMargin(transform.dim.x / 2),
				withMargin(transform.dim.y / 2),
				withMargin(transform.dim.z / 2)));
		}
		else if (shape == Shape.Sphere) {
			_shape = BtSphereShape.create(withMargin(transform.dim.x / 2));
		}
		#if cpp
		else if (shape == Shape.ConvexHull) {
		#else // TODO: recompile ammojs first
		else if (shape == Shape.ConvexHull || (shape == Shape.Mesh && mass > 0)) {
			if (shape == Shape.Mesh && mass > 0) {
				trace("Armory Warning: object " + object.name + " - dynamic mesh shape not yet implemented, using convex hull instead");
			}
		#end
			var _shapeConvex = BtConvexHullShape.create();
			fillConvexHull(_shapeConvex, transform.scale, collisionMargin);
			_shape = _shapeConvex;
		}
		else if (shape == Shape.Cone) {
			_shape = BtConeShapeZ.create(
				withMargin(transform.dim.x / 2), // Radius
				withMargin(transform.dim.z));	  // Height
		}
		else if (shape == Shape.Cylinder) {
			_shape = BtCylinderShapeZ.create(BtVector3.create(
				withMargin(transform.dim.x / 2),
				withMargin(transform.dim.y / 2),
				withMargin(transform.dim.z / 2)));
		}
		else if (shape == Shape.Capsule) {
			var r = transform.dim.x / 2;
			_shape = BtCapsuleShapeZ.create(
				withMargin(r), // Radius
				withMargin(transform.dim.z - r * 2)); // Height between 2 sphere centers
		}
		else if (shape == Shape.Mesh || shape == Shape.Terrain) {
			var meshInterface = BtTriangleMesh.create(true, true);
			fillTriangleMesh(meshInterface, transform.scale);
			#if cpp
			if (mass > 0) {
				var _shapeGImpact = BtGImpactMeshShape.create(meshInterface);
				_shapeGImpact.updateBound();
				_shape = _shapeGImpact;
				if (!physics.gimpactRegistered) {
					BtGImpactCollisionAlgorithm.registerAlgorithm(physics.dispatcher);
					physics.gimpactRegistered = true;
				}
			}
			else {
				_shape = BtBvhTriangleMeshShape.create(meshInterface, true, true);
			}
			#else // TODO: recompile ammojs first
			_shape = BtBvhTriangleMeshShape.create(meshInterface, true, true);
			#end
		}
		//else if (shape == Shape.Terrain) {
			// var data:Array<Dynamic> = [];
			// _shape = BtHeightfieldTerrainShape.create(3, 3, data, 1, -10, 10, 2, 0, true);
		//}

		var _transform = BtTransform.create();
		_transform.setIdentity();
		_transform.setOrigin(BtVector3.create(transform.worldx(), transform.worldy(), transform.worldz()));
		var rot = transform.world.getQuat();
		_transform.setRotation(BtQuaternion.create(rot.x, rot.y, rot.z, rot.w));

		var _centerOfMassOffset = BtTransform.create();
		_centerOfMassOffset.setIdentity();
		_motionState = BtDefaultMotionState.create(_transform, _centerOfMassOffset);

		var _inertia = BtVector3.create(0, 0, 0);
		if (mass > 0) _shape.calculateLocalInertia(mass, _inertia);
		var _bodyCI = BtRigidBodyConstructionInfo.create(mass, _motionState, _shape, _inertia);
		body = BtRigidBody.create(_bodyCI);
		body.setFriction(friction);
		body.setRollingFriction(friction);
		body.setRestitution(restitution);

		if (deactivationParams != null) {
			setDeactivationParams(deactivationParams[0], deactivationParams[1], deactivationParams[2]);
		}
		else {
			setActivationState(ActivationState.NoDeactivation);
		}

		if (linearDamping != 0.04 || angularDamping != 0.1) {
			body.setDamping(linearDamping, angularDamping);
		}

		if (linearFactors != null) {
			setLinearFactor(linearFactors[0], linearFactors[1], linearFactors[2]);
		}

		if (angularFactors != null) {
			setAngularFactor(angularFactors[0], angularFactors[1], angularFactors[2]);
		}

		if (trigger) body.setCollisionFlags(body.getCollisionFlags() | BtCollisionObject.CF_NO_CONTACT_RESPONSE);

		bodyScaleX = currentScaleX = transform.scale.x;
		bodyScaleY = currentScaleY = transform.scale.y;
		bodyScaleZ = currentScaleZ = transform.scale.z;

		id = nextId;
		nextId++;

		#if js
		//body.setUserIndex(nextId);
		untyped body.userIndex = id;
		#elseif cpp
		body.setUserIndex(id);
		#end

		physics.addRigidBody(this);

		if (onReady != null) onReady();
	}

	function lateUpdate() {
		if (!ready) return;
		if (object.animation != null || animated) {
			syncTransform();
		}
		else {
			var trans = body.getWorldTransform();
			var p = trans.getOrigin();
			var q = trans.getRotation();
			transform.loc.set(p.x(), p.y(), p.z());
			transform.rot.set(q.x(), q.y(), q.z(), q.w());
			if (object.parent != null) {
				var ptransform = object.parent.transform;
				transform.loc.x -= ptransform.worldx();
				transform.loc.y -= ptransform.worldy();
				transform.loc.z -= ptransform.worldz();
			}
			transform.buildMatrix();
		}

		if (onContact != null) {
			var rbs = physics.getContacts(this);
			if (rbs != null) for (rb in rbs) for (f in onContact) f(rb);
		}
	}

	public function removeFromWorld() {
		if (physics != null) physics.removeRigidBody(this);
	}

	public function activate() {
		body.activate(false);
	}

	public function disableGravity() {
		body.setGravity(BtVector3.create(0, 0, 0));
	}

	public function enableGravity() {
		body.setGravity(physics.world.getGravity());
	}

	public function setGravity(v:Vec4) {
		body.setGravity(BtVector3.create(v.x, v.y, v.z));
	}

	public function setActivationState(newState:Int) {
		body.setActivationState(newState);
	}

	public function setDeactivationParams(linearThreshold:Float, angularThreshold:Float, time:Float) {
		body.setSleepingThresholds(linearThreshold, angularThreshold);
		// body.setDeactivationTime(time); // not available in ammo
	}

	public function applyForce(force:Vec4, loc:Vec4 = null) {
		activate();
		if (loc == null) {
			body.applyCentralForce(BtVector3.create(force.x, force.y, force.z));
		}
		else {
			body.applyForce(BtVector3.create(force.x, force.y, force.z), BtVector3.create(loc.x, loc.y, loc.z));
		}
	}

	public function applyImpulse(impulse:Vec4, loc:Vec4 = null) {
		activate();
		if (loc == null) {
			body.applyCentralImpulse(BtVector3.create(impulse.x, impulse.y, impulse.z));
		}
		else {
			body.applyImpulse(BtVector3.create(impulse.x, impulse.y, impulse.z),
								  BtVector3.create(loc.x, loc.y, loc.z));
		}
	}

	public function setLinearFactor(x:Float, y:Float, z:Float) {
		body.setLinearFactor(BtVector3.create(x, y, z));
	}

	public function setAngularFactor(x:Float, y:Float, z:Float) {
		body.setAngularFactor(BtVector3.create(x, y, z));
	}

	public function getLinearVelocity():Vec4 {
		var v = body.getLinearVelocity();
		return new Vec4(v.x(), v.y(), v.z());
	}

	public function setLinearVelocity(x:Float, y:Float, z:Float) {
		body.setLinearVelocity(BtVector3.create(x, y, z));
	}

	public function getAngularVelocity():Vec4 {
		var v = body.getAngularVelocity();
		return new Vec4(v.x(), v.y(), v.z());
	}

	public function setAngularVelocity(x:Float, y:Float, z:Float) {
		body.setAngularVelocity(BtVector3.create(x, y, z));
	}

	public function setFriction(f:Float) {
		body.setFriction(f);
		body.setRollingFriction(f);
		this.friction = f;
	}

	public function notifyOnContact(f:RigidBody->Void) {
		if (onContact == null) onContact = [];
		onContact.push(f);
	}

	public function removeContact(f:RigidBody->Void) {
		onContact.remove(f);
	}

	public function syncTransform() {
		var t = transform;
		t.buildMatrix();
		var trans = BtTransform.create();
		trans.setOrigin(BtVector3.create(t.worldx(), t.worldy(), t.worldz()));
		var rot = t.world.getQuat();
		trans.setRotation(BtQuaternion.create(rot.x, rot.y, rot.z, rot.w));
		body.setCenterOfMassTransform(trans);
		// _motionState.getWorldTransform(trans);
		// trans.setOrigin(BtVector3.create(t.loc.x, t.loc.y, t.loc.z));
		// _motionState.setWorldTransform(trans);
		if (currentScaleX != t.scale.x || currentScaleY != t.scale.y || currentScaleZ != t.scale.z) setScale(t.scale);
		activate();
	}

	function setScale(v:Vec4) {
		currentScaleX = v.x;
		currentScaleY = v.y;
		currentScaleZ = v.z;
		_shape.setLocalScaling(BtVector3.create(bodyScaleX * v.x, bodyScaleY * v.y, bodyScaleZ * v.z));
		physics.world.updateSingleAabb(body);
	}

	function fillConvexHull(shape:BtConvexHullShapePointer, scale:Vec4, margin:Float) {
		var positions = cast(object, MeshObject).data.geom.positions;

		var sx = scale.x * (1.0 - margin);
		var sy = scale.y * (1.0 - margin);
		var sz = scale.z * (1.0 - margin);

		for (i in 0...Std.int(positions.length / 3)) {
			shape.addPoint(BtVector3.create(positions[i * 3] * sx, positions[i * 3 + 1] * sy, positions[i * 3 + 2] * sz), true);
		}
	}

	function fillTriangleMesh(triangleMesh:BtTriangleMeshPointer, scale:Vec4) {
		var positions = cast(object, MeshObject).data.geom.positions;
		var indices = cast(object, MeshObject).data.geom.indices;

		for (ar in indices) {
			for (i in 0...Std.int(ar.length / 3)) {
				triangleMesh.addTriangle(
					BtVector3.create(positions[ar[i * 3 + 0] * 3 + 0] * scale.x,
								  	 positions[ar[i * 3 + 0] * 3 + 1] * scale.y,
								  	 positions[ar[i * 3 + 0] * 3 + 2] * scale.z),
					BtVector3.create(positions[ar[i * 3 + 1] * 3 + 0] * scale.x,
								  	 positions[ar[i * 3 + 1] * 3 + 1] * scale.y,
								  	 positions[ar[i * 3 + 1] * 3 + 2] * scale.z),
					BtVector3.create(positions[ar[i * 3 + 2] * 3 + 0] * scale.x,
								  	 positions[ar[i * 3 + 2] * 3 + 1] * scale.y,
								  	 positions[ar[i * 3 + 2] * 3 + 2] * scale.z)
				);
			}
		}
	}
}

@:enum abstract Shape(Int) from Int to Int {
	var Box = 0;
	var Sphere = 1;
	var ConvexHull = 2;
	var Mesh = 3;
	var Cone = 4;
	var Cylinder = 5;
	var Capsule = 6;
	var Terrain = 7;
}

@:enum abstract ActivationState(Int) from Int to Int {
	var Active = 1;
	var NoDeactivation = 4;
	var NoSimulation = 5;
}

#end
