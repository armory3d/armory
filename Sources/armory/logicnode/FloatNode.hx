package armory.logicnode;

class FloatNode extends Node {

	public var value:Float;

	public function new(trait:armory.Trait, value = 0.0) {
		super(trait);
		this.value = value;
	}

	override function get():Dynamic {
		if (inputs.length > 0) return inputs[0].get();
		return value;
	}
}
