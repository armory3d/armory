package armory.logicnode;

import armory.object.MeshObject;

class GetMeshNode extends LogicNode {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function get(from:Int):Dynamic {
		var object:MeshObject = inputs[0].get();

		if (object == null) object = cast(tree.object, MeshObject);

		return object.data;
	}
}
