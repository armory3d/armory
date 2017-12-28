package armory.trait.physics.bullet;

#if arm_bullet

import haxebullet.Bullet;
import iron.Trait;
import iron.math.Vec4;
import iron.object.Transform;
import iron.object.MeshObject;

class KinematicCharacterController extends Trait {

	var shape:ControllerShape;
	var _shapeConvex:BtConvexShapePointer;
	var _shapeConvexHull:BtConvexHullShapePointer;
	var isConvexHull = false;

	public var physics:PhysicsWorld;
	public var transform:Transform = null;

	public var mass:Float;
	public var friction:Float;
	public var restitution:Float;
	public var collisionMargin:Float;
	public var animated:Bool;
	public var group = 1;
	var bodyScaleX:Float; // Transform scale at creation time
	var bodyScaleY:Float;
	var bodyScaleZ:Float;
	var currentScaleX:Float;
	var currentScaleY:Float;
	var currentScaleZ:Float;
	var jumpSpeed:Float;

	public var body:BtPairCachingGhostObjectPointer = null;
	public var character:BtKinematicCharacterControllerPointer = null;
	public var ready = false;

	static var nextId = 0;
	public var id = 0;

	public var onReady:Void->Void = null;

	public function new(mass = 1.0, shape = ControllerShape.Capsule, jumpSpeed = 8.0, friction = 0.5, restitution = 0.0,
						collisionMargin = 0.0, animated = false, group = 1) {
		super();

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
	
	inline function withMargin(f:Float):Float {
		return f - f * collisionMargin;
	}

	public function notifyOnReady(f:Void->Void):Void {
		onReady = f;
		if (ready) onReady();
	}

	public function init():Void {
		if (ready) return;
		ready = true;
		
		transform = object.transform;
		physics = armory.trait.physics.PhysicsWorld.active;

		_shapeConvex = null;
		_shapeConvexHull = null;
		isConvexHull = false;

		if (shape == ControllerShape.Box) {
			_shapeConvex = BtBoxShape.create(BtVector3.create(
				withMargin(transform.dim.x / 2),
				withMargin(transform.dim.y / 2),
				withMargin(transform.dim.z / 2)));
		}
		else if (shape == ControllerShape.Sphere) {
			var width = transform.dim.x;
			if(transform.dim.y > width) width = transform.dim.y;
			if(transform.dim.z > width) width = transform.dim.z;
			_shapeConvex = BtSphereShape.create(withMargin(width / 2));
		}
		else if (shape == ControllerShape.ConvexHull && mass > 0) {
			_shapeConvexHull = BtConvexHullShape.create();
			isConvexHull = true;
			addPointsToConvexHull(_shapeConvexHull, transform.scale, collisionMargin);
		}
		else if (shape == ControllerShape.Cone) {
			_shapeConvex = BtConeShapeZ.create(
				withMargin(transform.dim.x / 2), // Radius
				withMargin(transform.dim.z));	 // Height
		}
		else if (shape == ControllerShape.Cylinder) {
			_shapeConvex = BtCylinderShapeZ.create(BtVector3.create(
				withMargin(transform.dim.x / 2),
				withMargin(transform.dim.y / 2),
				withMargin(transform.dim.z / 2)));
		}
		else if (shape == ControllerShape.Capsule) {
			var r = transform.dim.x / 2;
			_shapeConvex = BtCapsuleShapeZ.create(
				withMargin(r), // Radius
				withMargin(transform.dim.z - r * 2)); // Height between 2 sphere centers
		}

		var _transform = BtTransform.create();
		_transform.setIdentity();
		_transform.setOrigin(BtVector3.create(transform.worldx(), transform.worldy(), transform.worldz()));
		var rot = transform.world.getQuat();
		_transform.setRotation(BtQuaternion.create(rot.x, rot.y, rot.z, rot.w));

		body = BtPairCachingGhostObject.create();
		body.setCollisionShape(isConvexHull ? _shapeConvexHull : _shapeConvex);
		body.setCollisionFlags(BtCollisionObject.CF_CHARACTER_OBJECT);
		body.setWorldTransform(_transform);
		body.setFriction(friction);
		body.setRollingFriction(friction);
		body.setRestitution(restitution);
		#if js
		character = BtKinematicCharacterController.create(body, isConvexHull ? _shapeConvexHull : _shapeConvex, 0.5, 2);
		#elseif cpp
		character = BtKinematicCharacterController.create(body, isConvexHull ? _shapeConvexHull : _shapeConvex, 0.5, BtVector3.create(0.0, 0.0, 1.0));
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

		physics.addKinematicCharacterController(this);

		if (onReady != null) onReady();
	}

	function lateUpdate():Void {
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

	public function canJump():Bool {
		return character.canJump();
	}

	public function onGround():Bool {
		return character.onGround();
	}

	public function setJumpSpeed(jumpSpeed:Float):Void {
		character.setJumpSpeed(jumpSpeed);
	}

	public function setFallSpeed(fallSpeed:Float):Void {
		character.setFallSpeed(fallSpeed);
	}

	public function setMaxSlope(slopeRadians:Float):Void {
		return character.setMaxSlope(slopeRadians);
	}

	public function getMaxSlope():Float {
		return character.getMaxSlope();
	}

	public function setMaxJumpHeight(maxJumpHeight:Float):Void {
		character.setMaxJumpHeight(maxJumpHeight);
	}

	public function setWalkDirection(walkDirection:Vec4):Void {
		character.setWalkDirection(BtVector3.create(walkDirection.x, walkDirection.y, walkDirection.z));
	}

	public function setUpInterpolate(value:Bool):Void {
		character.setUpInterpolate(value);
	}

	#if js
	public function jump():Void{
		character.jump();
	}
	#elseif cpp
	public function jump(v:Vec4):Void{
		character.jump(BtVector3.create(v.x, v.y, v.z));
	}
	#end

	public function removeFromWorld():Void {
		if (physics != null) physics.removeKinematicCharacterController(this);
	}

	public function activate():Void {
		body.activate(false);
	}

	public function disableGravity():Void {
		#if js
		character.setGravity(0.0);
		#elseif cpp
		character.setGravity(BtVector3.create(0.0, 0.0, 0.0));
		#end
	}

	public function enableGravity():Void {
		#if js
		character.setGravity(Math.abs(physics.world.getGravity().z()) * 3.0); // 9.8 * 3.0 in cpp source code
		#elseif cpp
		character.setGravity(BtVector3.create(physics.world.getGravity().x() * 3.0, physics.world.getGravity().y() * 3.0, physics.world.getGravity().z() * 3.0));
		#end
	}

	#if js
	public function setGravity(f:Float):Void {
		character.setGravity(f);
	}
	#elseif cpp
	public function setGravity(v:Vec4):Void {
		character.setGravity(BtVector3.create(v.x, v.y, v.z));
	}
	#end

	public function setActivationState(newState:Int):Void {
		body.setActivationState(newState);
	}

	public function setFriction(f:Float):Void {
		body.setFriction(f);
		body.setRollingFriction(f);
		this.friction = f;
	}

	public function syncTransform():Void {
		var t = transform;
		t.buildMatrix();
		var trans = BtTransform.create();
		trans.setOrigin(BtVector3.create(t.worldx(), t.worldy(), t.worldz()));
		var rot = t.world.getQuat();
		trans.setRotation(BtQuaternion.create(rot.x, rot.y, rot.z, rot.w));
		if (currentScaleX != t.scale.x || currentScaleY != t.scale.y || currentScaleZ != t.scale.z) setScale(t.scale);
		activate();
	}

	function setScale(v:Vec4):Void {
		currentScaleX = v.x;
		currentScaleY = v.y;
		currentScaleZ = v.z;
		if (isConvexHull) _shapeConvexHull.setLocalScaling(BtVector3.create(bodyScaleX * v.x, bodyScaleY * v.y, bodyScaleZ * v.z));
		else _shapeConvex.setLocalScaling(BtVector3.create(bodyScaleX * v.x, bodyScaleY * v.y, bodyScaleZ * v.z));
		physics.world.updateSingleAabb(body);
	}

	function addPointsToConvexHull(shape:BtConvexHullShapePointer, scale:Vec4, margin:Float):Void {
		var positions = cast(object, MeshObject).data.geom.positions;

		var sx = scale.x * (1.0 - margin);
		var sy = scale.y * (1.0 - margin);
		var sz = scale.z * (1.0 - margin);

		for (i in 0...Std.int(positions.length / 3)) {
			shape.addPoint(BtVector3.create(positions[i * 3] * sx, positions[i * 3 + 1] * sy, positions[i * 3 + 2] * sz), true);
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
