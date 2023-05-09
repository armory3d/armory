package armory.logicnode;

class IsRigidBodyActiveNode extends LogicNode {
	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
#if arm_physics
		final object: iron.object.Object = inputs[0].get();

		if (object == null) {
			return false;
		}

		final rb = object.getTrait(armory.trait.physics.RigidBody);
		return rb != null && rb.isActive();
#else
		return false;
#end
	}
}
