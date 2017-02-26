package armory.trait.internal;

#if arm_physics
import haxebullet.Bullet;
#end
import iron.Trait;
import iron.system.Time;
import iron.math.Vec4;
import iron.math.RayCaster;

class ContactPair {
	public var a:Int;
	public var b:Int;
	public var posA:Vec4;
	public var posB:Vec4;
	public var nor:Vec4;
	public var impulse:Float;
	public function new(a:Int, b:Int) {
		this.a = a;
		this.b = b;
	}
}

@:keep
class PhysicsWorld extends Trait {

#if (!arm_physics)
	public function new() { super(); }
#else
#if arm_profile
	public static var physTime = 0.0;
#end

	public static var active:PhysicsWorld = null;

#if arm_physics_soft
	public var world:BtSoftRigidDynamicsWorldPointer;
#else
	public var world:BtDiscreteDynamicsWorldPointer;
#end

	var dispatcher:BtCollisionDispatcherPointer;
	var contacts:Array<ContactPair> = [];
	var preUpdates:Array<Void->Void> = null;
	public var rbMap:Map<Int, RigidBody>;

	static inline var timeStep = 1 / 60;
	static inline var fixedStep = 1 / 60;

	public function new() {
		super();

		if (active != null) {
			for (rb in active.rbMap) removeRigidBody(rb);
			active.rbMap = new Map();
			return;
		}

		active = this;
		rbMap = new Map();

		//var min = BtVector3.create(-100, -100, -100);
		//var max = BtVector3.create(100, 100, 100);
		//var broadphase = BtAxisSweep3.create(min, max);

		var broadphase = BtDbvtBroadphase.create();

#if arm_physics_soft
		var collisionConfiguration = BtSoftBodyRigidBodyCollisionConfiguration.create();
#else
		var collisionConfiguration = BtDefaultCollisionConfiguration.create();
#end
		
		dispatcher = BtCollisionDispatcher.create(collisionConfiguration);
		var solver = BtSequentialImpulseConstraintSolver.create();

		var gravity = iron.Scene.active.raw.gravity == null ? [0, 0, -9.81] : iron.Scene.active.raw.gravity;

#if arm_physics_soft
		var softSolver = BtDefaultSoftBodySolver.create();
		world = BtSoftRigidDynamicsWorld.create(dispatcher, broadphase, solver, collisionConfiguration, softSolver);
		#if js
		world.getWorldInfo().set_m_gravity(BtVector3.create(gravity[0], gravity[1], gravity[2]));
		#elseif cpp
		world.getWorldInfo().m_gravity = BtVector3.create(gravity[0], gravity[1], gravity[2]);
		#end
#else
		world = BtDiscreteDynamicsWorld.create(dispatcher, broadphase, solver, collisionConfiguration);
#end

		world.setGravity(BtVector3.create(gravity[0], gravity[1], gravity[2]));

		Scene.active.notifyOnInit(function() {
			notifyOnUpdate(update);
		});
	}

	public function addRigidBody(body:RigidBody) {
		world.addRigidBody(body.body);
		rbMap.set(body.id, body);
	}

	public function removeRigidBody(body:RigidBody) {
		if (world != null) world.removeRigidBody(body.body);
		#if js
		Ammo.destroy(body.body);
		#elseif cpp
		// body.body.destroy(); // delete body;
		#end

		rbMap.remove(body.id);
	}

	public function getContacts(body:RigidBody):Array<RigidBody> {
		if (contacts.length == 0) return null;
		var res:Array<RigidBody> = [];
		for (i in 0...contacts.length) {
			var c = contacts[i];
#if js
			if (c.a == untyped body.body.userIndex) res.push(rbMap.get(c.b));
			else if (c.b == untyped body.body.userIndex) res.push(rbMap.get(c.a));
#elseif cpp
			if (c.a == body.body.getUserIndex()) res.push(rbMap.get(c.b));
			else if (c.b == body.body.getUserIndex()) res.push(rbMap.get(c.a));
#end
		}
		return res;
	}

	public function getContactPairs(body:RigidBody):Array<ContactPair> {
		if (contacts.length == 0) return null;
		var res:Array<ContactPair> = [];
		for (i in 0...contacts.length) {
			var c = contacts[i];
#if js
			if (c.a == untyped body.body.userIndex) res.push(c);
			else if (c.b == untyped body.body.userIndex) res.push(c);
#elseif cpp
			if (c.a == body.body.getUserIndex()) res.push(c);
			else if (c.b == body.body.getUserIndex()) res.push(c);
#end
		}
		return res;
	}

	public function update() {
#if arm_profile
		var startTime = kha.Scheduler.realTime();
#end

		if (preUpdates != null) for (f in preUpdates) f();

		world.stepSimulation(timeStep, 1, fixedStep);
		updateContacts();

#if arm_profile
		physTime = kha.Scheduler.realTime() - startTime;
#end
	}

	function updateContacts() {
		contacts = [];

		var numManifolds = dispatcher.getNumManifolds();

		for (i in 0...numManifolds) {
			var contactManifold = dispatcher.getManifoldByIndexInternal(i);
			#if js
			var obA = contactManifold.getBody0();
			var obB = contactManifold.getBody1();
			var bodyA = untyped Ammo.btRigidBody.prototype.upcast(obA);
			var bodyB = untyped Ammo.btRigidBody.prototype.upcast(obB);
			// TODO: remove ContactPair
			var cp = new ContactPair(untyped bodyA.userIndex, untyped bodyB.userIndex);
			#elseif cpp
			var cp = new ContactPair(contactManifold.getBody0().getUserIndex(), contactManifold.getBody1().getUserIndex());
			#end

			var numContacts = contactManifold.getNumContacts();
			for (j in 0...numContacts) {
				var pt:BtManifoldPoint = contactManifold.getContactPoint(j);
				if (pt.getDistance() < 0) {
					#if js
					var posA = pt.get_m_positionWorldOnA();
					var posB = pt.get_m_positionWorldOnB();
					var nor = pt.get_m_normalWorldOnB();
					#elseif cpp
					var posA = pt.m_positionWorldOnA;
					var posB = pt.m_positionWorldOnB;
					var nor = pt.m_normalWorldOnB;
					#end
					cp.posA = new Vec4(posA.x(), posA.y(), posA.z());
					cp.posB = new Vec4(posB.x(), posB.y(), posB.z());
					cp.nor = new Vec4(nor.x(), nor.y(), nor.z());
					cp.impulse = pt.getAppliedImpulse();
					contacts.push(cp);
					break; // TODO: only one contact point for now
				}
			}
		}
	}

	public var hitPointWorld:BtVector3;
	public function pickClosest(inputX:Float, inputY:Float):RigidBody {

		var rayFrom = getRayFrom();
		var rayTo = getRayTo(inputX, inputY);

		var rayCallback = ClosestRayResultCallback.create(rayFrom, rayTo);
		world.rayTest(rayFrom, rayTo, rayCallback);
		
		if (rayCallback.hasHit()) {
			#if js
			var co = rayCallback.get_m_collisionObject();
			var body = untyped Ammo.btRigidBody.prototype.upcast(co);
			hitPointWorld = rayCallback.get_m_hitPointWorld();
			return rbMap.get(untyped body.userIndex);
			#elseif cpp
			hitPointWorld = rayCallback.m_hitPointWorld;
			return rbMap.get(rayCallback.m_collisionObject.getUserIndex());
			#end
		}
		else {
			return null;
		}
	}

	public function getRayFrom():BtVector3 {
		var camera = iron.Scene.active.camera;
		return BtVector3.create(camera.transform.absx(), camera.transform.absy(), camera.transform.absz());
	}

	public function getRayTo(inputX:Float, inputY:Float):BtVector3 {
		var camera = iron.Scene.active.camera;
		var start = new Vec4();
		var end = new Vec4();
		RayCaster.getDirection(start, end, inputX, inputY, camera);
		return BtVector3.create(end.x, end.y, end.z);
	}

	public function notifyOnPreUpdate(f:Void->Void) {
		if (preUpdates == null) preUpdates = [];
		preUpdates.push(f);
	}

	public function removePreUpdate(f:Void->Void) {
		preUpdates.remove(f);
	}
#end
}
