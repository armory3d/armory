package armory.logicnode;

import iron.object.Object;
import iron.math.Vec4;
import armory.trait.physics.RigidBody;

class GetGravityNode extends LogicNode {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function get(from:Int):Dynamic {
		
#if arm_physics
        var physics = armory.trait.physics.PhysicsWorld.active;
		return physics.world.getGravity();
#end

		return null;
	}
}
