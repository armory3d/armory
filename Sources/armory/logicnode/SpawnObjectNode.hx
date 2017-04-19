package armory.logicnode;

import armory.object.Object;
import armory.math.Mat4;

class SpawnObjectNode extends LogicNode {

	var object:Object;

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run() {

		var objectNode = cast(inputs[1].node, ObjectNode);
		var objectName:String = objectNode.objectName != "" ? objectNode.objectName : tree.object.name;
		var matrix:Mat4 = inputs[2].get();

		Scene.active.spawnObject(objectName, null, function(o:armory.object.Object) {
			object = o;
			if (matrix != null) object.transform.setMatrix(matrix);
			object.visible = true;
			runOutputs(0);
		});
	}

	override function get(from:Int):Dynamic {
		return object;
	}
}
