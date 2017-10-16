package armory.logicnode;

import armory.object.Object;

class PlayActionNode extends LogicNode {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run() {
		var object:Object = inputs[1].get();
		var action:String = inputs[2].get();

		// TODO: deprecated
		var blendTime:Float = inputs.length > 3 ? inputs[3].get() : 0.2;
		
		if (object == null) return;

		// Try first child if we are running from armature
		if (object.animation == null) object = object.children[0];

		object.animation.play(action, function() {
			runOutputs(1);
		}, blendTime);

		runOutputs(0);
	}
}
