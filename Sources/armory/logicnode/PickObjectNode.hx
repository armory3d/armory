package armory.logicnode;

import iron.math.Vec4;

class PickObjectNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		var coords: Vec4 = inputs[0].get();
		var mask: Int = inputs[1].get();

		if (coords == null) return null;

#if arm_physics
		var physics = armory.trait.physics.PhysicsWorld.active;
		var rb = physics.pickClosest(coords.x, coords.y, mask);
		if (rb == null) return null;

		if (from == 0) { // Object
			return rb.object;
		}
		else if(from == 1){ // Hit
			var v = new Vec4();
			return v.set(physics.hitPointWorld.x, physics.hitPointWorld.y, physics.hitPointWorld.z);
		}
		else { // Normal
			var v = new Vec4();
			return v.set(physics.hitNormalWorld.x, physics.hitNormalWorld.y, physics.hitNormalWorld.z, 0);
		}
#end
		return null;
	}
}
