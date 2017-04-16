package armory.logicnode;

import armory.object.Object;

class GetDistanceNode extends LogicNode {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function get(from:Int):Dynamic {
		var object1:Object = inputs[0].get();
		var object2:Object = inputs[1].get();

		return armory.math.Vec4.distance3d(object1.transform.abs, object2.transform.abs);
	}
}
