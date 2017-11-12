package armory.trait.physics.oimo;

#if arm_oimo

import iron.Trait;
import iron.system.Time;
import iron.math.Vec4;
import iron.math.RayCaster;
import iron.data.SceneFormat;
import oimo.physics.dynamics.World;

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

	#if arm_debug
	public static var physTime = 0.0;
	#end

	public static var active:PhysicsWorld = null;
	public var world:World;
	public var rbMap:Map<Int, RigidBody>;
	var preUpdates:Array<Void->Void> = null;
	static inline var timeStep = 1 / 60;
	static inline var fixedStep = 1 / 60;
	public var hitPointWorld = new Vec4();

	public function new() {
		super();

		if (active == null) {
			createPhysics();
		}
		else {
			for (rb in active.rbMap) removeRigidBody(rb);
			this.world = active.world;
		}

		rbMap = new Map();
		active = this;

		Scene.active.notifyOnInit(function() {
			notifyOnUpdate(update);
		});
	}

	function createPhysics() {
		
		// var gravity = iron.Scene.active.raw.gravity == null ? gravityArray() : iron.Scene.active.raw.gravity;
		world = new World();
	}

	// function gravityArray():TFloat32Array {
	// 	var ar = new TFloat32Array(3);
	// 	ar[0] = 0.0;
	// 	ar[1] = 0.0;
	// 	ar[2] = -9.81;
	// 	return ar;
	// }

	public function addRigidBody(body:RigidBody) {
		world.addRigidBody(body.body);
		rbMap.set(body.id, body);
	}

	public function removeRigidBody(body:RigidBody) {
		if (world != null) world.removeRigidBody(body.body);
		rbMap.remove(body.id);
	}

	public function getContacts(body:RigidBody):Array<RigidBody> {
		var res:Array<RigidBody> = [];
		return res;
	}

	public function getContactPairs(body:RigidBody):Array<ContactPair> {
		var res:Array<ContactPair> = [];
		return res;
	}

	public function update() {
		#if arm_debug
		var startTime = kha.Scheduler.realTime();
		#end

		if (preUpdates != null) for (f in preUpdates) f();

		world.step(timeStep);

		#if arm_debug
		physTime = kha.Scheduler.realTime() - startTime;
		#end
	}

	public function pickClosest(inputX:Float, inputY:Float):RigidBody {
		return null;
	}

	public function rayCast(from:Vec4, to:Vec4):RigidBody {
		return null;
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
