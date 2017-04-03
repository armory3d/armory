package armory.logicnode;

class ObjectNode extends Node {

	public var property0:String;
	public var value:Object;

	public function new(trait:armory.Trait) {
		super(trait);
	}

	override function get(from:Int):Dynamic { 
		value = armory.Scene.active.getChild(property0);
		return value;
	}

	override function set(value:Dynamic) {
		this.value = value;
	}
}
