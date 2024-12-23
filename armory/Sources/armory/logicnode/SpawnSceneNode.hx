package armory.logicnode;

import iron.object.Object;
import iron.math.Mat4;

class SpawnSceneNode extends LogicNode {

	var root: Object;

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {

		var sceneName: String = inputs[1].get();
		var matrix: Mat4 = inputs[2].get();

		root = iron.Scene.active.addObject();
		root.name = sceneName;
		if (matrix != null) {
			root.transform.setMatrix(matrix);
			root.transform.buildMatrix();
		}

		iron.Scene.active.addScene(sceneName, root, function(o: Object) {
			runOutput(0);
		});
	}

	override function get(from: Int): Dynamic {
		return root;
	}
}
