package armory.logicnode;

import iron.object.Object;
import armory.trait.physics.RigidBody;

class ClearParentNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		var object: Object = inputs[1].get();
		var keepTransform: Bool = inputs[2].get();

		if (object == null || object.parent == null) return;

		object.setParent(iron.Scene.active.root, false, keepTransform);

		#if arm_physics
		var rigidBody = object.getTrait(RigidBody);
		if (rigidBody != null) rigidBody.syncTransform();
		#end

		runOutput(0);
	}
}
