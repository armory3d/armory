package armory.logicnode;

class BooleanNode extends Node {

	public var value:Bool;

	public function new(tree:LogicTree, value = false) {
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
