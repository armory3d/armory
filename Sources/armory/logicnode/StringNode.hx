package armory.logicnode;

class StringNode extends Node {

	public var value:String;

	public function new(tree:LogicTree, value = "") {
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
