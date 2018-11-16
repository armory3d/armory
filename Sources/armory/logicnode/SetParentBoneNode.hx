package armory.logicnode;

import iron.object.Object;

class SetParentBoneNode extends LogicNode {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run(from:Int) {
		#if arm_skin

		var object:Object = inputs[1].get();
		var parent:Object = inputs[2].get();
		var bone:String = inputs[3].get();
		
		if (object == null || parent == null) return;

		if (object.parent != parent) {
			object.parent.removeChild(object, false); // keepTransform
			parent.addChild(object, false); // applyInverse
		}

		var banim = object.getParentArmature(object.parent.name);
		banim.addBoneChild(bone, object);

		runOutput(0);

		#end
	}
}
