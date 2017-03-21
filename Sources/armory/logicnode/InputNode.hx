package armory.logicnode;

class InputNode extends Node {

	public function new(trait:armory.Trait) {
		super(trait);
	}

	override function get():Dynamic {
		return armory.system.Input.down;
	}
}
