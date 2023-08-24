package armory.logicnode;

import iron.object.Object;
import armory.trait.physics.RigidBody;

class TranslateOnLocalAxisNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		var object: Object = inputs[1].get();
		var sp: Float = inputs[2].get();
		var l: Int = inputs[3].get();
		var ini: Bool = inputs[4].get();

		if (object == null) return;

		if (ini) sp *= -1;

		if (l == 1) object.transform.move(object.transform.local.look(),sp);
		else if (l == 2) object.transform.move(object.transform.local.up(),sp);
		else if (l == 3) object.transform.move(object.transform.local.right(),sp);

		object.transform.buildMatrix();

		#if arm_physics
		var rigidBody = object.getTrait(RigidBody);
		if (rigidBody != null) rigidBody.syncTransform();
		#end

		runOutput(0);
	}
}
