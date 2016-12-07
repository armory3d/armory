package armory.logicnode;

#if arm_physics
import haxebullet.Bullet;
import armory.trait.internal.PhysicsWorld;
#end

import armory.trait.internal.NodeExecutor;
import iron.math.Vec4;

class PickLocationNode extends LocationNode {

	public static inline var _target = 0; // Target
	public static inline var _coords = 1; // Vector

	public function new() {
		super();
	}

	public override function start(executor:NodeExecutor, parent:Node = null) {
		super.start(executor, parent);

		executor.notifyOnNodeInit(init);
	}

	function init() {

	}

	override function fetch() {
#if arm_physics
		var physics = armory.trait.internal.PhysicsWorld.active;
		
		var coords = inputs[_coords];
		coords.fetch();
		var b = physics.pickClosest(coords.x, coords.y);
		var rb = inputs[_target].target.getTrait(armory.trait.internal.RigidBody);

		if (rb != null && b == rb) {
			#if js
			var p:BtVector3 = physics.rayCallback.get_m_hitPointWorld();
			#elseif cpp
			var p:BtVector3 = physics.rayCallback.value.m_hitPointWorld;
			#end
			loc.set(p.x(), p.y(), p.z());
		}
#end
	}

	public static function create(target:iron.object.Object, p:iron.math.Vec4):PickLocationNode {
		var n = new PickLocationNode();
		n.inputs.push(target);
		n.inputs.push(p);
		return n;
	}
}
