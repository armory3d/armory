package armory.logicnode;

class CallGroupNode extends Node {

	public var property0:String;
	var instance:LogicTree = null;

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run() {

		// Experimental only
		if (instance != null) tree.object.removeTrait(instance);

		var classType = Type.resolveClass(property0);
		instance = Type.createInstance(classType, []);

		tree.object.addTrait(instance);

		runOutputs(0);
	}
}
