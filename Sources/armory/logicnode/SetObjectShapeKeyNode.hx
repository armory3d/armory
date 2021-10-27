package armory.logicnode;

import iron.object.MeshObject;

class SetObjectShapeKeyNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		var object: Dynamic = inputs[1].get();
		var shapeKey: String = inputs[2].get();
		var value: Dynamic = inputs[3].get();

		if (object == null) return;
		var sk = cast(object, MeshObject).morphTarget;
		if(sk == null) return;

		sk.setMorphValue(shapeKey, value);
		runOutput(0);
	}
}
