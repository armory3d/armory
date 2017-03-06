package armory.logicnode;

class BoolNode extends Node {

	public var value:Bool;

	public function new(trait:armory.Trait, value = false) {
		super(trait);
		this.value = value;
	}

	override function get():Dynamic {
		if (inputs.length > 0) return inputs[0].get();
		return value;
	}
}
