package armory.trait.physics.bullet;

#if arm_bullet

import iron.Trait;
import iron.system.Time;
import iron.math.Vec4;
import iron.math.Quat;
import iron.math.RayCaster;

class Hit {

	public var rb: RigidBody;
	public var pos: Vec4;
	public var normal: Vec4;
	public function new(rb: RigidBody, pos: Vec4, normal: Vec4){
		this.rb = rb;
		this.pos = pos;
		this.normal = normal;
	}
}

class ConvexHit {
	public var pos: Vec4;
	public var normal: Vec4;
	public var hitFraction: Float;
	public function new(pos: Vec4, normal: Vec4, hitFraction: Float){
		this.pos = pos;
		this.normal = normal;
		this.hitFraction = hitFraction;
	}
}

class ContactPair {

	public var a: Int;
	public var b: Int;
	public var posA: Vec4;
	public var posB: Vec4;
	public var normOnB: Vec4;
	public var impulse: Float;
	public var distance: Float;
	public function new(a: Int, b: Int) {
		this.a = a;
		this.b = b;
	}
}

class PhysicsWorld extends Trait {

	public static var active: PhysicsWorld = null;
	static var sceneRemoved = false;

	#if arm_physics_soft
	public var world: bullet.Bt.SoftRigidDynamicsWorld;
	#else
	public var world: bullet.Bt.DiscreteDynamicsWorld;
	#end

	var dispatcher: bullet.Bt.CollisionDispatcher;
	var gimpactRegistered = false;
	var contacts: Array<ContactPair>;
	var preUpdates: Array<Void->Void> = null;
	public var rbMap: Map<Int, RigidBody>;
	public var conMap: Map<Int, PhysicsConstraint>;
	public var timeScale = 1.0;
	var maxSteps = 1;
	public var solverIterations = 10;
	public var hitPointWorld = new Vec4();
	public var hitNormalWorld = new Vec4();
	public var convexHitPointWorld = new Vec4();
	public var convexHitNormalWorld = new Vec4();
	var pairCache: Bool = false;

	static var nullvec = true;
	static var vec1: bullet.Bt.Vector3 = null;
	static var vec2: bullet.Bt.Vector3 = null;
	static var quat1: bullet.Bt.Quaternion = null;
	static var transform1: bullet.Bt.Transform = null;
	static var transform2: bullet.Bt.Transform = null;

	#if arm_debug
	public static var physTime = 0.0;
	#end

	public function new(timeScale = 1.0, maxSteps = 10, solverIterations = 10) {
		super();

		if (nullvec) {
			nullvec = false;
			vec1 = new bullet.Bt.Vector3(0, 0, 0);
			vec2 = new bullet.Bt.Vector3(0, 0, 0);
			transform1 = new bullet.Bt.Transform();
			transform2 = new bullet.Bt.Transform();
			quat1 = new bullet.Bt.Quaternion(0, 0, 0, 1.0);
		}

		// Scene spawn
		if (active != null && !sceneRemoved) return;
		sceneRemoved = false;

		this.timeScale = timeScale;
		this.maxSteps = maxSteps;
		this.solverIterations = solverIterations;

		// First scene
		if (active == null) {
			createPhysics();
		}
		else { // Scene switch
			world = active.world;
			dispatcher = active.dispatcher;
			gimpactRegistered = active.gimpactRegistered;
		}

		contacts = [];
		rbMap = new Map();
		conMap = new Map();
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
		var broadphase = new bullet.Bt.DbvtBroadphase();

#if arm_physics_soft
		var collisionConfiguration = new bullet.Bt.SoftBodyRigidBodyCollisionConfiguration();
#else
		var collisionConfiguration = new bullet.Bt.DefaultCollisionConfiguration();
#end

		dispatcher = new bullet.Bt.CollisionDispatcher(collisionConfiguration);
		var solver = new bullet.Bt.SequentialImpulseConstraintSolver();

		var g = iron.Scene.active.raw.gravity;
		var gravity = g == null ? new Vec4(0, 0, -9.81) : new Vec4(g[0], g[1], g[2]);

#if arm_physics_soft
		var softSolver = new bullet.Bt.DefaultSoftBodySolver();
		world = new bullet.Bt.SoftRigidDynamicsWorld(dispatcher, broadphase, solver, collisionConfiguration, softSolver);
		vec1.setX(gravity.x);
		vec1.setY(gravity.y);
		vec1.setZ(gravity.z);
		#if js
		world.getWorldInfo().set_m_gravity(vec1);
		#else
		world.getWorldInfo().m_gravity = vec1;
		#end
#else
		world = new bullet.Bt.DiscreteDynamicsWorld(dispatcher, broadphase, solver, collisionConfiguration);
#end

		setGravity(gravity);
	}

	public function setGravity(v: Vec4) {
		vec1.setValue(v.x, v.y, v.z);
		world.setGravity(vec1);
	}

	public function getGravity(): Vec4{
		var g = world.getGravity();
		return (new Vec4(g.x(), g.y(), g.z()));
	}

	public function addRigidBody(body: RigidBody) {
		#if js
		world.addRigidBodyToGroup(body.body, body.group, body.mask);
		#else
		world.addRigidBody(body.body, body.group, body.mask);
		#end
		rbMap.set(body.id, body);
	}

	public function addPhysicsConstraint(constraint: PhysicsConstraint) {
		world.addConstraint(constraint.con, constraint.disableCollisions);
		conMap.set(constraint.id, constraint);
	}

	public function removeRigidBody(body: RigidBody) {
		if (body.destroyed) return;
		body.destroyed = true;
		if (world != null) world.removeRigidBody(body.body);
		rbMap.remove(body.id);
		body.delete();
	}

	public function removePhysicsConstraint(constraint: PhysicsConstraint) {
		if(world != null) world.removeConstraint(constraint.con);
		conMap.remove(constraint.id);
		constraint.delete();
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
	// 	bullet.Bt.Ammo.destroy(controller.body);
	// 	#else
	// 	var cbody = controller.body;
	// 	untyped __cpp__("delete cbody");
	// 	#end
	// }

	/**
	   Used to get intersecting rigid bodies with the passed in RigidBody as reference. Often used when checking for object collisions.
	   @param	body The passed in RigidBody to be checked for intersecting rigid bodies.
	   @return `Array<RigidBody>`
	**/
	public function getContacts(body: RigidBody): Array<RigidBody> {
		if (contacts.length == 0) return null;
		var res: Array<RigidBody> = [];
		for (i in 0...contacts.length) {
			var c = contacts[i];
			var rb = null;

			#if js
			if (c.a == untyped body.body.userIndex) rb = rbMap.get(c.b);
			else if (c.b == untyped body.body.userIndex) rb = rbMap.get(c.a);

			#else
			var ob: bullet.Bt.CollisionObject = body.body;
			if (c.a == ob.getUserIndex()) rb = rbMap.get(c.b);
			else if (c.b == ob.getUserIndex()) rb = rbMap.get(c.a);
			#end

			if (rb != null && res.indexOf(rb) == -1) res.push(rb);
		}
		return res;
	}

	public function getContactPairs(body: RigidBody): Array<ContactPair> {
		if (contacts.length == 0) return null;
		var res: Array<ContactPair> = [];
		for (i in 0...contacts.length) {
			var c = contacts[i];
			#if js

			if (c.a == untyped body.body.userIndex) res.push(c);
			else if (c.b == untyped body.body.userIndex) res.push(c);

			#else

			var ob: bullet.Bt.CollisionObject = body.body;
			if (c.a == ob.getUserIndex()) res.push(c);
			else if (c.b == ob.getUserIndex()) res.push(c);

			#end
		}
		return res;
	}

	public function findBody(id: Int): RigidBody{
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

		//Bullet physics fixed timescale
		var fixedTime = 1.0 / 60;

		//This condition must be satisfied to not loose time
		var currMaxSteps = t < (fixedTime * maxSteps) ? maxSteps : 1;

		world.stepSimulation(t, currMaxSteps, fixedTime);
		updateContacts();

		for (rb in rbMap) @:privateAccess rb.physicsUpdate();

		#if arm_debug
		physTime = kha.Scheduler.realTime() - startTime;
		#end
	}

	function updateContacts() {
		contacts.resize(0);

		var disp: bullet.Bt.Dispatcher = dispatcher;
		var numManifolds = disp.getNumManifolds();

		for (i in 0...numManifolds) {
			var contactManifold = disp.getManifoldByIndexInternal(i);
			#if js
			var body0 = untyped bullet.Bt.Ammo.btRigidBody.prototype.upcast(contactManifold.getBody0());
			var body1 = untyped bullet.Bt.Ammo.btRigidBody.prototype.upcast(contactManifold.getBody1());
			#else
			var body0: bullet.Bt.CollisionObject = contactManifold.getBody0();
			var body1: bullet.Bt.CollisionObject = contactManifold.getBody1();
			#end

			var numContacts = contactManifold.getNumContacts();
			for (j in 0...numContacts) {

				var pt = contactManifold.getContactPoint(j);
				var posA: bullet.Bt.Vector3 = null;
				var posB: bullet.Bt.Vector3 = null;
				var nor: bullet.Bt.Vector3 = null;
				var cp: ContactPair = null;

				#if js
				posA = pt.get_m_positionWorldOnA();
				posB = pt.get_m_positionWorldOnB();
				nor = pt.get_m_normalWorldOnB();
				cp = new ContactPair(untyped body0.userIndex, untyped body1.userIndex);
				#else
				posA = pt.m_positionWorldOnA;
				posB = pt.m_positionWorldOnB;
				nor = pt.m_normalWorldOnB;
				cp = new ContactPair(body0.getUserIndex(), body1.getUserIndex());
				#end

				cp.posA = new Vec4(posA.x(), posA.y(), posA.z());
				cp.posB = new Vec4(posB.x(), posB.y(), posB.z());
				cp.normOnB = new Vec4(nor.x(), nor.y(), nor.z());
				cp.impulse = pt.getAppliedImpulse();
				cp.distance = pt.getDistance();
				contacts.push(cp);

				#if hl
				pt.delete();
				posA.delete();
				posB.delete();
				nor.delete();
				#end
			}
		}
	}

	public function pickClosest(inputX: Float, inputY: Float, group: Int = 0x00000001, mask = 0xFFFFFFFF): RigidBody {
		var camera = iron.Scene.active.camera;
		var start = new Vec4();
		var end = new Vec4();
		RayCaster.getDirection(start, end, inputX, inputY, camera);
		var hit = rayCast(camera.transform.world.getLoc(), end, group, mask);
		var rb = (hit != null) ? hit.rb : null;
		return rb;
	}

	public function rayCast(from: Vec4, to: Vec4, group: Int = 0x00000001, mask = 0xFFFFFFFF): Hit {
		var rayFrom = vec1;
		var rayTo = vec2;
		rayFrom.setValue(from.x, from.y, from.z);
		rayTo.setValue(to.x, to.y, to.z);

		var rayCallback = new bullet.Bt.ClosestRayResultCallback(rayFrom, rayTo);
		#if js
		rayCallback.set_m_collisionFilterGroup(group);
		rayCallback.set_m_collisionFilterMask(mask);
		#elseif (cpp || hl)
		rayCallback.m_collisionFilterGroup = group;
		rayCallback.m_collisionFilterMask = mask;
		#end
		var worldDyn: bullet.Bt.DynamicsWorld = world;
		var worldCol: bullet.Bt.CollisionWorld = worldDyn;
		worldCol.rayTest(rayFrom, rayTo, rayCallback);
		var rb: RigidBody = null;
		var hitInfo: Hit = null;

		var rc: bullet.Bt.RayResultCallback = rayCallback;
		if (rc.hasHit()) {
			#if js
			var co = rayCallback.get_m_collisionObject();
			var body = untyped bullet.Bt.Ammo.btRigidBody.prototype.upcast(co);
			var hit = rayCallback.get_m_hitPointWorld();
			hitPointWorld.set(hit.x(), hit.y(), hit.z());
			var norm = rayCallback.get_m_hitNormalWorld();
			hitNormalWorld.set(norm.x(), norm.y(), norm.z());
			rb = rbMap.get(untyped body.userIndex);
			hitInfo = new Hit(rb, hitPointWorld, hitNormalWorld);
			#elseif (cpp || hl)
			var hit = rayCallback.m_hitPointWorld;
			hitPointWorld.set(hit.x(), hit.y(), hit.z());
			var norm = rayCallback.m_hitNormalWorld;
			hitNormalWorld.set(norm.x(), norm.y(), norm.z());
			rb = rbMap.get(rayCallback.m_collisionObject.getUserIndex());
			hitInfo = new Hit(rb, hitPointWorld, hitNormalWorld);
			#end
		}

		#if js
		bullet.Bt.Ammo.destroy(rayCallback);
		#else
		rayCallback.delete();
		#end

		return hitInfo;
	}

	public function convexSweepTest(rb: RigidBody, from: Vec4, to: Vec4, rotation: Quat, group: Int = 0x00000001, mask = 0xFFFFFFFF): ConvexHit {
		var transformFrom = transform1;
		var transformTo = transform2;
		transformFrom.setIdentity();
		transformTo.setIdentity();

		vec1.setValue(from.x, from.y, from.z);
		transformFrom.setOrigin(vec1);
		quat1.setValue(rotation.x, rotation.y, rotation.z, rotation.w);
		transformFrom.setRotation(quat1);

		vec2.setValue(to.x, to.y, to.z);
		transformTo.setOrigin(vec2);
		quat1.setValue(rotation.x, rotation.y, rotation.z, rotation.w);
		transformFrom.setRotation(quat1);

		var convexCallback = new bullet.Bt.ClosestConvexResultCallback(vec1, vec2);
		#if js
		convexCallback.set_m_collisionFilterGroup(group);
		convexCallback.set_m_collisionFilterMask(mask);
		#elseif (cpp || hl)
		convexCallback.m_collisionFilterGroup = group;
		convexCallback.m_collisionFilterMask = mask;
		#end
		var worldDyn: bullet.Bt.DynamicsWorld = world;
		var worldCol: bullet.Bt.CollisionWorld = worldDyn;
		var bodyColl: bullet.Bt.ConvexShape =  cast rb.body.getCollisionShape();
		worldCol.convexSweepTest(bodyColl, transformFrom, transformTo, convexCallback, 0.0);
		
		var hitInfo: ConvexHit = null;

		var cc: bullet.Bt.ClosestConvexResultCallback = convexCallback;
		if (cc.hasHit()) {
			#if js
			var hit = convexCallback.get_m_hitPointWorld();
			convexHitPointWorld.set(hit.x(), hit.y(), hit.z());
			var norm = convexCallback.get_m_hitNormalWorld();
			convexHitNormalWorld.set(norm.x(), norm.y(), norm.z());
			var hitFraction = convexCallback.get_m_closestHitFraction();
			#elseif (cpp || hl)
			var hit = convexCallback.m_hitPointWorld;
			convexHitPointWorld.set(hit.x(), hit.y(), hit.z());
			var norm = convexCallback.m_hitNormalWorld;
			convexHitNormalWorld.set(norm.x(), norm.y(), norm.z());
			var hitFraction = convexCallback.m_closestHitFraction;
			#end
			hitInfo = new ConvexHit(convexHitPointWorld, convexHitNormalWorld, hitFraction);
		}

		#if js
		bullet.Bt.Ammo.destroy(convexCallback);
		#else
		convexCallback.delete();
		#end

		return hitInfo;
	}

	public function notifyOnPreUpdate(f: Void->Void) {
		if (preUpdates == null) preUpdates = [];
		preUpdates.push(f);
	}

	public function removePreUpdate(f: Void->Void) {
		preUpdates.remove(f);
	}
}

#end
