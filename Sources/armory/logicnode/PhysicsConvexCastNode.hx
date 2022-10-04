package armory.logicnode;

#if arm_physics
import armory.trait.physics.RigidBody;
#end
import iron.object.Object;
import iron.math.Vec4;
import iron.math.Mat4;

class PhysicsConvexCastNode extends LogicNode {

	var v = new Vec4();

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		var convex: Object = inputs[0].get();
		var tfrom: Mat4 = inputs[1].get();
		var tto: Mat4 = inputs[2].get();
		var mask: Int = inputs[3].get();

		if (tfrom == null || tto == null) return null;

#if arm_physics
		var rb = convex.getTrait(RigidBody);
		if(rb == null) return null;
		var physics = armory.trait.physics.PhysicsWorld.active;
		var hit = physics.convexSweepTest(rb, tfrom, tto, mask);

		if (from == 0) { // Hit
			if (hit != null) return hit.pos;
		}
		else if (from == 1) { // Hit
			if (hit != null) return hit.normal;
		}
#end
		return null;
	}
}
