package armory.trait.physics.oimo;

#if arm_oimo

import iron.Trait;
import iron.math.Vec4;
import iron.object.Transform;
import iron.object.MeshObject;

class RigidBody extends Trait {

	var shape:Shape;
	public var physics:PhysicsWorld;
	public var transform:Transform = null;

	public var mass:Float;
	public var friction:Float;
	public var restitution:Float;
	public var collisionMargin:Float;
	public var linearDamping:Float;
	public var angularDamping:Float;
	public var passive:Bool;

	public var body:oimo.physics.dynamics.RigidBody = null;
	public var ready = false;

	static var nextId = 0;
	public var id = 0;

	public var onReady:Void->Void = null;

	public function new(mass = 1.0, shape = Shape.Box, friction = 0.5, restitution = 0.0, collisionMargin = 0.0,
						linearDamping = 0.04, angularDamping = 0.1, passive = false) {
		super();

		this.mass = mass;
		this.shape = shape;
		this.friction = friction;
		this.restitution = restitution;
		this.collisionMargin = collisionMargin;
		this.linearDamping = linearDamping;
		this.angularDamping = angularDamping;
		this.passive = passive;

		notifyOnAdd(init);
		notifyOnLateUpdate(lateUpdate);
		notifyOnRemove(removeFromWorld);
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
		
		transform = object.transform;
		physics = armory.trait.physics.PhysicsWorld.active;

		
		var shapeConfig = new oimo.physics.collision.shape.ShapeConfig();
		shapeConfig.friction = friction;
		shapeConfig.restitution = restitution;
		shapeConfig.density = mass > 0 ? mass : 1.0; // todo
		var _shape:oimo.physics.collision.shape.Shape = null;

		if (shape == Shape.Box) {
			_shape = new oimo.physics.collision.shape.BoxShape(shapeConfig, 
				withMargin(transform.size.x),
				withMargin(transform.size.y),
				withMargin(transform.size.z));
		}
		else if (shape == Shape.Sphere) {
			_shape = new oimo.physics.collision.shape.SphereShape(shapeConfig,
				withMargin(transform.size.x / 2));
		}
		else {
			throw "Oimo is restricted to Box and Sphere shapes";
		}

		body = new oimo.physics.dynamics.RigidBody(transform.worldx(), transform.worldy(), transform.worldz());
		body.orientation.x = transform.rot.x;
		body.orientation.y = transform.rot.y;
		body.orientation.z = transform.rot.z;
		body.orientation.s = transform.rot.w;
		body.addShape(_shape);
		body.setupMass(mass > 0 ? oimo.physics.dynamics.RigidBody.BODY_DYNAMIC : oimo.physics.dynamics.RigidBody.BODY_STATIC);

		id = nextId;
		nextId++;

		physics.addRigidBody(this);

		if (onReady != null) onReady();
	}

	function lateUpdate() {
		if (!ready) return;
		if (object.animation != null || passive) {
			syncTransform();
		}
		else {
			var p = body.position;
			var q = body.orientation;
			transform.loc.set(p.x, p.y, p.z);
			transform.rot.set(q.x, q.y, q.z, q.s);
			if (object.parent != null) {
				var ptransform = object.parent.transform;
				transform.loc.x -= ptransform.worldx();
				transform.loc.y -= ptransform.worldy();
				transform.loc.z -= ptransform.worldz();
			}
			transform.buildMatrix();
		}
	}

	public function removeFromWorld() {
		if (physics != null) physics.removeRigidBody(this);
	}

	public function activate() {
		body.awake();
	}

	public function disableGravity() {
	}

	public function setActivationState(newState:Int) {
	}

	public function applyImpulse(impulse:Vec4, loc:Vec4 = null) {
		activate();
		if (loc == null) loc = transform.loc;
		body.applyImpulse(new oimo.math.Vec3(loc.x, loc.y, loc.z), new oimo.math.Vec3(impulse.x, impulse.y, impulse.z));
	}

	public function setLinearFactor(x:Float, y:Float, z:Float) {
	}

	public function setAngularFactor(x:Float, y:Float, z:Float) {
	}

	public function getLinearVelocity():Vec4 {
		return null;
	}

	public function setLinearVelocity(x:Float, y:Float, z:Float) {
	}

	public function setAngularVelocity(x:Float, y:Float, z:Float) {
	}

	public function setFriction(f:Float) {
	//TODO
	}

	public function syncTransform() {
		body.position.x = transform.worldx();
		body.position.y = transform.worldy();
		body.position.z = transform.worldz();
		body.orientation.x = transform.rot.x;
		body.orientation.y = transform.rot.y;
		body.orientation.z = transform.rot.z;
		body.orientation.s = transform.rot.w;
		activate();
	}
}

@:enum abstract Shape(Int) from Int {
	var Box = 0;
	var Sphere = 1;
	var ConvexHull = 2;
	var Mesh = 3;
	var Cone = 4;
	var Cylinder = 5;
	var Capsule = 6;
	var Terrain = 7;
	var StaticMesh = 8;
}

@:enum abstract ActivationState(Int) from Int {
	var Active = 1;
	var NoDeactivation = 4;
	var NoSimulation = 5;
}

#end
