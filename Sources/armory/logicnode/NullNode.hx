package armory.logicnode;

class NullNode extends Node {

	public function new(trait:armory.Trait) {
		super(trait);
	}

	override function get(from:Int):Dynamic { return null; }
}
