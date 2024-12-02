package armory.logicnode;

import iron.object.Object;

class CallFunctionNode extends LogicNode {

	var result: Dynamic;

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		var object: Dynamic = inputs[1].get();
		if (object == null) return;

		var funName: String = inputs[2].get();
		var args: Array<Dynamic> = [];

		for (i in 3...inputs.length) {
			args.push(inputs[i].get());
		}

		var func = Reflect.field(object, funName);
		if (func != null) {
			result = Reflect.callMethod(object, func, args);
		}

		runOutput(0);
	}

	override function get(from: Int): Dynamic {
		return result;
	}
}
