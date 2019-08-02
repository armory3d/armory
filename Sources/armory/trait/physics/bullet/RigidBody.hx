package armory.trait.physics.bullet;

#if arm_bullet

import iron.math.Vec4;
import iron.math.Quat;
import iron.object.Transform;
import iron.object.MeshObject;
import iron.data.MeshData;

/**
 * RigidBody is used to allow objects to interact with Physics in your game including collisions and gravity.
 * RigidBody can also be used with the getContacts method to detect collisions and run appropriate code.
 * The Bullet physics engine is used for these calculations.
 */
@:access(armory.trait.physics.bullet.PhysicsWorld)
class RigidBody extends iron.Trait {

	var shape:Shape;
	public var physics:PhysicsWorld;
	public var transform:Transform = null;
	public var mass:Float;
	public var friction:Float;
	public var restitution:Float;
	public var collisionMargin:Float;
	public var linearDamping:Float;
	public var angularDamping:Float;
	public var animated:Bool;
	public var destroyed = false;
	var linearFactors:Array<Float>;
	var angularFactors:Array<Float>;
	var deactivationParams:Array<Float>;
	var ccd = false; // Continuous collision detection
	public var group = 1;
	var trigger = false;
	var bodyScaleX:Float; // Transform scale at creation time
	var bodyScaleY:Float;
	var bodyScaleZ:Float;
	var currentScaleX:Float;
	var currentScaleY:Float;
	var currentScaleZ:Float;

	public var body:bullet.RigidBody = null;
	public var motionState:bullet.MotionState;
	public var btshape:bullet.CollisionShape;
	public var ready = false;
	static var nextId = 0;
	public var id = 0;
	public var onReady:Void->Void = null;
	public var onContact:Array<RigidBody->Void> = null;
	public var heightData:haxe.io.Bytes = null;
	#if js
	static var ammoArray:Int = -1;
	#end

	static var nullvec = true;
	static var vec1:bullet.Vector3;
	static var vec2:bullet.Vector3;
	static var vec3:bullet.Vector3;
	static var quat1:bullet.Quaternion;
	static var trans1:bullet.Transform;
	static var trans2:bullet.Transform;
	static var quat = new Quat();

	static var convexHullCache = new Map<MeshData, bullet.ConvexHullShape>();
	static var triangleMeshCache = new Map<MeshData, bullet.TriangleMesh>();
	static var usersCache = new Map<MeshData, Int>();

	public function new(shape = Shape.Box, mass = 1.0, friction = 0.5, restitution = 0.0, group = 1,
						params:Array<Float> = null, flags:Array<Bool> = null) {
		super();

		if (nullvec) {
			nullvec = false;
			vec1 = new bullet.Vector3(0, 0, 0);
			vec2 = new bullet.Vector3(0, 0, 0);
			vec3 = new bullet.Vector3(0, 0, 0);
			quat1 = new bullet.Quaternion(0, 0, 0, 0);
			trans1 = new bullet.Transform();
			trans2 = new bullet.Transform();
		} 

		this.shape = shape;
		this.mass = mass;
		this.friction = friction;
		this.restitution = restitution;
		this.group = group;

		if (params == null) params = [0.04, 0.1, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0];
		if (flags == null) flags = [false, false, false];

		this.linearDamping = params[0];
		this.angularDamping = params[1];
		this.linearFactors = [params[2], params[3], params[4]];
		this.angularFactors = [params[5], params[6], params[7]];
		this.collisionMargin = params[8];
		this.deactivationParams = [params[9], params[10], params[11]];
		this.animated = flags[0];
		this.trigger = flags[1];
		this.ccd = flags[2];

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

		transform = object.transform;
		physics = armory.trait.physics.PhysicsWorld.active;

		if (shape == Shape.Box) {
			vec1.setX(withMargin(transform.dim.x / 2));
			vec1.setY(withMargin(transform.dim.y / 2));
			vec1.setZ(withMargin(transform.dim.z / 2));
			btshape = new bullet.BoxShape(vec1);
		}
		else if (shape == Shape.Sphere) {
			btshape = new bullet.SphereShape(withMargin(transform.dim.x / 2));
		}
		else if (shape == Shape.ConvexHull) {
			var shapeConvex = fillConvexHull(transform.scale, collisionMargin);
			btshape = shapeConvex;
		}
		else if (shape == Shape.Cone) {
			var coneZ = new bullet.ConeShapeZ(
				withMargin(transform.dim.x / 2), // Radius
				withMargin(transform.dim.z));	  // Height
			var cone:bullet.ConeShape = coneZ;
			btshape = cone;
		}
		else if (shape == Shape.Cylinder) {
			vec1.setX(withMargin(transform.dim.x / 2));
			vec1.setY(withMargin(transform.dim.y / 2));
			vec1.setZ(withMargin(transform.dim.z / 2));
			var cylZ = new bullet.CylinderShapeZ(vec1);
			var cyl:bullet.CylinderShape = cylZ;
			btshape = cyl;
		}
		else if (shape == Shape.Capsule) {
			var r = transform.dim.x / 2;
			var capsZ = new bullet.CapsuleShapeZ(
				withMargin(r), // Radius
				withMargin(transform.dim.z - r * 2)); // Height between 2 sphere centers
			var caps:bullet.CapsuleShape = capsZ;
			btshape = caps;
		}
		else if (shape == Shape.Mesh) {
			var meshInterface = fillTriangleMesh(transform.scale);
			if (mass > 0) {
				var shapeGImpact = new bullet.GImpactMeshShape(meshInterface);
				shapeGImpact.updateBound();
				var shapeConcave:bullet.ConcaveShape = shapeGImpact;
				btshape = shapeConcave;
				if (!physics.gimpactRegistered) {
					// TODO: add binding // shapeGImpact.registerAlgorithm(physics.dispatcher);
					physics.gimpactRegistered = true;
				}
			}
			else {
				var shapeBvh = new bullet.BvhTriangleMeshShape(meshInterface, true, true);
				var shapeTri:bullet.TriangleMeshShape = shapeBvh;
				var shapeConcave:bullet.ConcaveShape = shapeTri;
				btshape = shapeConcave;
			}
		}
		// else if (shape == Shape.Terrain) {
		// 	#if js
		// 	var length = heightData.length;
		// 	if (ammoArray == -1) {
		// 		ammoArray = bullet.Ammo._malloc(length);
		// 	}
		// 	// From texture bytes
		// 	for (i in 0...length) {
		// 		bullet.Ammo.HEAPU8[ammoArray + i] = heightData.get(i);
		// 	}
		// 	var slice = Std.int(Math.sqrt(length)); // Assuming square terrain data
		// 	var axis = 2; // z
		// 	var dataType = 5; // u8
		// 	btshape = new bullet.HeightfieldTerrainShape(slice, slice, ammoArray, 1 / 255, 0, 1, axis, dataType, false);
		// 	vec1.setX(transform.dim.x / slice);
		// 	vec1.setY(transform.dim.y / slice);
		// 	vec1.setZ(transform.dim.z);
		// 	btshape.setLocalScaling(vec1);
		// 	#end
		// }

		trans1.setIdentity();
		vec1.setX(transform.worldx());
		vec1.setY(transform.worldy());
		vec1.setZ(transform.worldz());
		trans1.setOrigin(vec1);
		quat.fromMat(transform.world);
		quat1.setValue(quat.x, quat.y, quat.z, quat.w);
		trans1.setRotation(quat1);

		var centerOfMassOffset = trans2;
		centerOfMassOffset.setIdentity();
		motionState = new bullet.DefaultMotionState(trans1, centerOfMassOffset);

		vec1.setX(0);
		vec1.setY(0);
		vec1.setZ(0);
		var inertia = vec1;
		if (mass > 0) btshape.calculateLocalInertia(mass, inertia);
		var bodyCI = new bullet.RigidBodyConstructionInfo(mass, motionState, btshape, inertia);
		body = new bullet.RigidBody(bodyCI);
		
		var bodyColl:bullet.CollisionObject = body;
		bodyColl.setFriction(friction);
		// body.setRollingFriction(friction); // This causes bodies to get stuck, apply angular damping instead
		if (shape == Shape.Sphere || shape == Shape.Cylinder || shape == Shape.Cone || shape == Shape.Capsule) {
			angularDamping += friction;
		}
		bodyColl.setRestitution(restitution);

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

		var CF_NO_CONTACT_RESPONSE = 4; // bullet.CollisionObject.CF_NO_CONTACT_RESPONSE
		if (trigger) bodyColl.setCollisionFlags(bodyColl.getCollisionFlags() | CF_NO_CONTACT_RESPONSE);

		if (ccd) setCcd(transform.radius);

		bodyScaleX = currentScaleX = transform.scale.x;
		bodyScaleY = currentScaleY = transform.scale.y;
		bodyScaleZ = currentScaleZ = transform.scale.z;

		id = nextId;
		nextId++;

		bodyColl.setUserIndex(id);

		physics.addRigidBody(this);
		notifyOnRemove(removeFromWorld);

		if (onReady != null) onReady();

		bodyCI.delete();
	}

	function physicsUpdate() {
		if (!ready) return;
		if (object.animation != null || animated) {
			syncTransform();
		}
		else {
			var bodyColl:bullet.CollisionObject = body;
			var trans = bodyColl.getWorldTransform();

			var p = trans.getOrigin();
			var q = trans.getRotation();
			var qw:bullet.QuadWord = q;

			transform.loc.set(p.x(), p.y(), p.z());
			transform.rot.set(qw.x(), qw.y(), qw.z(), qw.w());
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
		var bodyColl:bullet.CollisionObject = body;
		bodyColl.activate(false);
	}

	public function disableGravity() {
		vec1.setValue(0, 0, 0);
		body.setGravity(vec1);
	}

	public function enableGravity() {
		body.setGravity(physics.world.getGravity());
	}

	public function setGravity(v:Vec4) {
		vec1.setValue(v.x, v.y, v.z);
		body.setGravity(vec1);
	}

	public function setActivationState(newState:Int) {
		var bodyColl:bullet.CollisionObject = body;
		bodyColl.setActivationState(newState);
	}

	public function setDeactivationParams(linearThreshold:Float, angularThreshold:Float, time:Float) {
		body.setSleepingThresholds(linearThreshold, angularThreshold);
		// body.setDeactivationTime(time); // not available in ammo
	}

	public function applyForce(force:Vec4, loc:Vec4 = null) {
		activate();
		vec1.setValue(force.x, force.y, force.z);
		if (loc == null) {
			body.applyCentralForce(vec1);
		}
		else {
			vec2.setValue(loc.x, loc.y, loc.z);
			body.applyForce(vec1, vec2);
		}
	}

	public function applyImpulse(impulse:Vec4, loc:Vec4 = null) {
		activate();
		vec1.setValue(impulse.x, impulse.y, impulse.z);
		if (loc == null) {
			body.applyCentralImpulse(vec1);
		}
		else {
			vec2.setValue(loc.x, loc.y, loc.z);
			body.applyImpulse(vec1, vec2);
		}
	}

	public function applyTorque(torque:Vec4) {
		activate();
		vec1.setValue(torque.x, torque.y, torque.z);
		body.applyTorque(vec1);
	}

	public function applyTorqueImpulse(torque:Vec4) {
		activate();
		vec1.setValue(torque.x, torque.y, torque.z);
		body.applyTorqueImpulse(vec1);
	}

	public function setLinearFactor(x:Float, y:Float, z:Float) {
		vec1.setValue(x, y, z);
		body.setLinearFactor(vec1);
	}

	public function setAngularFactor(x:Float, y:Float, z:Float) {
		vec1.setValue(x, y, z);
		body.setAngularFactor(vec1);
	}

	public function getLinearVelocity():Vec4 {
		var v = body.getLinearVelocity();
		return new Vec4(v.x(), v.y(), v.z());
	}

	public function setLinearVelocity(x:Float, y:Float, z:Float) {
		vec1.setValue(x, y, z);
		body.setLinearVelocity(vec1);
	}

	public function getAngularVelocity():Vec4 {
		var v = body.getAngularVelocity();
		return new Vec4(v.x(), v.y(), v.z());
	}

	public function setAngularVelocity(x:Float, y:Float, z:Float) {
		vec1.setValue(x, y, z);
		body.setAngularVelocity(vec1);
	}

	public function setFriction(f:Float) {
		var bodyColl:bullet.CollisionObject = body;
		bodyColl.setFriction(f);
		// bodyColl.setRollingFriction(f);
		this.friction = f;
	}

	public function notifyOnContact(f:RigidBody->Void) {
		if (onContact == null) onContact = [];
		onContact.push(f);
	}

	public function removeContact(f:RigidBody->Void) {
		onContact.remove(f);
	}

	function setScale(v:Vec4) {
		currentScaleX = v.x;
		currentScaleY = v.y;
		currentScaleZ = v.z;
		vec1.setX(v.x / bodyScaleX);
		vec1.setY(v.y / bodyScaleY);
		vec1.setZ(v.z / bodyScaleZ);
		btshape.setLocalScaling(vec1);
		var worldDyn:bullet.DynamicsWorld = physics.world;
		var worldCol:bullet.CollisionWorld = worldDyn;
		worldCol.updateSingleAabb(body);
	}

	public function syncTransform() {
		var t = transform;
		t.buildMatrix();
		vec1.setValue(t.worldx(), t.worldy(), t.worldz());
		trans1.setOrigin(vec1);
		quat.fromMat(t.world);
		quat1.setValue(quat.x, quat.y, quat.z, quat.w);
		trans1.setRotation(quat1);
		body.setCenterOfMassTransform(trans1);
		if (currentScaleX != t.scale.x || currentScaleY != t.scale.y || currentScaleZ != t.scale.z) setScale(t.scale);
		activate();
	}

	// Continuous collision detection
	public function setCcd(sphereRadius:Float, motionThreshold = 1e-7) {
		var bodyColl:bullet.CollisionObject = body;
		bodyColl.setCcdSweptSphereRadius(sphereRadius);
		bodyColl.setCcdMotionThreshold(motionThreshold);
	}

	function fillConvexHull(scale:Vec4, margin:kha.FastFloat):bullet.ConvexHullShape {
		// Check whether shape already exists
		var data = cast(object, MeshObject).data;
		var shape = convexHullCache.get(data);
		if (shape != null) {
			usersCache.set(data, usersCache.get(data) + 1);
			return shape;
		}
		
		shape = new bullet.ConvexHullShape();
		convexHullCache.set(data, shape);
		usersCache.set(data, 1);

		var positions = data.geom.positions;

		var sx:kha.FastFloat = scale.x * (1.0 - margin) * (1 / 32767);
		var sy:kha.FastFloat = scale.y * (1.0 - margin) * (1 / 32767);
		var sz:kha.FastFloat = scale.z * (1.0 - margin) * (1 / 32767);

		if (data.raw.scale_pos != null) {
			sx *= data.raw.scale_pos;
			sy *= data.raw.scale_pos;
			sz *= data.raw.scale_pos;
		}

		for (i in 0...Std.int(positions.length / 4)) {
			vec1.setX(positions[i * 4    ] * sx);
			vec1.setY(positions[i * 4 + 1] * sy);
			vec1.setZ(positions[i * 4 + 2] * sz);
			shape.addPoint(vec1, true);
		}
		return shape;
	}

	function fillTriangleMesh(scale:Vec4):bullet.TriangleMesh {
		// Check whether shape already exists
		var data = cast(object, MeshObject).data;
		var triangleMesh = triangleMeshCache.get(data);
		if (triangleMesh != null) {
			usersCache.set(data, usersCache.get(data) + 1);
			return triangleMesh;
		}
		
		triangleMesh = new bullet.TriangleMesh(true, true);
		triangleMeshCache.set(data, triangleMesh);
		usersCache.set(data, 1);

		var positions = data.geom.positions;
		var indices = data.geom.indices;

		var sx:kha.FastFloat = scale.x * (1 / 32767);
		var sy:kha.FastFloat = scale.y * (1 / 32767);
		var sz:kha.FastFloat = scale.z * (1 / 32767);

		if (data.raw.scale_pos != null) {
			sx *= data.raw.scale_pos;
			sy *= data.raw.scale_pos;
			sz *= data.raw.scale_pos;
		}

		for (ar in indices) {
			for (i in 0...Std.int(ar.length / 3)) {
				vec1.setX(positions[ar[i * 3    ] * 4    ] * sx);
				vec1.setY(positions[ar[i * 3    ] * 4 + 1] * sy);
				vec1.setZ(positions[ar[i * 3    ] * 4 + 2] * sz);
				vec2.setX(positions[ar[i * 3 + 1] * 4    ] * sx);
				vec2.setY(positions[ar[i * 3 + 1] * 4 + 1] * sy);
				vec2.setZ(positions[ar[i * 3 + 1] * 4 + 2] * sz);
				vec3.setX(positions[ar[i * 3 + 2] * 4    ] * sx);
				vec3.setY(positions[ar[i * 3 + 2] * 4 + 1] * sy);
				vec3.setZ(positions[ar[i * 3 + 2] * 4 + 2] * sz);
				triangleMesh.addTriangle(vec1, vec2, vec3);
			}
		}
		return triangleMesh;
	}

	public function delete() {
		motionState.delete();
		body.delete();

		// Delete shape if no other user is found
		if (shape == Shape.ConvexHull || shape == Shape.Mesh) {
			var data = cast(object, MeshObject).data;
			var i = usersCache.get(data) - 1;
			usersCache.set(data, i);
			if (i <= 0) {
				deleteShape();
				shape == Shape.ConvexHull ?
					convexHullCache.remove(data) :
					triangleMeshCache.remove(data);
			}
		}
		else deleteShape();
	}

	inline function deleteShape() {
		btshape.delete();
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
