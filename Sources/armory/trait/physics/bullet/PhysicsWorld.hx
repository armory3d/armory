package armory.trait.physics.bullet;

#if arm_bullet

import iron.Trait;
import iron.system.Time;
import iron.math.Vec4;
import iron.math.RayCaster;
import iron.data.SceneFormat;

class Hit {
	public var rb:RigidBody;
	public var pos:Vec4;
	public var normal:Vec4;
	public function new(rb:RigidBody, pos:Vec4, normal:Vec4){
		this.rb = rb;
		this.pos = pos;
		this.normal = normal;
	}
}

class ContactPair {
	public var a:Int;
	public var b:Int;
	public var posA:Vec4;
	public var posB:Vec4;
	public var normOnB:Vec4;
	public var impulse:Float;
	public var distance:Float;
	public function new(a:Int, b:Int) {
		this.a = a;
		this.b = b;
	}
}

class PhysicsWorld extends Trait {

	public static var active:PhysicsWorld = null;
	static var sceneRemoved = false;

	#if arm_physics_soft
	public var world:bullet.SoftRigidDynamicsWorld;
	#else
	public var world:bullet.DiscreteDynamicsWorld;
	#end

	var dispatcher:bullet.CollisionDispatcher;
	var gimpactRegistered = false;
	var contacts:Array<ContactPair>;
	var preUpdates:Array<Void->Void> = null;
	public var rbMap:Map<Int, RigidBody>;
	public var timeScale = 1.0;
	var timeStep = 1 / 60;
	var maxSteps = 1;
	public var solverIterations = 10;
	public var hitPointWorld = new Vec4();
	public var hitNormalWorld = new Vec4();
	var pairCache:Bool = false;

	static var nullvec = true;
	static var vec1:bullet.Vector3 = null;
	static var vec2:bullet.Vector3 = null;
	static var vec3:bullet.Vector3 = null;

	#if arm_debug
	public static var physTime = 0.0;
	#end

	public function new(timeScale = 1.0, timeStep = 1 / 60, solverIterations = 10) {
		super();

		if (nullvec) {
			nullvec = false;
			vec1 = new bullet.Vector3(0, 0, 0);
			vec2 = new bullet.Vector3(0, 0, 0);
			vec3 = new bullet.Vector3(0, 0, 0);
		}

		// Scene spawn
		if (active != null && !sceneRemoved) return;
		sceneRemoved = false;

		this.timeScale = timeScale;
		this.timeStep = timeStep;
		maxSteps = timeStep < 1 / 60 ? 10 : 1;
		this.solverIterations = solverIterations;

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

		// Ensure physics are updated first in the lateUpdate list
		_lateUpdate = [lateUpdate];
		@:privateAccess iron.App.traitLateUpdates.insert(0, lateUpdate);
		
		iron.Scene.active.notifyOnRemove(function() {
			sceneRemoved = true;
		});
	}

	public function reset() {
		for (rb in active.rbMap) removeRigidBody(rb);
	}

	function createPhysics() {
		var broadphase = new bullet.DbvtBroadphase();

#if arm_physics_soft
		var collisionConfiguration = new bullet.SoftBodyRigidBodyCollisionConfiguration();
#else
		var collisionConfiguration = new bullet.DefaultCollisionConfiguration();
#end
		
		dispatcher = new bullet.CollisionDispatcher(collisionConfiguration);
		var solver = new bullet.SequentialImpulseConstraintSolver();

		var g = iron.Scene.active.raw.gravity;
		var gravity = g == null ? new Vec4(0, 0, -9.81) : new Vec4(g[0], g[1], g[2]);

#if arm_physics_soft
		var softSolver = new bullet.DefaultSoftBodySolver();
		world = new bullet.SoftRigidDynamicsWorld(dispatcher, broadphase, solver, collisionConfiguration, softSolver);
		vec1.setX(gravity.x);
		vec1.setY(gravity.y);
		vec1.setZ(gravity.z);
		world.getWorldInfo().m_gravity = vec1;
#else
		world = new bullet.DiscreteDynamicsWorld(dispatcher, broadphase, solver, collisionConfiguration);
#end

		setGravity(gravity);
	}

	public function setGravity(v:Vec4) {
		vec1.setValue(v.x, v.y, v.z);
		world.setGravity(vec1);
	}

	public function addRigidBody(body:RigidBody) {
		world.addRigidBody(body.body, body.group, body.group);
		rbMap.set(body.id, body);
	}

	public function removeRigidBody(body:RigidBody) {
		if (body.destroyed) return;
		body.destroyed = true;
		if (world != null) world.removeRigidBody(body.body);
		rbMap.remove(body.id);
		body.delete();
	}

	// public function addKinematicCharacterController(controller:KinematicCharacterController) {
	// 	if (!pairCache){ // Only create PairCache if needed
	// 		world.getPairCache().setInternalGhostPairCallback(BtGhostPairCallbackPointer.create());
	// 		pairCache = true;
	// 	}
	// 	world.addAction(controller.character);
	// 	world.addCollisionObjectToGroup(controller.body, controller.group, controller.group);
	// }

	// public function removeKinematicCharacterController(controller:KinematicCharacterController) {
	// 	if (world != null) {
	// 		world.removeCollisionObject(controller.body);
	// 		world.removeAction(controller.character);
	// 	}
	// 	#if js
	// 	bullet.Ammo.destroy(controller.body);
	// 	#else
	// 	var cbody = controller.body;
	// 	untyped __cpp__("delete cbody");
	// 	#end
	// }

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
			var rb = null;

			var ob:bullet.CollisionObject = body.body;
			if (c.a == ob.getUserIndex()) rb = rbMap.get(c.b);
			else if (c.b == ob.getUserIndex()) rb = rbMap.get(c.a);

			if (rb != null && res.indexOf(rb) == -1) res.push(rb);
		}
		return res;
	}

	public function getContactPairs(body:RigidBody):Array<ContactPair> {
		if (contacts.length == 0) return null;
		var res:Array<ContactPair> = [];
		for (i in 0...contacts.length) {
			var c = contacts[i];
			var ob:bullet.CollisionObject = body.body;

			if (c.a == ob.getUserIndex()) res.push(c);
			else if (c.b == ob.getUserIndex()) res.push(c);
		}
		return res;
	}
	
	public function findBody(id:Int):RigidBody{
		var rb = rbMap.get(id);
		return rb;
	}

	function lateUpdate() {
		var t = Time.delta * timeScale;
		if (t == 0.0) return; // Simulation paused

		#if arm_debug
		var startTime = kha.Scheduler.realTime();
		#end

		if (preUpdates != null) for (f in preUpdates) f();

		world.stepSimulation(timeStep, maxSteps, t);
		updateContacts();

		for (rb in rbMap) @:privateAccess rb.physicsUpdate();

		#if arm_debug
		physTime = kha.Scheduler.realTime() - startTime;
		#end
	}

	function updateContacts() {
		var cp:ContactPair = null;
		var pt:bullet.ManifoldPoint = null;
		var contactManifold:bullet.PersistentManifold = null;
		contacts = [];

		for (i in 0...dispatcher.getNumManifolds()) {
			contactManifold = dispatcher.getManifoldByIndexInternal(i);

			for (j in 0...contactManifold.getNumContacts()) {
				pt = contactManifold.getContactPoint(j);
				vec1 = pt.m_positionWorldOnA;
				vec2 = pt.m_positionWorldOnB;
				vec3 = pt.m_normalWorldOnB;
				cp = new ContactPair(
					contactManifold.getBody0().getUserIndex(),
					contactManifold.getBody1().getUserIndex()
				);
				cp.posA = new Vec4(vec1.x(), vec1.y(), vec1.z());
				cp.posB = new Vec4(vec2.x(), vec2.y(), vec2.z());
				cp.normOnB = new Vec4(vec3.x(), vec3.y(), vec3.z());
				cp.impulse = pt.getAppliedImpulse();
				cp.distance = pt.getDistance();
				contacts.push(cp);
				vec1.delete();
				vec2.delete();
				vec3.delete();
				pt.delete();
			}
		}
	}

	public function pickClosest(inputX:Float, inputY:Float):RigidBody {
		var camera = iron.Scene.active.camera;
		var start = new Vec4();
		var end = new Vec4();
		RayCaster.getDirection(start, end, inputX, inputY, camera);
		var hit = rayCast(camera.transform.world.getLoc(), end);
		var rb = (hit != null) ? hit.rb : null;
		return rb;
	}

	public function rayCast(from:Vec4, to:Vec4):Hit {
		var rayFrom = vec1;
		var rayTo = vec2;
		rayFrom.setValue(from.x, from.y, from.z);
		rayTo.setValue(to.x, to.y, to.z);

		var rayCallback = new bullet.ClosestRayResultCallback(rayFrom, rayTo);
		var worldDyn:bullet.DynamicsWorld = world;
		var worldCol:bullet.CollisionWorld = worldDyn;
		worldCol.rayTest(rayFrom, rayTo, rayCallback);
		var rb:RigidBody = null;
		var hitInfo:Hit = null;

		var rc:bullet.RayResultCallback = rayCallback;
		if (rc.hasHit()) {
			var hit = rayCallback.m_hitPointWorld;
			hitPointWorld.set(hit.x(), hit.y(), hit.z());
			var norm = rayCallback.m_hitNormalWorld;
			hitNormalWorld.set(norm.x(), norm.y(), norm.z());
			rb = rbMap.get(rayCallback.m_collisionObject.getUserIndex());
		}

		rayCallback.delete();

		return hitInfo;
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
