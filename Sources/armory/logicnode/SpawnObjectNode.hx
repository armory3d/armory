package armory.logicnode;

import armory.object.Object;
import armory.math.Mat4;
#if arm_physics
import armory.trait.physics.RigidBody;
#end

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
			runOutputs(0);
		});
	}

	override function get(from:Int):Dynamic {
		return object;
	}
}
