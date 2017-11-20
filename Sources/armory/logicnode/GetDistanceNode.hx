package armory.logicnode;

import iron.object.Object;

class GetDistanceNode extends LogicNode {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function get(from:Int):Dynamic {
		var object1:Object = inputs[0].get();
		var object2:Object = inputs[1].get();

		return iron.math.Vec4.distance3d(object1.transform.world.getLoc(), object2.transform.world.getLoc());
	}
}
