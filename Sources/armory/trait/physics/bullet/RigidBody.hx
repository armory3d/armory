package armory.trait.physics.bullet;

#if arm_bullet

import haxebullet.Bullet;
import iron.math.Vec4;
import iron.math.Quat;
import iron.object.Transform;
import iron.object.MeshObject;

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
	var alternatePhysicUpdate = false;
	public var group = 1;
	public var trigger = false;
	var bodyScaleX:Float; // Transform scale at creation time
	var bodyScaleY:Float;
	var bodyScaleZ:Float;
	var currentScaleX:Float;
	var currentScaleY:Float;
	var currentScaleZ:Float;

	public var body:BtRigidBodyPointer = null;
	public var motionState:BtMotionStatePointer;
	public var btshape:BtCollisionShapePointer;
	public var ready = false;
	static var nextId = 0;
	public var id = 0;
	public var onReady:Void->Void = null;
	public var onContact:Array<RigidBody->Void> = null;

	static var nullvec = true;
	static var vec1:BtVector3;
	static var vec2:BtVector3;
	static var vec3:BtVector3;
	static var quat1:BtQuaternion;
	static var trans1:BtTransform;
	static var trans2:BtTransform;
	static var quat = new Quat();

	public function new(mass = 1.0, shape = Shape.Box, friction = 0.5, restitution = 0.0, collisionMargin = 0.0,
						linearDamping = 0.04, angularDamping = 0.1, animated = false,
						linearFactors:Array<Float> = null, angularFactors:Array<Float> = null,
						group = 1, trigger = false, deactivationParams:Array<Float> = null, ccd = false,
						alternatePhysicUpdate = false, body:BtRigidBodyPointer = null) {
		super();

		if (nullvec) {
			nullvec = false;
			vec1 = BtVector3.create(0, 0, 0);
			vec2 = BtVector3.create(0, 0, 0);
			vec3 = BtVector3.create(0, 0, 0);
			quat1 = BtQuaternion.create(0, 0, 0, 0);
			trans1 = BtTransform.create();
			trans2 = BtTransform.create();
		} 

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
		this.ccd = ccd;
		this.body = body;
		this.alternatePhysicUpdate = alternatePhysicUpdate;

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

		physics = armory.trait.physics.PhysicsWorld.active;
        var bodyCI = null;

		if(body == null)
		{
            transform = object.transform;

            if (shape == Shape.Box) {
                vec1.setX(withMargin(transform.dim.x / 2));
                vec1.setY(withMargin(transform.dim.y / 2));
                vec1.setZ(withMargin(transform.dim.z / 2));
                btshape = BtBoxShape.create(vec1);
            }
            else if (shape == Shape.Sphere) {
                btshape = BtSphereShape.create(withMargin(transform.dim.x / 2));
            }
            else if (shape == Shape.ConvexHull) {
                var shapeConvex = BtConvexHullShape.create();
                fillConvexHull(shapeConvex, transform.scale, collisionMargin);
                btshape = shapeConvex;
            }
            else if (shape == Shape.Cone) {
                btshape = BtConeShapeZ.create(
                    withMargin(transform.dim.x / 2), // Radius
                    withMargin(transform.dim.z));	  // Height
            }
            else if (shape == Shape.Cylinder) {
                vec1.setX(withMargin(transform.dim.x / 2));
                vec1.setY(withMargin(transform.dim.y / 2));
                vec1.setZ(withMargin(transform.dim.z / 2));
                btshape = BtCylinderShapeZ.create(vec1);
            }
            else if (shape == Shape.Capsule) {
                var r = transform.dim.x / 2;
                btshape = BtCapsuleShapeZ.create(
                    withMargin(r), // Radius
                    withMargin(transform.dim.z - r * 2)); // Height between 2 sphere centers
            }
            else if (shape == Shape.Mesh || shape == Shape.Terrain) {
                var meshInterface = BtTriangleMesh.create(true, true);
                fillTriangleMesh(meshInterface, transform.scale);
                if (mass > 0) {
                    var shapeGImpact = BtGImpactMeshShape.create(meshInterface);
                    shapeGImpact.updateBound();
                    btshape = shapeGImpact;
                    if (!physics.gimpactRegistered) {
                        #if js
                        GImpactCollisionAlgorithm.create().registerAlgorithm(physics.dispatcher);
                        #else
                        BtGImpactCollisionAlgorithm.registerAlgorithm(physics.dispatcher);
                        #end
                        physics.gimpactRegistered = true;
                    }
                }
                else {
                    btshape = BtBvhTriangleMeshShape.create(meshInterface, true, true);
                }
            }
            //else if (shape == Shape.Terrain) {
                // var data:Array<Dynamic> = [];
                // btshape = BtHeightfieldTerrainShape.create(3, 3, data, 1, -10, 10, 2, 0, true);
            //}

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

            var centerOfMassOffset = trans2;
            centerOfMassOffset.setIdentity();
            motionState = BtDefaultMotionState.create(trans1, centerOfMassOffset);

            vec1.setX(0);
            vec1.setY(0);
            vec1.setZ(0);
            var inertia = vec1;
            if (mass > 0) btshape.calculateLocalInertia(mass, inertia);
            var bodyCI = BtRigidBodyConstructionInfo.create(mass, motionState, btshape, inertia);
            body = BtRigidBody.create(bodyCI);
            body.setFriction(friction);
            // body.setRollingFriction(friction); // This causes bodies to get stuck, apply angular damping instead
            if (shape == Shape.Sphere || shape == Shape.Cylinder || shape == Shape.Cone || shape == Shape.Capsule) {
                angularDamping += friction;
            }
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

            if (ccd) setCcd(transform.radius);

            bodyScaleX = currentScaleX = transform.scale.x;
            bodyScaleY = currentScaleY = transform.scale.y;
            bodyScaleZ = currentScaleZ = transform.scale.z;
        }
        else
        {
        	motionState = body.getMotionState();
        	btshape = body.getCollisionShape();
        }

		id = nextId;
		nextId++;

		#if js
		//body.setUserIndex(nextId);
		untyped body.userIndex = id;
		#elseif cpp
		body.setUserIndex(id);
		#end

		physics.addRigidBody(this);
		notifyOnRemove(removeFromWorld);

		if (onReady != null) onReady();

		#if js
		if (bodyCI != null) Ammo.destroy(bodyCI);
		#end
	}

	function physicsUpdate() {
		if (!ready) return;
		if (alternatePhysicUpdate) return;
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
		vec1.setX(0);
		vec1.setY(0);
		vec1.setZ(0);
		body.setGravity(vec1);
	}

	public function enableGravity() {
		body.setGravity(physics.world.getGravity());
	}

	public function setGravity(v:Vec4) {
		vec1.setX(v.x);
		vec1.setY(v.y);
		vec1.setZ(v.z);
		body.setGravity(vec1);
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
		vec1.setX(force.x);
		vec1.setY(force.y);
		vec1.setZ(force.z);
		if (loc == null) {
			body.applyCentralForce(vec1);
		}
		else {
			vec2.setX(loc.x);
			vec2.setY(loc.y);
			vec2.setZ(loc.z);
			body.applyForce(vec1, vec2);
		}
	}

	public function applyImpulse(impulse:Vec4, loc:Vec4 = null) {
		activate();
		vec1.setX(impulse.x);
		vec1.setY(impulse.y);
		vec1.setZ(impulse.z);
		if (loc == null) {
			body.applyCentralImpulse(vec1);
		}
		else {
			vec2.setX(loc.x);
			vec2.setY(loc.y);
			vec2.setZ(loc.z);
			body.applyImpulse(vec1, vec2);
		}
	}

	public function applyTorque(torque:Vec4) {
		activate();
		vec1.setX(torque.x);
		vec1.setY(torque.y);
		vec1.setZ(torque.z);
		body.applyTorque(vec1);
	}

	public function applyTorqueImpulse(torque:Vec4) {
		activate();
		vec1.setX(torque.x);
		vec1.setY(torque.y);
		vec1.setZ(torque.z);
		body.applyTorqueImpulse(vec1);
	}

	public function setLinearFactor(x:Float, y:Float, z:Float) {
		vec1.setX(x);
		vec1.setY(y);
		vec1.setZ(z);
		body.setLinearFactor(vec1);
	}

	public function setAngularFactor(x:Float, y:Float, z:Float) {
		vec1.setX(x);
		vec1.setY(y);
		vec1.setZ(z);
		body.setAngularFactor(vec1);
	}

	public function getLinearVelocity():Vec4 {
		var v = body.getLinearVelocity();
		return new Vec4(v.x(), v.y(), v.z());
	}

	public function setLinearVelocity(x:Float, y:Float, z:Float) {
		vec1.setX(x);
		vec1.setY(y);
		vec1.setZ(z);
		body.setLinearVelocity(vec1);
	}

	public function getAngularVelocity():Vec4 {
		var v = body.getAngularVelocity();
		return new Vec4(v.x(), v.y(), v.z());
	}

	public function setAngularVelocity(x:Float, y:Float, z:Float) {
		vec1.setX(x);
		vec1.setY(y);
		vec1.setZ(z);
		body.setAngularVelocity(vec1);
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
		body.setCenterOfMassTransform(trans1);
		if (currentScaleX != t.scale.x || currentScaleY != t.scale.y || currentScaleZ != t.scale.z) setScale(t.scale);
		activate();
	}

	// Continuous collision detection
	public function setCcd(sphereRadius:Float, motionThreshold = 1e-7) {
		body.setCcdSweptSphereRadius(sphereRadius);
		body.setCcdMotionThreshold(motionThreshold);
	}

	function setScale(v:Vec4) {
		currentScaleX = v.x;
		currentScaleY = v.y;
		currentScaleZ = v.z;
		vec1.setX(bodyScaleX * v.x);
		vec1.setY(bodyScaleY * v.y);
		vec1.setZ(bodyScaleZ * v.z);
		btshape.setLocalScaling(vec1);
		physics.world.updateSingleAabb(body);
	}

	function fillConvexHull(shape:BtConvexHullShapePointer, scale:Vec4, margin:Float) {
		var positions = cast(object, MeshObject).data.geom.positions;

		var sx = scale.x * (1.0 - margin);
		var sy = scale.y * (1.0 - margin);
		var sz = scale.z * (1.0 - margin);

		for (i in 0...Std.int(positions.length / 3)) {
			vec1.setX(positions[i * 3] * sx);
			vec1.setY(positions[i * 3 + 1] * sy);
			vec1.setZ(positions[i * 3 + 2] * sz);
			shape.addPoint(vec1, true);
		}
	}

	function fillTriangleMesh(triangleMesh:BtTriangleMeshPointer, scale:Vec4) {
		var positions = cast(object, MeshObject).data.geom.positions;
		var indices = cast(object, MeshObject).data.geom.indices;

		for (ar in indices) {
			for (i in 0...Std.int(ar.length / 3)) {
				vec1.setX(positions[ar[i * 3 + 0] * 3 + 0] * scale.x);
				vec1.setY(positions[ar[i * 3 + 0] * 3 + 1] * scale.y);
				vec1.setZ(positions[ar[i * 3 + 0] * 3 + 2] * scale.z);
				vec2.setX(positions[ar[i * 3 + 1] * 3 + 0] * scale.x);
				vec2.setY(positions[ar[i * 3 + 1] * 3 + 1] * scale.y);
				vec2.setZ(positions[ar[i * 3 + 1] * 3 + 2] * scale.z);
				vec3.setX(positions[ar[i * 3 + 2] * 3 + 0] * scale.x);
				vec3.setY(positions[ar[i * 3 + 2] * 3 + 1] * scale.y);
				vec3.setZ(positions[ar[i * 3 + 2] * 3 + 2] * scale.z);
				triangleMesh.addTriangle(vec1, vec2, vec3);
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
