package armory.logicnode;

#if arm_physics
import armory.trait.physics.RigidBody;
#end
import iron.object.Object;
import iron.math.Vec4;
import iron.math.Quat;

class PhysicsConvexCastNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		var convex: Object = inputs[0].get();
		var vfrom: Vec4 = inputs[1].get();
		var vto: Vec4 = inputs[2].get();
		var rot: Quat = inputs[3].get();
		var mask: Int = inputs[4].get();

		if (vfrom == null || vto == null) return null;

#if arm_physics
		var rb = convex.getTrait(RigidBody);
		if(rb == null) return null;
		var physics = armory.trait.physics.PhysicsWorld.active;
		var hit = physics.convexSweepTest(rb, vfrom, vto, rot, mask);

		if (from == 0) { // Hit Position
			if (hit != null) return hit.pos;
		}
		else if (from == 1) { // RB Position
			if (hit != null) {
				var d = Vec4.distance(vfrom, vto);
				var v = new Vec4();
				v.subvecs(vto, vfrom).normalize();
				v.mult(d * hit.hitFraction);
				v.add(vfrom);
				return v;
			}
		}
		else if (from == 2) { // Hit
			if (hit != null) return hit.normal;
		}
#end
		return null;
	}
}
