package armory.logicnode;

import iron.data.SceneFormat;
import iron.object.Object;

class GetObjectByUidNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		var objectUid: Int = inputs[0].get();
		
		var obj = iron.Scene.active.getChildren(true);
		
		for (obji in obj) if (obji.uid == objectUid) return obji;
		
		return null;
		
	}
}
