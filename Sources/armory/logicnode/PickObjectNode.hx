package armory.logicnode;

import armory.math.Vec4;

class PickObjectNode extends Node {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function get(from:Int):Dynamic {
		var coords:Vec4 = inputs[0].get();

#if arm_physics
		var physics = armory.trait.internal.PhysicsWorld.active;
		var rb = physics.pickClosest(coords.x, coords.y);
		return rb.object;
#end
		return null;
	}
}
