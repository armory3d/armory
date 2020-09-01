package armory.logicnode;

import iron.object.Object;
import iron.math.Vec4;
import armory.trait.physics.RigidBody;

class TranslateObjectNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		var object: Object = inputs[1].get();
		var vec: Vec4 = inputs[2].get();
		var local: Bool = inputs.length > 3 ? inputs[3].get() : false;

		if (object == null || vec == null) return;

		if (!local) {
			object.transform.loc.add(vec);
			object.transform.buildMatrix();
		}
		else {
			object.transform.move(object.transform.local.look(),vec.y);
			object.transform.move(object.transform.local.up(),vec.z);
			object.transform.move(object.transform.local.right(),vec.x);
			object.transform.buildMatrix();
		}

		#if arm_physics
		var rigidBody = object.getTrait(RigidBody);
		if (rigidBody != null) rigidBody.syncTransform();
		#end

		runOutput(0);
	}
}
