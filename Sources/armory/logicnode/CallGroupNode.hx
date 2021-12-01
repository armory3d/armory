package armory.logicnode;

class CallGroupNode extends LogicNode {

	public var property0: String;
	var callTree: LogicTree = null;

	public function new(tree: LogicTree) {
		super(tree);
	}

	@:access(iron.Trait)
	override function run(from: Int) {

		if (callTree == null) {
			var classType = Type.resolveClass(property0);
			callTree = Type.createInstance(classType, []);
			callTree.object = tree.object;
			callTree.add();
		}

		var args = [];
		args.push(from);
		var func = Reflect.field(callTree, "runGroupInput");
		Reflect.callMethod(callTree, func, args);
		runOutput(0);
	}

	override function get(from:Int):Dynamic {
		return inputs[from].get();
	}
}
