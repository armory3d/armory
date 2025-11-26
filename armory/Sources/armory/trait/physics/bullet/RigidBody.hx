package armory.trait.physics.bullet;

#if arm_bullet
import armory.math.Helper;
import iron.data.MeshData;
import iron.math.Vec4;
import iron.math.Quat;
import iron.object.Transform;
import iron.object.MeshObject;
import iron.system.Time;

/**
   RigidBody is used to allow objects to interact with Physics in your game including collisions and gravity.
   RigidBody can also be used with the getContacts method to detect collisions and run appropriate code.
   The Bullet physics engine is used for these calculations.
**/
@:access(armory.trait.physics.bullet.PhysicsWorld)
class RigidBody extends iron.Trait {

	var shape: Shape;
	public var physics: PhysicsWorld;
	public var transform: Transform = null;
	public var mass: Float;
	public var friction: Float;
	public var angularFriction: Float;
	public var restitution: Float;
	public var collisionMargin: Float;
	public var linearDamping: Float;
	public var angularDamping: Float;
	public var animated: Bool;
	public var staticObj: Bool;
	public var destroyed = false;
	var linearFactors: Array<Float>;
	var angularFactors: Array<Float>;
	var useDeactivation: Bool;
	var deactivationParams: Array<Float>;
	var ccd = false; // Continuous collision detection
	public var group = 1;
	public var mask = 1;
	var trigger = false;
	var bodyScaleX: Float; // Transform scale at creation time
	var bodyScaleY: Float;
	var bodyScaleZ: Float;
	var currentScaleX: Float;
	var currentScaleY: Float;
	var currentScaleZ: Float;
	var meshInterface: bullet.Bt.TriangleMesh;

	public var body: bullet.Bt.RigidBody = null;
	public var motionState: bullet.Bt.MotionState;
	public var btshape: bullet.Bt.CollisionShape;
	public var ready = false;
	static var nextId = 0;
	public var id = 0;
	public var onReady: Void->Void = null;
	public var onContact: Array<RigidBody->Void> = null;
	public var heightData: haxe.io.Bytes = null;
	#if js
	static var ammoArray: Int = -1;
	#end

	static var nullvec = true;
	static var vec1: bullet.Bt.Vector3;
	static var vec2: bullet.Bt.Vector3;
	static var vec3: bullet.Bt.Vector3;
	static var quat1: bullet.Bt.Quaternion;
	static var trans1: bullet.Bt.Transform;
	static var trans2: bullet.Bt.Transform;
	static var quat = new Quat();

	static var CF_STATIC_OBJECT = 1;
	static var CF_KINEMATIC_OBJECT = 2;
	static var CF_NO_CONTACT_RESPONSE = 4;
	static var CF_CHARACTER_OBJECT = 16;

	static var convexHullCache = new Map<MeshData, bullet.Bt.ConvexHullShape>();
	static var triangleMeshCache = new Map<MeshData, bullet.Bt.TriangleMesh>();
	static var usersCache = new Map<MeshData, Int>();

	// Interpolation
	var interpolate: Bool = false;
	var time: Float = 0.0;
	var currentPos: bullet.Bt.Vector3 = new bullet.Bt.Vector3(0, 0, 0);
	var prevPos: bullet.Bt.Vector3 = new bullet.Bt.Vector3(0, 0, 0);
	var currentRot: bullet.Bt.Quaternion = new bullet.Bt.Quaternion(0, 0, 0, 1);
	var prevRot: bullet.Bt.Quaternion = new bullet.Bt.Quaternion(0, 0, 0, 1);

	public function new(shape = Shape.Box, mass = 1.0, friction = 0.5, restitution = 0.0, group = 1, mask = 1,
						params: RigidBodyParams = null, flags: RigidBodyFlags = null) {
		super();

		if (nullvec) {
			nullvec = false;
			vec1 = new bullet.Bt.Vector3(0, 0, 0);
			vec2 = new bullet.Bt.Vector3(0, 0, 0);
			vec3 = new bullet.Bt.Vector3(0, 0, 0);
			quat1 = new bullet.Bt.Quaternion(0, 0, 0, 1);
			trans1 = new bullet.Bt.Transform();
			trans2 = new bullet.Bt.Transform();
		}

		this.shape = shape;
		this.mass = mass;
		this.friction = friction;
		this.restitution = restitution;
		this.group = group;
		this.mask = mask;

		if (params == null) params = {
			linearDamping: 0.04,
			angularDamping: 0.1,
			angularFriction: 0.1,
			linearFactorsX: 1.0,
			linearFactorsY: 1.0,
			linearFactorsZ: 1.0,
			angularFactorsX: 1.0,
			angularFactorsY: 1.0,
			angularFactorsZ: 1.0,
			collisionMargin: 0.0,
			linearDeactivationThreshold: 0.0,
			angularDeactivationThrshold: 0.0,
			deactivationTime: 0.0
		};

		if (flags == null) flags = {
			animated: false,
			trigger: false,
			ccd: false,
			interpolate: false,
			staticObj: false,
			useDeactivation: true
		};

		this.linearDamping = params.linearDamping;
		this.angularDamping = params.angularDamping;
		this.angularFriction = params.angularFriction;
		this.linearFactors = [params.linearFactorsX, params.linearFactorsY, params.linearFactorsZ];
		this.angularFactors = [params.angularFactorsX, params.angularFactorsY, params.angularFactorsZ];
		this.collisionMargin = params.collisionMargin;
		this.deactivationParams = [params.linearDeactivationThreshold, params.angularDeactivationThrshold, params.deactivationTime];
		this.animated = flags.animated;
		this.trigger = flags.trigger;
		this.ccd = flags.ccd;
		this.interpolate = flags.interpolate;
		this.staticObj = flags.staticObj;
		this.useDeactivation = flags.useDeactivation;

		notifyOnAdd(init);
	}

	inline function withMargin(f: Float) {
		return f + f * collisionMargin;
	}

	public function notifyOnReady(f: Void->Void) {
		onReady = f;
		if (ready) onReady();
	}

	public function init() {
		if (ready) return;
		ready = true;

		if (!Std.isOfType(object, MeshObject)) return; // No mesh data

		transform = object.transform;
		transform.buildMatrix();
		physics = armory.trait.physics.PhysicsWorld.active;

		if (shape == Shape.Box) {
			vec1.setX(withMargin(transform.dim.x / 2));
			vec1.setY(withMargin(transform.dim.y / 2));
			vec1.setZ(withMargin(transform.dim.z / 2));
			btshape = new bullet.Bt.BoxShape(vec1);
		}
		else if (shape == Shape.Sphere) {
			btshape = new bullet.Bt.SphereShape(withMargin(transform.dim.x / 2));
		}
		else if (shape == Shape.ConvexHull) {
			var shapeConvex = fillConvexHull(transform.scale, collisionMargin);
			btshape = shapeConvex;
		}
		else if (shape == Shape.Cone) {
			var coneZ = new bullet.Bt.ConeShapeZ(
				withMargin(transform.dim.x / 2), // Radius
				withMargin(transform.dim.z));	  // Height
			var cone: bullet.Bt.ConeShape = coneZ;
			btshape = cone;
		}
		else if (shape == Shape.Cylinder) {
			vec1.setX(withMargin(transform.dim.x / 2));
			vec1.setY(withMargin(transform.dim.y / 2));
			vec1.setZ(withMargin(transform.dim.z / 2));
			var cylZ = new bullet.Bt.CylinderShapeZ(vec1);
			var cyl: bullet.Bt.CylinderShape = cylZ;
			btshape = cyl;
		}
		else if (shape == Shape.Capsule) {
			var r = transform.dim.x / 2;
			var capsZ = new bullet.Bt.CapsuleShapeZ(
				withMargin(r), // Radius
				withMargin(transform.dim.z - r * 2)); // Height between 2 sphere centers
			var caps: bullet.Bt.CapsuleShape = capsZ;
			btshape = caps;
		}
		else if (shape == Shape.Mesh) {
			meshInterface = fillTriangleMesh(transform.scale);
			if (mass > 0) {
				var shapeGImpact = new bullet.Bt.GImpactMeshShape(meshInterface);
				shapeGImpact.updateBound();
				var shapeConcave: bullet.Bt.ConcaveShape = shapeGImpact;
				btshape = shapeConcave;
				if (!physics.gimpactRegistered) {
					#if js
					new bullet.Bt.GImpactCollisionAlgorithm().registerAlgorithm(physics.dispatcher);
					#else
					shapeGImpact.registerAlgorithm(physics.dispatcher);
					#end
					physics.gimpactRegistered = true;
				}
			}
			else {
				var shapeBvh = new bullet.Bt.BvhTriangleMeshShape(meshInterface, true, true);
				var shapeTri: bullet.Bt.TriangleMeshShape = shapeBvh;
				var shapeConcave: bullet.Bt.ConcaveShape = shapeTri;
				btshape = shapeConcave;
			}
		}
		else if (shape == Shape.Terrain) {
			#if js
			var length = heightData.length;
			if (ammoArray == -1) {
				ammoArray = bullet.Bt.Ammo._malloc(length);
			}
			// From texture bytes
			for (i in 0...length) {
				bullet.Bt.Ammo.HEAPU8[ammoArray + i] = heightData.get(i);
			}
			var slice = Std.int(Math.sqrt(length)); // Assuming square terrain data
			var axis = 2; // z
			var dataType = 5; // u8
			btshape = new bullet.Bt.HeightfieldTerrainShape(slice, slice, ammoArray, 1 / 255, 0, 1, axis, dataType, false);
			vec1.setX(transform.dim.x / slice);
			vec1.setY(transform.dim.y / slice);
			vec1.setZ(transform.dim.z);
			btshape.setLocalScaling(vec1);
			#end
		}

		trans1.setIdentity();
		vec1.setX(transform.worldx());
		vec1.setY(transform.worldy());
		vec1.setZ(transform.worldz());
		trans1.setOrigin(vec1);
		quat.fromMat(transform.world);
		quat1.setValue(quat.x, quat.y, quat.z, quat.w);
		trans1.setRotation(quat1);

		currentPos.setValue(vec1.x(), vec1.y(), vec1.z());
		currentRot.setValue(quat.x, quat.y, quat.z, quat.w);

		var centerOfMassOffset = trans2;
		centerOfMassOffset.setIdentity();
		motionState = new bullet.Bt.DefaultMotionState(trans1, centerOfMassOffset);

		vec1.setX(0);
		vec1.setY(0);
		vec1.setZ(0);
		var inertia = vec1;

		if (staticObj || animated) mass = 0;
		if (mass > 0) btshape.calculateLocalInertia(mass, inertia);
		var bodyCI = new bullet.Bt.RigidBodyConstructionInfo(mass, motionState, btshape, inertia);
		body = new bullet.Bt.RigidBody(bodyCI);

		var bodyColl: bullet.Bt.CollisionObject = body;
		bodyColl.setFriction(friction);
		bodyColl.setRollingFriction(angularFriction);
		bodyColl.setRestitution(restitution);

		if (useDeactivation) {
			setDeactivationParams(deactivationParams[0], deactivationParams[1], deactivationParams[2]);
		}
		else {
			setActivationState(bullet.Bt.CollisionObjectActivationState.DISABLE_DEACTIVATION);
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

		if (trigger) bodyColl.setCollisionFlags(bodyColl.getCollisionFlags() | CF_NO_CONTACT_RESPONSE);
		if (animated) {
			bodyColl.setCollisionFlags(bodyColl.getCollisionFlags() | CF_KINEMATIC_OBJECT);
			bodyColl.setCollisionFlags(bodyColl.getCollisionFlags() & ~CF_STATIC_OBJECT);
		}
		if (staticObj && !animated) bodyColl.setCollisionFlags(bodyColl.getCollisionFlags() | CF_STATIC_OBJECT);

		if (ccd) setCcd(transform.radius);

		bodyScaleX = currentScaleX = transform.scale.x;
		bodyScaleY = currentScaleY = transform.scale.y;
		bodyScaleZ = currentScaleZ = transform.scale.z;

		id = nextId;
		nextId++;

		#if js
		//body.setUserIndex(nextId);
		untyped body.userIndex = id;
		#else
		bodyColl.setUserIndex(id);
		#end

		physics.addRigidBody(this);
		notifyOnRemove(removeFromWorld);
		if (!animated) notifyOnUpdate(update);

		if (onReady != null) onReady();

		#if js
		bullet.Bt.Ammo.destroy(bodyCI);
		#else
		bodyCI.delete();
		#end
	}

	function update() {
		if (interpolate) {
			time += Time.delta;

			while (time >= Time.fixedStep) {
				time -= Time.fixedStep;
			}

			var t: Float = time / Time.fixedStep;
			t = Helper.clamp(t, 0, 1);

			var tx: Float = prevPos.x() * (1.0 - t) + currentPos.x() * t;
			var ty: Float = prevPos.y() * (1.0 - t) + currentPos.y() * t;
			var tz: Float = prevPos.z() * (1.0 - t) + currentPos.z() * t;

			var tRot: bullet.Bt.Quaternion = nlerp(prevRot, currentRot, t);

			transform.loc.set(tx, ty, tz, 1.0);
			transform.rot.set(tRot.x(), tRot.y(), tRot.z(), tRot.w());
		} else {
			transform.loc.set(currentPos.x(), currentPos.y(), currentPos.z(), 1.0);
			transform.rot.set(currentRot.x(), currentRot.y(), currentRot.z(), currentRot.w());
		}

		if (object.parent != null) {
			var ptransform = object.parent.transform;
			transform.loc.x -= ptransform.worldx();
			transform.loc.y -= ptransform.worldy();
			transform.loc.z -= ptransform.worldz();
		}

		transform.buildMatrix();
	}

	function nlerp(q1: bullet.Bt.Quaternion, q2: bullet.Bt.Quaternion, t: Float): bullet.Bt.Quaternion {
		var dot = q1.x() * q2.x() + q1.y() * q2.y() + q1.z() * q2.z() + q1.w() * q2.w();
		var _q2 = dot < 0 ? new bullet.Bt.Quaternion(-q2.x(), -q2.y(), -q2.z(), -q2.w()) : q2;

		var x = q1.x() * (1.0 - t) + _q2.x() * t;
		var y = q1.y() * (1.0 - t) + _q2.y() * t;
		var z = q1.z() * (1.0 - t) + _q2.z() * t;
		var w = q1.w() * (1.0 - t) + _q2.w() * t;

		var len = Math.sqrt(x * x + y * y + z * z + w * w);
		return new bullet.Bt.Quaternion(x / len, y / len, z / len, w / len);
	}

	function physicsUpdate() {
		if (!ready) return;

		if (animated) {
			syncTransform();
		} else {
			if (interpolate) {
				prevPos.setValue(currentPos.x(), currentPos.y(), currentPos.z());
				prevRot.setValue(currentRot.x(), currentRot.y(), currentRot.z(), currentRot.w());
			}

			var trans = body.getWorldTransform();
			var p = trans.getOrigin();
			var q = trans.getRotation();

			currentPos.setValue(p.x(), p.y(), p.z());
			currentRot.setValue(q.x(), q.y(), q.z(), q.w());

			#if hl
			p.delete();
			q.delete();
			trans.delete();
			#end
		}

		if (onContact != null) {
			var rbs = physics.getContacts(this);
			if (rbs != null) for (rb in rbs) for (f in onContact) f(rb);
		}
	}

	public function disableCollision() {
		var bodyColl: bullet.Bt.CollisionObject = body;
		bodyColl.setCollisionFlags(bodyColl.getCollisionFlags() | CF_NO_CONTACT_RESPONSE);
	}

	public function enableCollision() {
		var bodyColl: bullet.Bt.CollisionObject = body;
		bodyColl.setCollisionFlags(~bodyColl.getCollisionFlags() & CF_NO_CONTACT_RESPONSE);
	}

	public function removeFromWorld() {
		if (physics != null) physics.removeRigidBody(this);
	}

	public function isActive() : Bool {
		return body.isActive();
	}

	public function activate() {
		var bodyColl: bullet.Bt.CollisionObject = body;
		bodyColl.activate(false);
	}

	public function disableGravity() {
		vec1.setValue(0, 0, 0);
		body.setGravity(vec1);
	}

	public function enableGravity() {
		body.setGravity(physics.world.getGravity());
	}

	public function setGravity(v: Vec4) {
		vec1.setValue(v.x, v.y, v.z);
		body.setGravity(vec1);
	}

	public function setActivationState(newState: Int) {
		var bodyColl: bullet.Bt.CollisionObject = body;
		bodyColl.setActivationState(newState);
	}

	public function setDeactivationParams(linearThreshold: Float, angularThreshold: Float, time: Float) {
		body.setSleepingThresholds(linearThreshold, angularThreshold);
		// body.setDeactivationTime(time); // not available in ammo
	}

	public function setUpDeactivation(useDeactivation: Bool, linearThreshold: Float, angularThreshold: Float, time: Float) {
		this.useDeactivation = useDeactivation;
		this.deactivationParams[0] = linearThreshold;
		this.deactivationParams[1] = angularThreshold;
		this.deactivationParams[2] = time;
	}

	public function isTriggerObject(isTrigger: Bool) {
		this.trigger = isTrigger;
	}

	public function applyForce(force: Vec4, loc: Vec4 = null) {
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

	public function applyImpulse(impulse: Vec4, loc: Vec4 = null) {
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

	public function applyTorque(torque: Vec4) {
		activate();
		vec1.setValue(torque.x, torque.y, torque.z);
		body.applyTorque(vec1);
	}

	public function applyTorqueImpulse(torque: Vec4) {
		activate();
		vec1.setValue(torque.x, torque.y, torque.z);
		body.applyTorqueImpulse(vec1);
	}

	public function setLinearFactor(x: Float, y: Float, z: Float) {
		vec1.setValue(x, y, z);
		body.setLinearFactor(vec1);
	}

	public function setAngularFactor(x: Float, y: Float, z: Float) {
		vec1.setValue(x, y, z);
		body.setAngularFactor(vec1);
	}

	public function getLinearVelocity(): Vec4 {
		var v = body.getLinearVelocity();
		return new Vec4(v.x(), v.y(), v.z());
	}

	public function setLinearVelocity(x: Float, y: Float, z: Float) {
		vec1.setValue(x, y, z);
		body.setLinearVelocity(vec1);
	}

	public function getAngularVelocity(): Vec4 {
		var v = body.getAngularVelocity();
		return new Vec4(v.x(), v.y(), v.z());
	}

	public function setAngularVelocity(x: Float, y: Float, z: Float) {
		vec1.setValue(x, y, z);
		body.setAngularVelocity(vec1);
	}

	public function getPointVelocity(x: Float, y: Float, z: Float) {
		var linear = getLinearVelocity();

		var relativePoint = new Vec4(x, y, z).sub(transform.world.getLoc());
		var angular = getAngularVelocity().cross(relativePoint);

		return linear.add(angular);
	}

	public function setFriction(f: Float) {
		var bodyColl: bullet.Bt.CollisionObject = body;
		bodyColl.setFriction(f);
		// bodyColl.setRollingFriction(f);
		this.friction = f;
	}

	public function notifyOnContact(f: RigidBody->Void) {
		if (onContact == null) onContact = [];
		onContact.push(f);
	}

	public function removeContact(f: RigidBody->Void) {
		onContact.remove(f);
	}

	function setScale(v: Vec4) {
		currentScaleX = v.x;
		currentScaleY = v.y;
		currentScaleZ = v.z;
		vec1.setX(v.x / bodyScaleX);
		vec1.setY(v.y / bodyScaleY);
		vec1.setZ(v.z / bodyScaleZ);
		btshape.setLocalScaling(vec1);
		var worldDyn: bullet.Bt.DynamicsWorld = physics.world;
		var worldCol: bullet.Bt.CollisionWorld = worldDyn;
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
		if (animated) body.getMotionState().setWorldTransform(trans1);
		else body.setCenterOfMassTransform(trans1);
		if (currentScaleX != t.scale.x || currentScaleY != t.scale.y || currentScaleZ != t.scale.z) setScale(t.scale);
		activate();
	}

	public function setGroup(group: Int) {
		if (this.group == group) return;
		this.group = group;
		physics.updateRigidBody(this);
	}

	public function setMask(mask: Int) {
		if (this.mask == mask) return;
		this.mask = mask;
		physics.updateRigidBody(this);
	}

	// Continuous collision detection
	public function setCcd(sphereRadius: Float, motionThreshold = 1e-7) {
		var bodyColl: bullet.Bt.CollisionObject = body;
		bodyColl.setCcdSweptSphereRadius(sphereRadius);
		bodyColl.setCcdMotionThreshold(motionThreshold);
	}

	function fillConvexHull(scale: Vec4, margin: kha.FastFloat): bullet.Bt.ConvexHullShape {
		// Check whether shape already exists
		var data = cast(object, MeshObject).data;
		var shape = convexHullCache.get(data);
		if (shape != null) {
			usersCache.set(data, usersCache.get(data) + 1);
			return shape;
		}

		shape = new bullet.Bt.ConvexHullShape();
		convexHullCache.set(data, shape);
		usersCache.set(data, 1);

		var positions = data.geom.positions.values;

		var sx: kha.FastFloat = scale.x * (1.0 - margin) * (1 / 32767);
		var sy: kha.FastFloat = scale.y * (1.0 - margin) * (1 / 32767);
		var sz: kha.FastFloat = scale.z * (1.0 - margin) * (1 / 32767);

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

	function fillTriangleMesh(scale: Vec4): bullet.Bt.TriangleMesh {
		// Check whether shape already exists
		var data = cast(object, MeshObject).data;
		var triangleMesh = triangleMeshCache.get(data);
		if (triangleMesh != null) {
			usersCache.set(data, usersCache.get(data) + 1);
			return triangleMesh;
		}

		triangleMesh = new bullet.Bt.TriangleMesh(true, true);
		triangleMeshCache.set(data, triangleMesh);
		usersCache.set(data, 1);

		var positions = data.geom.positions.values;
		var indices = data.geom.indices;

		var sx: kha.FastFloat = scale.x * (1 / 32767);
		var sy: kha.FastFloat = scale.y * (1 / 32767);
		var sz: kha.FastFloat = scale.z * (1 / 32767);

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
		#if js
		bullet.Bt.Ammo.destroy(motionState);
		bullet.Bt.Ammo.destroy(body);
		#else
		motionState.delete();
		body.delete();
		#end

		// Delete shape if no other user is found
		if (shape == Shape.ConvexHull || shape == Shape.Mesh) {
			var data = cast(object, MeshObject).data;
			var i = usersCache.get(data) - 1;
			usersCache.set(data, i);
			if(shape == Shape.Mesh) deleteShape();
			if (i <= 0) {
				if(shape == Shape.ConvexHull)
				{
					deleteShape();
					convexHullCache.remove(data);
				}
				else
				{
					triangleMeshCache.remove(data);
					if(meshInterface != null)
					{
						#if js
						bullet.Bt.Ammo.destroy(meshInterface);
						#else
						meshInterface.delete();
						#end
					}
				}
			}
		}
		else deleteShape();
	}

	inline function deleteShape() {
		#if js
		bullet.Bt.Ammo.destroy(btshape);
		#else
		btshape.delete();
		#end
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

typedef RigidBodyParams = {
	var linearDamping: Float;
	var angularDamping: Float;
	var angularFriction: Float;
	var linearFactorsX: Float;
	var linearFactorsY: Float;
	var linearFactorsZ: Float;
	var angularFactorsX: Float;
	var angularFactorsY: Float;
	var angularFactorsZ: Float;
	var collisionMargin: Float;
	var linearDeactivationThreshold: Float;
	var angularDeactivationThrshold: Float;
	var deactivationTime: Float;
}

typedef RigidBodyFlags = {
	var animated: Bool;
	var trigger: Bool;
	var ccd: Bool;
	var interpolate: Bool;
	var staticObj: Bool;
	var useDeactivation: Bool;
}
#end
