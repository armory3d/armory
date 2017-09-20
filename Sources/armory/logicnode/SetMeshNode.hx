package armory.logicnode;

import armory.object.MeshObject;
import armory.data.MeshData;

class SetMeshNode extends LogicNode {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run() {
		var object:MeshObject = inputs[1].get();
		var mesh:MeshData = inputs[2].get();
		
		if (object == null) return;

		object.data = mesh;

		super.run();
	}
}
