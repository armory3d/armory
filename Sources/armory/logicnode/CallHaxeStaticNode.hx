package armory.logicnode;

class CallHaxeStaticNode extends LogicNode {

	var result: Dynamic;

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {

		var path: String = inputs[1].get();
		if (path != "") {
			var args: Array<Dynamic> = [];

			for (i in 2...inputs.length) {
				args.push(inputs[i].get());
			}
			
			var dotIndex = path.lastIndexOf(".");
			var classPath = path.substr(0, dotIndex);
			var classType = Type.resolveClass(classPath);
			var funName = path.substr(dotIndex + 1);
			result = Reflect.callMethod(classType, Reflect.field(classType, funName), args);
		}

		runOutput(0);
	}

	override function get(from: Int): Dynamic {
		return result;
	}
}
