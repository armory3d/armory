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
		
		return iron.Scene.active.getChild(objectName);
	}
}
