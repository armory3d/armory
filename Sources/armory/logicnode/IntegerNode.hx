package armory.logicnode;

class IntegerNode extends LogicNode {

	public var value:Int;

	public function new(tree:LogicTree, value = 0) {
		super(tree);
		this.value = value;
	}

	override function get(from:Int):Dynamic {
		if (inputs.length > 0) return inputs[0].get();
		return value;
	}

	override function set(value:Dynamic) {
		this.value = value;
	}
}
