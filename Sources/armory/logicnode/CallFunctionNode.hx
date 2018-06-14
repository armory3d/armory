package armory.logicnode;

import iron.object.Object;

class CallFunctionNode extends LogicNode {

	var result:Dynamic;

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run() {
		var object:Object = inputs[1].get();
		if (object == null) return;
		
		var funName:String = inputs[2].get();
		
		result = Reflect.callMethod(object, Reflect.field(object, funName), null);

		runOutputs(0);
	}

	override function get(from:Int):Dynamic {
		return result;
	}
}
