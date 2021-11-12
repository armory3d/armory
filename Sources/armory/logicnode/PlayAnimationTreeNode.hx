package armory.logicnode;

import iron.object.Object;
import iron.object.ObjectAnimation;
import iron.object.BoneAnimation;
import iron.Scene;

class PlayAnimationTreeNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		var object: Object = inputs[1].get();
		var action: Dynamic = inputs[2].get();

		assert(Error, object != null, "The object input not be null");
		var animation = object.animation;
		if(animation == null) {
			animation = object.getParentArmature(object.name);
			cast(animation, BoneAnimation).animationLoop(function f(mats) {
				action(mats);
			});
		}
		else{
			cast(animation, ObjectAnimation).animationLoop(function f(mats) {
				action(mats);
			});
		}
		
		runOutput(0);
	}
}
