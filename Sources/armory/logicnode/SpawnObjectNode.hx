package armory.logicnode;

import iron.object.Object;
import iron.math.Mat4;
import armory.trait.physics.RigidBody;

class SpawnObjectNode extends LogicNode {

	var object: Object;
	var matrices: Array<Mat4> = [];

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		var objectInput = inputs[1].get();
		if (objectInput == null) return;

		var objectName = objectInput.name;
		if (objectName == "") objectName = tree.object.name;

		var m: Mat4 = inputs[2].get();
		matrices.push(m != null ? m.clone() : null);
		var spawnChildren: Bool = inputs.length > 3 ? inputs[3].get() : true; // TODO

		iron.Scene.active.spawnObject(objectName, null, function(o: Object) {
			object = o;
			var matrix = matrices.pop(); // Async spawn in a loop, order is non-stable
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
			runOutput(0);
		}, spawnChildren);
	}

	override function get(from: Int): Dynamic {
		return object;
	}
}
