package armory.logicnode;

import iron.data.SceneFormat.TObj;
import iron.math.Mat4;
import iron.object.Object;

class SpawnCollectionNode extends LogicNode {

	/** Collection name **/
	public var property0: Null<String>;

	var topLevelObjects: Array<Object>;
	var allObjects: Array<Object>;
	var ownerObject: Null<Object>;

	public function new(tree: LogicTree) {
		super(tree);

		// Return empty arrays if not executed
		topLevelObjects = new Array();
		allObjects = new Array();
	}

	override function run(from: Int) {
		var raw = iron.Scene.active.raw;

		if (property0 == null) return;

		// Check if the group exists
		for (g in raw.groups) {
			if (g.name == property0) {

				var transform: Mat4 = inputs[1].get();
				if (transform == null) transform = Mat4.identity();

				// Create owner object that instantiates the group
				var rawOwnerObject: TObj = {
					name: property0,
					type: "object",
					group_ref: property0,
					data_ref: "",
					transform: {
						values: transform.toFloat32Array()
					}
				};
				raw.objects.push(rawOwnerObject);

				iron.Scene.active.createObject(rawOwnerObject, raw, null, null,
					(created: Object) -> {
						ownerObject = created;
						topLevelObjects = created.getChildren(false);
						allObjects = created.getChildren(true);

						runOutput(0);
					}
				);
				return;
			}
		}
	}

	override function get(from: Int): Dynamic {
		switch (from) {
			case 1: return topLevelObjects;
			case 2: return allObjects;
			case 3: return ownerObject;
		}
		return null;
	}
}
