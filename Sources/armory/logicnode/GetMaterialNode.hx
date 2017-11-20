package armory.logicnode;

import iron.object.MeshObject;

class GetMaterialNode extends LogicNode {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function get(from:Int):Dynamic {
		var object:MeshObject = inputs[0].get();

		if (object == null) return null;

		return object.materials[0];
	}
}
