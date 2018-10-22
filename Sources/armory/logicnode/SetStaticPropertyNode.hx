package armory.logicnode;

class SetStaticPropertyNode extends LogicNode {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run(from:Int) {
		var className:String = inputs[1].get();
		var property:String = inputs[2].get();
		var value:Dynamic = inputs[3].get();
		
		var cl = Type.resolveClass(className);
		if (cl == null) return;
        Reflect.setField(cl, property, value);

		runOutput(0);
	}
}
