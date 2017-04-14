package armory.logicnode;

import armory.object.Object;
import armory.math.Vec4;

class SetScaleNode extends LogicNode {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run() {
		var object:Object = inputs[1].get();
		var vec:Vec4 = inputs[2].get();

		if (object == null) object = tree.object;

		object.transform.scale.setFrom(vec);
		object.transform.buildMatrix();

		super.run();
	}
}
