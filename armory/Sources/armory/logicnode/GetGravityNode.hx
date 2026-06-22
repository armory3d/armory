package armory.logicnode;

class GetGravityNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {

#if arm_physics
		var physics = armory.trait.physics.PhysicsWorld.active;

		return physics.getGravity();
#end

		return null;
	}
}
