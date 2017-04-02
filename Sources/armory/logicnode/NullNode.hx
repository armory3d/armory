package armory.logicnode;

class NullNode extends Node {

	public function new(trait:armory.Trait) {
		super(trait);
	}

	override function get():Dynamic { return null; }
}
