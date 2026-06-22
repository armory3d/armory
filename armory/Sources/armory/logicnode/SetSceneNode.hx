package armory.logicnode;

import iron.object.Object;

class SetSceneNode extends LogicNode {

	var root: Object;

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		var sceneName: String = inputs[1].get();

		#if arm_json
		sceneName += ".json";
		#elseif arm_compress
		sceneName += ".lz4";
		#end

		iron.Scene.setActive(sceneName, function(o: iron.object.Object) {
			root = o;
			runOutput(0);
		});
	}

	override function get(from: Int): Dynamic {
		return root;
	}
}
