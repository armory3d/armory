package armory.logicnode;

#if arm_physics
import armory.trait.physics.RigidBody;
#end
import iron.object.Object;
import iron.math.Vec4;
import iron.math.Quat;

class PhysicsConvexCastOnNode extends LogicNode {

	var hitPos: Vec4 = null;
	var convexPos: Vec4 = null;
	var hitNormal: Vec4 = null;

	public function new(tree: LogicTree) {
		super(tree);
	}

	function reset() {
		hitPos = null;
		convexPos = null;
		hitNormal = null;
	}

	override function run(from:Int) {
		reset();

		var convex: Object = inputs[1].get();
		var vfrom: Vec4 = inputs[2].get();
		var vto: Vec4 = inputs[3].get();
		var rot: Quat = inputs[4].get();
		var mask: Int = inputs[5].get();

#if arm_physics
		if (vfrom != null && vto != null) {
			var rb = convex.getTrait(RigidBody);
			var physics = armory.trait.physics.PhysicsWorld.active;
			var hit = physics.convexSweepTest(rb, vfrom, vto, rot, mask);
			if(hit != null) {
				hitPos = new Vec4().setFrom(hit.pos);
				var d = Vec4.distance(vfrom, vto);
				var v = new Vec4();
				v.subvecs(vto, vfrom).normalize();
				v.mult(d * hit.hitFraction);
				v.add(vfrom);
				convexPos = new Vec4().setFrom(v);

				hitNormal = new Vec4().setFrom(physics.hitNormalWorld);
			}
		}
#end
		runOutput(0);
	}

	override function get(from: Int): Dynamic {
		if (from == 1) { // Hit Position
			return hitPos;
		}
		else if (from == 2) { // RB Position
			return convexPos;
		}
		else { // Normal
			return hitNormal;
		}
		return null;
	}
}
