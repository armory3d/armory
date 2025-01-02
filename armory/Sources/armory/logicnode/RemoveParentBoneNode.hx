package armory.logicnode;

import iron.object.Object;

class RemoveParentBoneNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		#if arm_skin

		var object: Object = inputs[1].get();
		var parent: Object = inputs[2].get();
		var bone: String = inputs[3].get();

		if (object == null || parent == null) return;

		var banim = object.getParentArmature(object.parent.name);
		banim.removeBoneChild(bone, object);

		runOutput(0);

		#end
	}
}
