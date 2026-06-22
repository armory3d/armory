package armory.logicnode;

import iron.object.Object;
import iron.math.Quat;
import iron.math.Vec4;

class GetRotationNode extends LogicNode {

	public var property0: String;
	
	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		var object: Object = inputs[0].get();

		if (object == null) {
			return null;
		}


		switch(property0){
		case "Local":
			return object.transform.rot;
		case "Global":{
		        var useless1 = new Vec4();
			var ret = new Quat();
			object.transform.world.decompose(useless1, ret, useless1);
			return ret;
		}}
		return null;
	}
}
