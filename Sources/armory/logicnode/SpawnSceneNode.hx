package armory.logicnode;

import armory.object.Object;
import armory.math.Mat4;

class SpawnSceneNode extends LogicNode {

	var root:Object;

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run() {

		var sceneName:String = inputs[1].get();
		var matrix:Mat4 = inputs[2].get();

		Scene.active.addScene(sceneName, null, function(o:armory.object.Object) {
			root = o;
			if (matrix != null) root.transform.setMatrix(matrix);
			runOutputs(0);
		});
	}

	override function get(from:Int):Dynamic {
		return root;
	}
}
