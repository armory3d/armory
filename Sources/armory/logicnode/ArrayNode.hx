package armory.logicnode;

class ArrayNode extends Node {

	public var value:Array<Dynamic> = [];

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function get(from:Int):Dynamic { 
		return from == 0 ? value : value.length;
	}

	override function set(value:Dynamic) {
		this.value = value;
	}
}
