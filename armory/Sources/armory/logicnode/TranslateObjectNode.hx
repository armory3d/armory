package armory.logicnode;

import iron.object.Object;
import iron.math.Vec4;
import armory.trait.physics.RigidBody;

using armory.object.TransformExtension;

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
			object.transform.loc.add(object.transform.worldVecToOrientation(vec));
			object.transform.buildMatrix();
		}

#if arm_physics
		var rigidBody = object.getTrait(RigidBody);

		if (rigidBody != null) rigidBody.syncTransform();
#end

		runOutput(0);
	}

}
