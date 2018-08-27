package armory.trait.physics.bullet;

#if arm_bullet

import haxebullet.Bullet;
import iron.Trait;
import iron.system.Time;
import iron.math.Vec4;
import iron.math.RayCaster;
import iron.data.SceneFormat;

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

class PhysicsWorld extends Trait {

	public static var active:PhysicsWorld = null;
	static var sceneRemoved = false;

	#if arm_physics_soft
	public var world:BtSoftRigidDynamicsWorldPointer;
	#else
	public var world:BtDiscreteDynamicsWorldPointer;
	#end

	var dispatcher:BtCollisionDispatcherPointer;
	var gimpactRegistered = false;
	var contacts:Array<ContactPair>;
	var preUpdates:Array<Void->Void> = null;
	public var rbMap:Map<Int, RigidBody>;
	public var timeScale = 1.0;
	var timeStep = 1 / 60;
	var maxSteps = 1;
	public var hitPointWorld = new Vec4();
	var pairCache:Bool = false;

	static var nullvec = true;
	static var vec1:BtVector3;
	static var vec2:BtVector3;

	#if arm_debug
	public static var physTime = 0.0;
	#end

	public function new(timeScale = 1.0, timeStep = 1 / 60) {
		super();

		if (nullvec) {
			nullvec = false;
			vec1 = BtVector3.create(0, 0, 0);
			vec2 = BtVector3.create(0, 0, 0);
		}

		// Scene spawn
		if (active != null && !sceneRemoved) return;
		sceneRemoved = false;

		this.timeScale = timeScale;
		this.timeStep = timeStep;
		maxSteps = timeStep < 1 / 60 ? 10 : 1;

		// First scene
		if (active == null) {
			createPhysics();
		}
		// Scene switch
		else {
			world = active.world;
			dispatcher = active.dispatcher;
			gimpactRegistered = active.gimpactRegistered;
		}

		contacts = [];
		rbMap = new Map();
		active = this;

		notifyOnLateUpdate(lateUpdate);
		iron.Scene.active.notifyOnRemove(function() {
			sceneRemoved = true;
		});
	}

	public function reset() {
		for (rb in active.rbMap) removeRigidBody(rb);
	}

	function createPhysics() {
		var broadphase = BtDbvtBroadphase.create();

#if arm_physics_soft
		var collisionConfiguration = BtSoftBodyRigidBodyCollisionConfiguration.create();
#else
		var collisionConfiguration = BtDefaultCollisionConfiguration.create();
#end
		
		dispatcher = BtCollisionDispatcher.create(collisionConfiguration);
		var solver = BtSequentialImpulseConstraintSolver.create();

		var g = iron.Scene.active.raw.gravity;
		var gravity = g == null ? new Vec4(0, 0, -9.81) : new Vec4(g[0], g[1], g[2]);

#if arm_physics_soft
		var softSolver = BtDefaultSoftBodySolver.create();
		world = BtSoftRigidDynamicsWorld.create(dispatcher, broadphase, solver, collisionConfiguration, softSolver);
		vec1.setX(gravity.x);
		vec1.setY(gravity.y);
		vec1.setZ(gravity.z);
		#if js
		world.getWorldInfo().set_m_gravity(vec1);
		#elseif cpp
		world.getWorldInfo().m_gravity = vec1;
		#end
#else
		world = BtDiscreteDynamicsWorld.create(dispatcher, broadphase, solver, collisionConfiguration);
#end

		setGravity(gravity);
	}

	public function setGravity(v:Vec4) {
		vec1.setX(v.x);
		vec1.setY(v.y);
		vec1.setZ(v.z);
		world.setGravity(vec1);
	}

	public function addRigidBody(body:RigidBody) {
		world.addRigidBodyToGroup(body.body, body.group, body.group);
		rbMap.set(body.id, body);
	}

	public function removeRigidBody(body:RigidBody) {
		if (body.destroyed) return;
		body.destroyed = true;
		if (world != null) world.removeRigidBody(body.body);
		rbMap.remove(body.id);
		#if js
		Ammo.destroy(body.motionState);
		Ammo.destroy(body.btshape);
		Ammo.destroy(body.body);
		#elseif cpp
		var cbody = body.body;
		untyped __cpp__("delete cbody");
		#end
	}

	public function addKinematicCharacterController(controller:KinematicCharacterController) {
		if (!pairCache){ // Only create PairCache if needed
			world.getPairCache().setInternalGhostPairCallback(BtGhostPairCallbackPointer.create());
			pairCache = true;
		}
		world.addAction(controller.character);
		world.addCollisionObjectToGroup(controller.body, controller.group, controller.group);
	}

	public function removeKinematicCharacterController(controller:KinematicCharacterController) {
		if (world != null) {
			world.removeCollisionObject(controller.body);
			world.removeAction(controller.character);
		}
		#if js
		Ammo.destroy(controller.body);
		#elseif cpp
		var cbody = controller.body;
		untyped __cpp__("delete cbody");
		#end
	}

	/**
	 * Used to get intersecting rigid bodies with the passed in RigidBody as reference. Often used when checking for object collisions.
	 *
	 * @param	body The passed in RigidBody to be checked for intersecting rigid bodies.
	 * @return Array<RigidBody> or null.
	 */
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

	public function lateUpdate() {
		var t = Time.delta * timeScale;
		if (t == 0.0) return; // Simulation paused

		#if arm_debug
		var startTime = kha.Scheduler.realTime();
		#end

		if (preUpdates != null) for (f in preUpdates) f();

		world.stepSimulation(timeStep, maxSteps, t);
		updateContacts();

		#if arm_debug
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

	public function pickClosest(inputX:Float, inputY:Float):RigidBody {
		var camera = iron.Scene.active.camera;
		var start = new Vec4();
		var end = new Vec4();
		RayCaster.getDirection(start, end, inputX, inputY, camera);
		return rayCast(camera.transform.world.getLoc(), end);
	}

	public function rayCast(from:Vec4, to:Vec4):RigidBody {
		var rayFrom = vec1;
		var rayTo = vec2;
		rayFrom.setX(from.x);
		rayFrom.setY(from.y);
		rayFrom.setZ(from.z);
		rayTo.setX(to.x);
		rayTo.setY(to.y);
		rayTo.setZ(to.z);

		var rayCallback = ClosestRayResultCallback.create(rayFrom, rayTo);
		world.rayTest(rayFrom, rayTo, rayCallback);
		var rb:RigidBody = null;

		if (rayCallback.hasHit()) {
			#if js
			var co = rayCallback.get_m_collisionObject();
			var body = untyped Ammo.btRigidBody.prototype.upcast(co);
			var hit = rayCallback.get_m_hitPointWorld();
			hitPointWorld.set(hit.x(), hit.y(), hit.z());
			rb = rbMap.get(untyped body.userIndex);
			#elseif cpp
			var hit = rayCallback.m_hitPointWorld;
			hitPointWorld.set(hit.x(), hit.y(), hit.z());
			rb = rbMap.get(rayCallback.m_collisionObject.getUserIndex());
			#end
		}

		#if js
		Ammo.destroy(rayCallback);
		#end

		return rb;
	}

	public function notifyOnPreUpdate(f:Void->Void) {
		if (preUpdates == null) preUpdates = [];
		preUpdates.push(f);
	}

	public function removePreUpdate(f:Void->Void) {
		preUpdates.remove(f);
	}
}

#end
