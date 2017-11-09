package armory.logicnode;

class CallGroupNode extends LogicNode {

	public var property0:String;
	var instance:Dynamic = null;

	public function new(tree:LogicTree) {
		super(tree);
	}

	@:access(iron.Trait)
	override function run() {

		if (instance == null) {
			var classType = Type.resolveClass(property0);
			instance = Type.createInstance(classType, []);
			instance.add();
		}

		if (instance._init != null) instance._init[0]();

		runOutputs(0);
	}
}
