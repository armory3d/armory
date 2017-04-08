package armory.logicnode;

import armory.object.Object;

class SetSceneNode extends LogicNode {

	var root:Object;

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run() {
		var sceneName:String = inputs[1].get();

		Scene.setActive(sceneName, function(o:armory.object.Object) {
			root = o;
			runOutputs(0);
		});
	}

	override function get(from:Int):Dynamic {
		return root;
	}
}
