package armory.logicnode;

import iron.object.MeshObject;
import iron.data.MaterialData;

class SetMaterialNode extends LogicNode {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run() {
		var object:MeshObject = inputs[1].get();
		var mat:MaterialData = inputs[2].get();
		
		if (object == null) return;

		object.materials[0] = mat;

		super.run();
	}
}
