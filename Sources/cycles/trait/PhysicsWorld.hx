package cycles.trait;

import haxebullet.Bullet;
import lue.trait.Trait;
import lue.sys.Time;
import lue.math.Vec3;
import lue.math.RayCaster;

class ContactPair {
	public var a:Int;
	public var b:Int;
	public function new(a:Int, b:Int) {
		this.a = a;
		this.b = b;
	}
}

class PhysicsWorld extends Trait {

	#if js
	public var world:BtDiscreteDynamicsWorld;
	var dispatcher:BtCollisionDispatcher;
	#elseif cpp
	public var world:cpp.Pointer<BtDiscreteDynamicsWorld>;
	var dispatcher:cpp.Pointer<BtCollisionDispatcher>;
	#end

	var contacts:Array<ContactPair> = [];
	var rbMap:Map<Int, RigidBody>;

	public function new() {
		super();

		rbMap = new Map();

		#if js

		//var min = new BtVector3(-100, -100, -100);
		//var max = new BtVector3(100, 100, 100);
		//var broadphase = new BtAxisSweep3(min, max);

		var broadphase = new BtDbvtBroadphase();

		var collisionConfiguration = new BtDefaultCollisionConfiguration();
		dispatcher = new BtCollisionDispatcher(collisionConfiguration);
		
		var solver = new BtSequentialImpulseConstraintSolver();

		world = new BtDiscreteDynamicsWorld(dispatcher, broadphase, solver, collisionConfiguration);
		var g = new BtVector3(0, 0, -9.81);
		world.setGravity(g);

		#elseif cpp

		//var min = BtVector3.create(-100, -100, -100);
		//var max = BtVector3.create(100, 100, 100);
		//var broadphase = BtAxisSweep3.create(min.value, max.value);

		var broadphase = BtDbvtBroadphase.create();

		var collisionConfiguration = BtDefaultCollisionConfiguration.create();
		dispatcher = BtCollisionDispatcher.create(collisionConfiguration);
		
		var solver = BtSequentialImpulseConstraintSolver.create();

		world = BtDiscreteDynamicsWorld.create(dispatcher, broadphase, solver, collisionConfiguration);
		var g = BtVector3.create(0, 0, -9.81);
		world.value.setGravity(g.value);
		
		#end

		requestUpdate(update);
	}

	public function addRigidBody(body:RigidBody) {
		#if js
		world.addRigidBody(body.body);
		#elseif cpp
		world.value.addRigidBody(body.body);
		#end

		rbMap.set(body.id, body);
	}

	public function removeRigidBody(body:RigidBody) {
		#if js
		world.removeRigidBody(body.body);
		Ammo.destroy(body.body);
		#elseif cpp
		world.value.removeRigidBody(body.body);
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
			if (c.a == body.body.value.getUserIndex()) {
				res.push(rbMap.get(c.b));
			}
			else if (c.b == body.body.value.getUserIndex()) {
				res.push(rbMap.get(c.a));
			}
			#end
		}
		return res;
	}

	public function update() {
		#if js
		world.stepSimulation(1 / 60);
		#elseif cpp
		world.value.stepSimulation(1 / 60);
		#end

		updateContacts();
	}

	function updateContacts() {
		contacts = [];

		#if cpp
		var numManifolds = dispatcher.value.getNumManifolds();
		#else
		var numManifolds = dispatcher.getNumManifolds();
		#end

		for (i in 0...numManifolds) {
			#if js
			var contactManifold = dispatcher.getManifoldByIndexInternal(i);
			var obA = contactManifold.getBody0();
			var obB = contactManifold.getBody1();
			var bodyA = untyped Ammo.btRigidBody.prototype.upcast(obA);
			var bodyB = untyped Ammo.btRigidBody.prototype.upcast(obB);
			// TODO: remove ContactPair
			var cp = new ContactPair(untyped bodyA.userIndex, untyped bodyB.userIndex);
			#elseif cpp
			var contactManifold = dispatcher.value.getManifoldByIndexInternal(i);
			var obA = contactManifold.value.getBody0();
			var obB = contactManifold.value.getBody1();
			var cp = new ContactPair(obA.value.getUserIndex(), obB.value.getUserIndex());
			#end

			#if js
			var numContacts = contactManifold.getNumContacts();
			#elseif cpp
			var numContacts = contactManifold.value.getNumContacts();
			#end
			for (j in 0...numContacts) {
				#if js
				var pt = contactManifold.getContactPoint(j);
				#elseif cpp
				var pt = contactManifold.value.getContactPoint(j);
				#end

				if (pt.getDistance() < 0) {
					//var ptA = pt.getPositionWorldOnA();
					//var ptB = pt.getPositionWorldOnB();
					contacts.push(cp);
					break; // TODO: only one contact point for now
				}
			}
	    }
	}

	#if js
	public var rayCallback:ClosestRayResultCallback;
	#elseif cpp
	public var rayCallback:cpp.Pointer<ClosestRayResultCallback>;
	#end
	public function pickClosest(inputX:Float, inputY:Float):RigidBody {

        var rayFrom = getRayFrom();
        var rayTo = getRayTo(inputX, inputY);

        #if js
        rayCallback = new ClosestRayResultCallback(rayFrom, rayTo);
        #elseif cpp
        rayCallback = ClosestRayResultCallback.create(rayFrom.value, rayTo.value);
        #end
 
 		#if js
        world.rayTest(rayFrom, rayTo, rayCallback);
        #elseif cpp
        world.value.rayTest(rayFrom.value, rayTo.value, rayCallback.value);
        #end
        
        #if js
        if (rayCallback.hasHit()) {
        	var co = rayCallback.get_m_collisionObject();
			var body = untyped Ammo.btRigidBody.prototype.upcast(co);
            return rbMap.get(untyped body.userIndex);
        }
        else { return null; }
        #elseif cpp
        if (rayCallback.value.hasHit()) {
        	var co = rayCallback.value.m_collisionObject;
            return rbMap.get(co.value.getUserIndex());
        }
        else { return null; }
        #end
    }

    #if cpp
    public function getRayFrom():cpp.Pointer<BtVector3> {
    #else
    public function getRayFrom():BtVector3 {
    #end
    	var camera = lue.node.Node.cameras[0];
    	#if js
    	return new BtVector3(camera.transform.pos.x, camera.transform.pos.y, camera.transform.pos.z);
    	#elseif cpp
    	return BtVector3.create(camera.transform.pos.x, camera.transform.pos.y, camera.transform.pos.z);
    	#end
    }

    #if cpp
    public function getRayTo(inputX:Float, inputY:Float):cpp.Pointer<BtVector3> {
    #else
    public function getRayTo(inputX:Float, inputY:Float):BtVector3 {
    #end
    	var camera = lue.node.Node.cameras[0];
    	var start = new Vec3();
        var end = new Vec3();
    	RayCaster.getDirection(start, end, inputX, inputY, camera);

    	#if js
    	return new BtVector3(end.x, end.y, end.z);
    	#elseif cpp
    	return BtVector3.create(end.x, end.y, end.z);
    	#end
    }
}
