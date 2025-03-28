package armory.logicnode;

import iron.object.Object;
import armory.trait.physics.RigidBody;

class SetParentNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		var object: Object = inputs[1].get();
		var parentObject: Object = inputs[2].get();
		var keepTransform: Bool = inputs[3].get();
		var parentInverse: Bool = inputs[4].get();

		if (object == null || parentObject == null || object.parent == parentObject) return;

		#if arm_physics
		var rigidBody = object.getTrait(RigidBody);
		if (rigidBody != null) rigidBody.setActivationState(0);
		#end

		object.setParent(parentObject, parentInverse, keepTransform);
		runOutput(0);
	}
}
