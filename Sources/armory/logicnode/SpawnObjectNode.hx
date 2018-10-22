package armory.logicnode;

import iron.object.Object;
import iron.math.Mat4;
import armory.trait.physics.RigidBody;

class SpawnObjectNode extends LogicNode {

	var object:Object;

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run(from:Int) {

		var objectName = "";
		var objectInput = inputs[1].get();
		if (objectInput == null) objectName = cast(inputs[1].node, ObjectNode).objectName;
		else objectName = objectInput.name;
		if (objectName == "") objectName = tree.object.name;
		var matrix:Mat4 = inputs[2].get();
		var spawnChildren:Bool = inputs.length > 3 ? inputs[3].get() : true; // TODO

		iron.Scene.active.spawnObject(objectName, null, function(o:Object) {
			object = o;
			if (matrix != null) {
				object.transform.setMatrix(matrix);
				#if arm_physics
				var rigidBody = object.getTrait(RigidBody);
				if (rigidBody != null) {
					object.transform.buildMatrix();
					rigidBody.syncTransform();
				}
				#end
			}
			object.visible = true;
			runOutput(0);
		}, spawnChildren);
	}

	override function get(from:Int):Dynamic {
		return object;
	}
}
