package armory.trait.physics.bullet;

#if arm_bullet

import iron.Trait;
import iron.math.Vec4;
import iron.math.Quat;
import iron.object.Transform;
import iron.object.MeshObject;

class KinematicCharacterController extends Trait {

	var shape: ControllerShape;
	var shapeConvex: bullet.Bt.ConvexShape;
	var shapeConvexHull: bullet.Bt.ConvexHullShape;
	var isConvexHull = false;

	public var physics: PhysicsWorld;
	public var transform: Transform = null;
	public var mass: Float;
	public var friction: Float;
	public var restitution: Float;
	public var collisionMargin: Float;
	public var animated: Bool;
	public var group = 1;
	var bodyScaleX: Float; // Transform scale at creation time
	var bodyScaleY: Float;
	var bodyScaleZ: Float;
	var currentScaleX: Float;
	var currentScaleY: Float;
	var currentScaleZ: Float;
	var jumpSpeed: Float;

	public var body: bullet.Bt.PairCachingGhostObject = null;
	public var character: bullet.Bt.KinematicCharacterController = null;
	public var ready = false;
	static var nextId = 0;
	public var id = 0;
	public var onReady: Void->Void = null;

	static var nullvec = true;
	static var vec1: bullet.Bt.Vector3;
	static var quat1: bullet.Bt.Quaternion;
	static var trans1: bullet.Bt.Transform;
	static var quat = new Quat();

	static inline var CF_CHARACTER_OBJECT = 16;

	public function new(mass = 1.0, shape = ControllerShape.Capsule, jumpSpeed = 8.0, friction = 0.5, restitution = 0.0,
						collisionMargin = 0.0, animated = false, group = 1) {
		super();

		if (nullvec) {
			nullvec = false;
			vec1 = new bullet.Bt.Vector3(0, 0, 0);
			quat1 = new bullet.Bt.Quaternion(0, 0, 0, 0);
			trans1 = new bullet.Bt.Transform();
		}

		this.mass = mass;
		this.jumpSpeed = jumpSpeed;
		this.shape = shape;
		this.friction = friction;
		this.restitution = restitution;
		this.collisionMargin = collisionMargin;
		this.animated = animated;
		this.group = group;

		notifyOnAdd(init);
		notifyOnLateUpdate(lateUpdate);
		notifyOnRemove(removeFromWorld);
	}

	inline function withMargin(f: Float): Float {
		return f + f * collisionMargin;
	}

	public function notifyOnReady(f: Void->Void) {
		onReady = f;
		if (ready) onReady();
	}

	public function init() {
		if (ready) return;
		ready = true;

		transform = object.transform;
		physics = armory.trait.physics.PhysicsWorld.active;

		shapeConvex = null;
		shapeConvexHull = null;
		isConvexHull = false;

		if (shape == ControllerShape.Box) {
			vec1.setX(withMargin(transform.dim.x / 2));
			vec1.setY(withMargin(transform.dim.y / 2));
			vec1.setZ(withMargin(transform.dim.z / 2));
			shapeConvex = new bullet.Bt.BoxShape(vec1);
		}
		else if (shape == ControllerShape.Sphere) {
			var width = transform.dim.x;
			if (transform.dim.y > width) width = transform.dim.y;
			if (transform.dim.z > width) width = transform.dim.z;
			shapeConvex = new bullet.Bt.SphereShape(withMargin(width / 2));
		}
		else if (shape == ControllerShape.ConvexHull && mass > 0) {
			shapeConvexHull = new bullet.Bt.ConvexHullShape();
			isConvexHull = true;
			addPointsToConvexHull(shapeConvexHull, transform.scale, collisionMargin);
		}
		else if (shape == ControllerShape.Cone) {
			shapeConvex = new bullet.Bt.ConeShapeZ(
				withMargin(transform.dim.x / 2), // Radius
				withMargin(transform.dim.z));	 // Height
		}
		else if (shape == ControllerShape.Cylinder) {
			vec1.setX(withMargin(transform.dim.x / 2));
			vec1.setY(withMargin(transform.dim.y / 2));
			vec1.setZ(withMargin(transform.dim.z / 2));
			shapeConvex = new bullet.Bt.CylinderShapeZ(vec1);
		}
		else if (shape == ControllerShape.Capsule) {
			var r = transform.dim.x / 2;
			shapeConvex = new bullet.Bt.CapsuleShapeZ(
				withMargin(r), // Radius
				withMargin(transform.dim.z - r * 2)); // Height between 2 sphere centers
		}

		trans1.setIdentity();
		vec1.setX(transform.worldx());
		vec1.setY(transform.worldy());
		vec1.setZ(transform.worldz());
		trans1.setOrigin(vec1);

		quat.fromMat(transform.world);
		quat1.setX(quat.x);
		quat1.setY(quat.y);
		quat1.setZ(quat.z);
		quat1.setW(quat.w);
		trans1.setRotation(quat1);

		body = new bullet.Bt.PairCachingGhostObject();
		body.setCollisionShape(isConvexHull ? shapeConvexHull : shapeConvex);
		body.setCollisionFlags(CF_CHARACTER_OBJECT);
		body.setWorldTransform(trans1);
		body.setFriction(friction);
		body.setRollingFriction(friction);
		body.setRestitution(restitution);
		#if js
		character = new bullet.Bt.KinematicCharacterController(body, isConvexHull ? shapeConvexHull : shapeConvex, 0.5, 2);
		#elseif cpp
		character = new bullet.Bt.KinematicCharacterController.create(body, isConvexHull ? shapeConvexHull : shapeConvex, 0.5, bullet.Bt.Vector3(0.0, 0.0, 1.0));
		#end
		character.setJumpSpeed(jumpSpeed);
		character.setUseGhostSweepTest(true);

		setActivationState(ControllerActivationState.NoDeactivation);

		bodyScaleX = currentScaleX = transform.scale.x;
		bodyScaleY = currentScaleY = transform.scale.y;
		bodyScaleZ = currentScaleZ = transform.scale.z;

		id = nextId;
		nextId++;

		#if js
		untyped body.userIndex = id;
		#elseif cpp
		body.setUserIndex(id);
		#end

		// physics.addKinematicCharacterController(this);

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
	}

	public function canJump(): Bool {
		return character.canJump();
	}

	public function onGround(): Bool {
		return character.onGround();
	}

	public function setJumpSpeed(jumpSpeed: Float) {
		character.setJumpSpeed(jumpSpeed);
	}

	public function setFallSpeed(fallSpeed: Float) {
		character.setFallSpeed(fallSpeed);
	}

	public function setMaxSlope(slopeRadians: Float) {
		return character.setMaxSlope(slopeRadians);
	}

	public function getMaxSlope(): Float {
		return character.getMaxSlope();
	}

	public function setMaxJumpHeight(maxJumpHeight: Float) {
		character.setMaxJumpHeight(maxJumpHeight);
	}

	public function setWalkDirection(walkDirection: Vec4) {
		vec1.setX(walkDirection.x);
		vec1.setY(walkDirection.y);
		vec1.setZ(walkDirection.z);
		character.setWalkDirection(vec1);
	}

	public function setUpInterpolate(value: Bool) {
		character.setUpInterpolate(value);
	}

	#if js
	public function jump(): Void{
		character.jump();
	}
	#elseif cpp
	public function jump(v: Vec4): Void{
		vec1.setX(v.x);
		vec1.setY(v.y);
		vec1.setZ(v.z);
		character.jump(vec1);
	}
	#end

	public function removeFromWorld() {
		// if (physics != null) physics.removeKinematicCharacterController(this);
	}

	public function activate() {
		body.activate(false);
	}

	public function disableGravity() {
		#if js
		character.setGravity(0.0);
		#elseif cpp
		vec1.setX(0);
		vec1.setY(0);
		vec1.setZ(0);
		character.setGravity(vec1);
		#end
	}

	public function enableGravity() {
		#if js
		character.setGravity(Math.abs(physics.world.getGravity().z()) * 3.0); // 9.8 * 3.0 in cpp source code
		#elseif cpp
		vec1.setX(physics.world.getGravity().x() * 3.0);
		vec1.setY(physics.world.getGravity().y() * 3.0);
		vec1.setZ(physics.world.getGravity().z() * 3.0);
		character.setGravity(vec1);
		#end
	}

	#if js
	public function setGravity(f: Float) {
		character.setGravity(f);
	}
	#elseif cpp
	public function setGravity(v: Vec4) {
		vec1.setX(v.x);
		vec1.setY(v.y);
		vec1.setZ(v.z);
		character.setGravity(vec1);
	}
	#end

	public function setActivationState(newState: Int) {
		body.setActivationState(newState);
	}

	public function setFriction(f: Float) {
		body.setFriction(f);
		body.setRollingFriction(f);
		this.friction = f;
	}

	public function syncTransform() {
		var t = transform;
		t.buildMatrix();
		vec1.setX(t.worldx());
		vec1.setY(t.worldy());
		vec1.setZ(t.worldz());
		trans1.setOrigin(vec1);
		quat.fromMat(t.world);
		quat1.setX(quat.x);
		quat1.setY(quat.y);
		quat1.setZ(quat.z);
		quat1.setW(quat.w);
		trans1.setRotation(quat1);
		//body.setCenterOfMassTransform(trans); // ?
		if (currentScaleX != t.scale.x || currentScaleY != t.scale.y || currentScaleZ != t.scale.z) setScale(t.scale);
		activate();
	}

	function setScale(v: Vec4) {
		currentScaleX = v.x;
		currentScaleY = v.y;
		currentScaleZ = v.z;
		vec1.setX(bodyScaleX * v.x);
		vec1.setY(bodyScaleY * v.y);
		vec1.setZ(bodyScaleZ * v.z);
		if (isConvexHull) shapeConvexHull.setLocalScaling(vec1);
		else shapeConvex.setLocalScaling(vec1);
		physics.world.updateSingleAabb(body);
	}

	function addPointsToConvexHull(shape: bullet.Bt.ConvexHullShape, scale: Vec4, margin: Float) {
		var positions = cast(object, MeshObject).data.geom.positions.values;

		var sx = scale.x * (1.0 - margin);
		var sy = scale.y * (1.0 - margin);
		var sz = scale.z * (1.0 - margin);

		for (i in 0...Std.int(positions.length / 4)) {
			vec1.setX(positions[i * 3] * sx);
			vec1.setY(positions[i * 3 + 1] * sy);
			vec1.setZ(positions[i * 3 + 2] * sz);
			shape.addPoint(vec1, true);
		}
	}
}

@:enum abstract ControllerShape(Int) from Int to Int {
	var Box = 0;
	var Sphere = 1;
	var ConvexHull = 2;
	var Cone = 3;
	var Cylinder = 4;
	var Capsule = 5;
}

@:enum abstract ControllerActivationState(Int) from Int to Int {
	var Active = 1;
	var NoDeactivation = 4;
	var NoSimulation = 5;
}

#end
