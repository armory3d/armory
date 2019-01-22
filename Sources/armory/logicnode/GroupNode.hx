package armory.logicnode;

import iron.Scene;
import iron.object.Object;

class GroupNode extends LogicNode {

	public var property0:String;

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function get(from:Int):Dynamic { 
		return Scene.active.getGroup(property0);
	}
}
