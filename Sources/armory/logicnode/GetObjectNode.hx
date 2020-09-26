package armory.logicnode;

import iron.data.SceneFormat;
import iron.object.Object;

class GetObjectNode extends LogicNode {

	/** Scene from which to take the object **/
	public var property0: Null<String>;

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		var objectName: String = inputs[0].get();

		if (property0 == null || property0 == iron.Scene.active.raw.name) {
			return iron.Scene.active.getChild(objectName);
		}

		#if arm_json
		property0 += ".json";
		#elseif arm_compress
		property0 += ".lz4";
		#end

		var outObj: Null<Object> = null;

		// Create the object in the active scene if it is from an inactive scene
		iron.data.Data.getSceneRaw(property0, (rawScene: TSceneFormat) -> {
			var objData: Null<TObj> = null;

			for (o in rawScene.objects) {
				if (o.name == objectName) {
					objData = o;
					break;
				}
			}
			if (objData == null) return;

			iron.Scene.active.createObject(objData, rawScene, null, null, (newObj: Object) -> {
				outObj = newObj;
			});
		});

		return outObj;
	}
}
