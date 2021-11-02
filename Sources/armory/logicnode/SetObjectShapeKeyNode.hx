package armory.logicnode;

import iron.object.MeshObject;

class SetObjectShapeKeyNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		#if arm_morph_target
		var object: Dynamic = inputs[1].get();
		var shapeKey: String = inputs[2].get();
		var value: Dynamic = inputs[3].get();

		assert(Error, object != null, "Object should not be null");
		var morph = cast(object, MeshObject).morphTarget;

		assert(Error, morph != null, "Object does not have shape keys");
		morph.setMorphValue(shapeKey, value);
		#end
		runOutput(0);
	}
}
