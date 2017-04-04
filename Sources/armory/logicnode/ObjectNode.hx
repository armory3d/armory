package armory.logicnode;

import armory.object.Object;

class ObjectNode extends Node {

	public var property0:String;
	public var value:Object;

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function get(from:Int):Dynamic { 
		value = armory.Scene.active.getChild(property0);
		return value;
	}

	override function set(value:Dynamic) {
		this.value = value;
	}
}
