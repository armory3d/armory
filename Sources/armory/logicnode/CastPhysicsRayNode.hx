package armory.logicnode;

import iron.math.Vec4;

class CastPhysicsRayNode extends LogicNode {

	var v = new Vec4();

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		var vfrom: Vec4 = inputs[0].get();
		var vto: Vec4 = inputs[1].get();
		var mask: Int = inputs[2].get();

		if (vfrom == null || vto == null) return null;

#if arm_physics
		var physics = armory.trait.physics.PhysicsWorld.active;
		var hit = physics.rayCast(vfrom, vto, mask);
		var rb = (hit != null) ? hit.rb : null;

		if (from == 0) { // Object
			if (rb != null) return rb.object;
		}
		else if (from == 1) { // Hit
			var hitPointWorld: Vec4 = rb != null ? physics.hitPointWorld : null;
			if (hitPointWorld != null) {
				v.set(hitPointWorld.x, hitPointWorld.y, hitPointWorld.z, 1);
				return v;
			}
		}
		else { // Normal
			var hitNormalWorld: Vec4 = rb != null ? physics.hitNormalWorld : null;
			if (hitNormalWorld != null) {
				v.set(hitNormalWorld.x, hitNormalWorld.y, hitNormalWorld.z, 0);
				return v;
			}
		}
#end
		return null;
	}
}
