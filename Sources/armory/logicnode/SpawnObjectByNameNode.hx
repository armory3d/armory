package armory.logicnode;

import iron.data.SceneFormat.TSceneFormat;
import iron.data.Data;
import iron.object.Object;
import iron.math.Mat4;
import armory.trait.physics.RigidBody;

class SpawnObjectByNameNode extends LogicNode {

	var object: Object;
	var matrices: Array<Mat4> = [];

	/** Scene from which to take the object **/
	public var property0: Null<String>;

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		var objectName = inputs[1].get();
		if (objectName == null) return;

		#if arm_json
		property0 += ".json";
		#elseif arm_compress
		property0 += ".lz4";
		#end

		var m: Mat4 = inputs[2].get();
		matrices.push(m != null ? m.clone() : null);
		var spawnChildren: Bool = inputs.length > 3 ? inputs[3].get() : true; // TODO

		Data.getSceneRaw(property0, (rawScene: TSceneFormat) -> {

			//Check if object with given name present in the specified scene
			var objPresent: Bool = false;

			for (o in rawScene.objects) {
				if (o.name == objectName) {
					objPresent = true;
					break;
				}
			}
			if (! objPresent) return;

			//Spawn object if present
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
			}, spawnChildren, rawScene);

		});
	}

	override function get(from: Int): Dynamic {
		return object;
	}
}
