package armory.trait.internal;

#if WITH_PHYSICS
import haxebullet.Bullet;
#end
import iron.Trait;
import iron.sys.Time;
import iron.math.Vec4;
import iron.math.RayCaster;

class ContactPair {
	public var a:Int;
	public var b:Int;
	public function new(a:Int, b:Int) {
		this.a = a;
		this.b = b;
	}
}

class PhysicsWorld extends Trait {

#if (!WITH_PHYSICS)
	public function new() { super(); }
#else

	public var world:BtDiscreteDynamicsWorldPointer;
	var dispatcher:BtCollisionDispatcherPointer;

	var contacts:Array<ContactPair> = [];
	var rbMap:Map<Int, RigidBody>;

	static inline var timeStep = 1 / 60;
	static inline var fixedStep = 1 / 60;

	public function new() {
		super();

		rbMap = new Map();

		//var min = BtVector3.create(-100, -100, -100);
		//var max = BtVector3.create(100, 100, 100);
		//var broadphase = BtAxisSweep3.create(min.value, max.value);

		var broadphase = BtDbvtBroadphase.create();

		var collisionConfiguration = BtDefaultCollisionConfiguration.create();
		dispatcher = BtCollisionDispatcher.create(collisionConfiguration);
		
		var solver = BtSequentialImpulseConstraintSolver.create();

		world = BtDiscreteDynamicsWorld.create(dispatcher, broadphase, solver, collisionConfiguration);
		world.ptr.setGravity(BtVector3.create(0, 0, -9.81).value);

		notifyOnUpdate(update);
	}

	public function addRigidBody(body:RigidBody) {
		world.ptr.addRigidBody(body.body);
		rbMap.set(body.id, body);
	}

	public function removeRigidBody(body:RigidBody) {
		world.ptr.removeRigidBody(body.body);
		#if js
		Ammo.destroy(body.body);
		#elseif cpp
		body.body.destroy();
		#end

		rbMap.remove(body.id);
	}

	public function getContacts(body:RigidBody):Array<RigidBody> {
		if (contacts.length == 0) return null;
		
		var res:Array<RigidBody> = [];
		for (i in 0...contacts.length) {

			var c = contacts[i];

			#if js
			if (c.a == untyped body.body.userIndex) {
				res.push(rbMap.get(c.b));
			}
			else if (c.b == untyped body.body.userIndex) {
				res.push(rbMap.get(c.a));
			}
			#elseif cpp
			if (c.a == body.body.ptr.getUserIndex()) {
				res.push(rbMap.get(c.b));
			}
			else if (c.b == body.body.ptr.getUserIndex()) {
				res.push(rbMap.get(c.a));
			}
			#end
		}
		return res;
	}

	public function update() {
		world.ptr.stepSimulation(timeStep, 1, fixedStep);
		updateContacts();
	}

	function updateContacts() {
		contacts = [];

		var numManifolds = dispatcher.value.getNumManifolds();

		for (i in 0...numManifolds) {
			var contactManifold = dispatcher.value.getManifoldByIndexInternal(i);
			var obA = contactManifold.value.getBody0();
			var obB = contactManifold.value.getBody1();
			#if js
			var bodyA = untyped Ammo.btRigidBody.prototype.upcast(obA);
			var bodyB = untyped Ammo.btRigidBody.prototype.upcast(obB);
			// TODO: remove ContactPair
			var cp = new ContactPair(untyped bodyA.userIndex, untyped bodyB.userIndex);
			#elseif cpp
			var cp = new ContactPair(obA.value.getUserIndex(), obB.value.getUserIndex());
			#end

			var numContacts = contactManifold.value.getNumContacts();
			for (j in 0...numContacts) {
				var pt = contactManifold.value.getContactPoint(j);

				if (pt.getDistance() < 0) {
					//var ptA = pt.getPositionWorldOnA();
					//var ptB = pt.getPositionWorldOnB();
					contacts.push(cp);
					break; // TODO: only one contact point for now
				}
			}
	    }
	}

	public var rayCallback:ClosestRayResultCallbackPointer;
	public function pickClosest(inputX:Float, inputY:Float):RigidBody {

        var rayFrom = getRayFrom();
        var rayTo = getRayTo(inputX, inputY);

        rayCallback = ClosestRayResultCallback.create(rayFrom.value, rayTo.value);
        world.ptr.rayTest(rayFrom.value, rayTo.value, rayCallback.value);
        
        if (rayCallback.value.hasHit()) {
        	#if js
        	var co = rayCallback.value.get_m_collisionObject();
			var body = untyped Ammo.btRigidBody.prototype.upcast(co);
        	return rbMap.get(untyped body.userIndex);
        	#elseif cpp
        	var co = rayCallback.value.m_collisionObject;
            return rbMap.get(co.value.getUserIndex());
            #end
        }
        else {
        	return null;
        }
    }

    public function getRayFrom():BtVector3Pointer {
    	var camera = iron.node.RootNode.cameras[0];
    	return BtVector3.create(camera.transform.pos.x, camera.transform.pos.y, camera.transform.pos.z);
    }

    public function getRayTo(inputX:Float, inputY:Float):BtVector3Pointer {
    	var camera = iron.node.RootNode.cameras[0];
    	var start = new Vec4();
        var end = new Vec4();
    	RayCaster.getDirection(start, end, inputX, inputY, camera);
    	return BtVector3.create(end.x, end.y, end.z);
    }
#end
}
