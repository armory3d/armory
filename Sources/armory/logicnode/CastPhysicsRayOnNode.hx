package armory.logicnode;

import iron.object.Object;
import iron.math.Vec4;

class CastPhysicsRayOnNode extends LogicNode {

	var v = new Vec4();
	var hitRb: Object = null;
	var hitPos: Vec4 = null;
	var hitNormal: Vec4 = null;

	public function new(tree: LogicTree) {
		super(tree);
	}

	function reset() {
		hitRb = null;
		hitPos = null;
		hitNormal = null;
	}

	override function run(from:Int) {
		reset();

		var vfrom: Vec4 = inputs[1].get();
		var vto: Vec4 = inputs[2].get();
		var mask: Int = inputs[3].get();

#if arm_physics
		if (vfrom != null && vto != null) {
			var physics = armory.trait.physics.PhysicsWorld.active;
			var hit = physics.rayCast(vfrom, vto, mask);
			if(hit != null) {
				hitRb = hit.rb.object;
				hitPos = new Vec4().setFrom(physics.hitPointWorld);
				hitNormal = new Vec4().setFrom(physics.hitNormalWorld);
			}
		}
#end
		runOutput(0);
	}

	override function get(from: Int): Dynamic {
		if (from == 1) { // Object
			return hitRb;
		}
		else if (from == 2) { // Hit
			return hitPos;
		}
		else { // Normal
			return hitNormal;
		}
		return null;
	}
}
