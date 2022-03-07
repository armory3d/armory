package armory.logicnode;

import iron.object.Object;

class SetParentBoneNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		#if arm_skin

		var object: Object = inputs[1].get();
		var parent: Object = inputs[2].get();
		var bone: String = inputs[3].get();

		if (object == null || parent == null) return;

		object.setParent(parent, false, false);

		var banim = object.getBoneAnimation(object.parent.uid);
		banim.addBoneChild(bone, object);

		runOutput(0);

		#end
	}
}
