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

	var debugDrawHelper: DebugDrawHelper = null;

	#if arm_debug
	public static var physTime = 0.0;
	#end

	public function new(timeScale = 1.0, maxSteps = 10, solverIterations = 10, debugDrawMode: DebugDrawMode = NoDebug) {
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

		setDebugDrawMode(debugDrawMode);

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
		#if !(kha_html5 || kha_debug_html5)
		var fixedTime = kha.Display.primary != null ? 1 / kha.Display.primary.frequency : 1 / 60;
		#else
		var fixedTime = 1.0 / 60;
		#end

		//This condition must be satisfied to not loose time
		var currMaxSteps = t < (fixedTime * maxSteps) ? maxSteps : 1;

		world.stepSimulation(t, currMaxSteps, fixedTime);
		updateContacts();

		for (rb in rbMap) { @:privateAccess try { rb.physicsUpdate(); } catch(e:haxe.Exception) { trace(e.message); } } // HACK: see this recommendation: https://github.com/armory3d/armory/issues/3044#issuecomment-2558199944.

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

		if (getDebugDrawMode() & DrawRayCast != 0) {
			debugDrawHelper.rayCast({
				from: from,
				to: to,
				hasHit: rc.hasHit(),
				hitPoint: hitPointWorld,
				hitNormal: hitNormalWorld
			});
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

	public function setDebugDrawMode(debugDrawMode: DebugDrawMode) {
		if (debugDrawHelper == null) {
			if (debugDrawMode == NoDebug) {
				return;
			}
			initDebugDrawing(debugDrawMode);
		}

		#if js
			world.getDebugDrawer().setDebugMode(debugDrawMode);
		#elseif hl
			hlDebugDrawer_setDebugMode(debugDrawMode);
		#end
	}

	public inline function getDebugDrawMode(): DebugDrawMode {
		if (debugDrawHelper == null) {
			return NoDebug;
		}

		#if js
			return world.getDebugDrawer().getDebugMode();
		#elseif hl
			return hlDebugDrawer_getDebugMode();
		#else
			return NoDebug;
		#end
	}

	function initDebugDrawing(debugDrawMode: DebugDrawMode) {
		debugDrawHelper = new DebugDrawHelper(this, debugDrawMode);

		#if js
			final drawer = new bullet.Bt.DebugDrawer();

			// https://emscripten.org/docs/porting/connecting_cpp_and_javascript/WebIDL-Binder.html?highlight=jsimplementation#sub-classing-c-base-classes-in-javascript-jsimplementation
			drawer.drawLine = debugDrawHelper.drawLine;
			drawer.drawContactPoint = debugDrawHelper.drawContactPoint;
			drawer.reportErrorWarning = debugDrawHelper.reportErrorWarning;
			drawer.draw3dText = debugDrawHelper.draw3dText;

			// From the Armory API perspective this is not required,
			// but Ammo requires it and will result in a black screen if not set
			drawer.setDebugMode = debugDrawHelper.setDebugMode;
			drawer.getDebugMode = debugDrawHelper.getDebugMode;

			world.setDebugDrawer(drawer);
		#elseif hl
			hlDebugDrawer_setDrawLine(debugDrawHelper.drawLine);
			hlDebugDrawer_setDrawContactPoint(debugDrawHelper.drawContactPoint);
			hlDebugDrawer_setReportErrorWarning(debugDrawHelper.reportErrorWarning);
			hlDebugDrawer_setDraw3dText(debugDrawHelper.draw3dText);

			hlDebugDrawer_worldSetGlobalDebugDrawer(world);
		#end
	}

	#if hl
	@:hlNative("bullet", "debugDrawer_worldSetGlobalDebugDrawer")
	public static function hlDebugDrawer_worldSetGlobalDebugDrawer(world: #if arm_physics_soft bullet.Bt.SoftRigidDynamicsWorld #else bullet.Bt.DiscreteDynamicsWorld #end) {}

	@:hlNative("bullet", "debugDrawer_setDebugMode")
	public static function hlDebugDrawer_setDebugMode(debugMode: Int) {}

	@:hlNative("bullet", "debugDrawer_getDebugMode")
	public static function hlDebugDrawer_getDebugMode(): Int { return 0; }

	@:hlNative("bullet", "debugDrawer_setDrawLine")
	public static function hlDebugDrawer_setDrawLine(func: bullet.Bt.Vector3->bullet.Bt.Vector3->bullet.Bt.Vector3->Void) {}

	@:hlNative("bullet", "debugDrawer_setDrawContactPoint")
	public static function hlDebugDrawer_setDrawContactPoint(func: bullet.Bt.Vector3->bullet.Bt.Vector3->kha.FastFloat->Int->bullet.Bt.Vector3->Void) {}

	@:hlNative("bullet", "debugDrawer_setReportErrorWarning")
	public static function hlDebugDrawer_setReportErrorWarning(func: hl.Bytes->Void) {}

	@:hlNative("bullet", "debugDrawer_setDraw3dText")
	public static function hlDebugDrawer_setDraw3dText(func: bullet.Bt.Vector3->hl.Bytes->Void) {}
	#end
}

/**
	Debug flags for Bullet physics, despite the name not solely related to debug drawing.
	You can combine multiple flags with bitwise operations.

	Taken from Bullet's `btIDebugDraw::DebugDrawModes` enum.
	Please note that the descriptions of the individual flags are a result of inspecting the Bullet sources and thus might contain inaccuracies.

	@see `armory.trait.physics.PhysicsWorld.getDebugDrawMode()`
	@see `armory.trait.physics.PhysicsWorld.setDebugDrawMode()`
**/
// Not all of the flags below are actually used in the library core, some of them are only used
// in individual Bullet example projects. The intention of the original authors is unknown,
// so whether those flags are actually meant to get their purpose from the implementing application
// and not from the library remains a mystery...
enum abstract DebugDrawMode(Int) from Int to Int {
	/** All debug flags off. **/
	var NoDebug = 0;

	/** Draw wireframes of the physics collider meshes and suspensions of raycast vehicle simulations. **/
	var DrawWireframe = 1;

	/** Draw axis-aligned minimum bounding boxes (AABBs) of the physics collider meshes. **/
	var DrawAABB = 1 << 1;

	/** Not used in Armory. **/
	// Only used in a Bullet physics example at the moment:
	// https://github.com/bulletphysics/bullet3/blob/39b8de74df93721add193e5b3d9ebee579faebf8/examples/ExampleBrowser/GL_ShapeDrawer.cpp#L616-L644
	var DrawFeaturesText = 1 << 2;

	/** Visualize contact points of multiple colliders. **/
	var DrawContactPoints = 1 << 3;

	/**
		Globally disable sleeping/deactivation of dynamic colliders.
	**/
	var NoDeactivation = 1 << 4;

	/** Not used in Armory. **/
	// Not used in the library core, in some Bullet examples this flag is used to print application-specific help text (e.g. keyboard shortcuts) to the screen, e.g.:
	// https://github.com/bulletphysics/bullet3/blob/39b8de74df93721add193e5b3d9ebee579faebf8/examples/ForkLift/ForkLiftDemo.cpp#L586
	var NoHelpText = 1 << 5;

	/** Not used in Armory. **/
	// Not used in the library core, appears to be the opposite of NoHelpText (not sure why there are two flags required for this...)
	// https://github.com/bulletphysics/bullet3/blob/39b8de74df93721add193e5b3d9ebee579faebf8/examples/FractureDemo/FractureDemo.cpp#L189
	var DrawText = 1 << 6;

	/** Not used in Armory. **/
	// Not even used in official Bullet examples, probably obsolete.
	// Related to btQuickprof.h: https://pybullet.org/Bullet/phpBB3/viewtopic.php?t=1285#p4743
	// Probably replaced by define: https://github.com/bulletphysics/bullet3/commit/d051e2eacb01a948c7b53e24fd3d9942ce64bdcc
	var ProfileTimings = 1 << 7;

	/** Not used in Armory. **/
	// Not even used in official Bullet examples, might be obsolete.
	var EnableSatComparison = 1 << 8;

	/** Not used in Armory. **/
	var DisableBulletLCP = 1 << 9;

	/** Not used in Armory. **/
	var EnableCCD = 1 << 10;

	/** Draw axis gizmos for important constraint points. **/
	var DrawConstraints = 1 << 11;

	/** Draw additional constraint information such as distance or angle limits. **/
	var DrawConstraintLimits = 1 << 12;

	/** Not used in Armory. **/
	// Only used in a Bullet physics example at the moment:
	// https://github.com/bulletphysics/bullet3/blob/39b8de74df93721add193e5b3d9ebee579faebf8/examples/ExampleBrowser/GL_ShapeDrawer.cpp#L258
	// We could use it in the future to toggle depth testing for lines, i.e. draw actual 3D lines if not set and Kha's g2 lines if set.
	var FastWireframe = 1 << 13;

	/**
		Draw the normal vectors of the triangles of the physics collider meshes.
		This only works for `Mesh` collision shapes.
	**/
	// Outside of Armory this works for a few more collision shapes
	var DrawNormals = 1 << 14;

	 /**
		Draw a small axis gizmo at the origin of the collision shape.
		Only works if `DrawWireframe` is enabled as well.
	 **/
	var DrawFrames = 1 << 15;

	var DrawRayCast = 1 << 16;

	@:op(~A) public inline function bitwiseNegate(): DebugDrawMode {
		return ~this;
	}

	@:op(A & B) public inline function bitwiseAND(other: DebugDrawMode): DebugDrawMode {
		return this & other;
	}

	@:op(A | B) public inline function bitwiseOR(other: DebugDrawMode): DebugDrawMode {
		return this | other;
	}
}

#end
