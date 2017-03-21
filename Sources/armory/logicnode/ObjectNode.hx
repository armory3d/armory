package armory.logicnode;

class ObjectNode extends Node {

	public var property0:String;

	public function new(trait:armory.Trait) {
		super(trait);
	}

	override function get():Dynamic { return armory.Scene.active.getChild(property0); }
}
