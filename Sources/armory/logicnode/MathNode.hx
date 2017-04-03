package armory.logicnode;

class MathNode extends Node {

	public var property0:String;

	public function new(trait:armory.Trait) {
		super(trait);
	}

	override function get(from:Int):Dynamic {
		var v1 = inputs[0].get();
		var v2 = inputs[1].get();
		switch (property0) {
		case "Add":
			return v1 + v2;
		case "Multiply":
			return v1 * v2;
		case "Sine":
			return Math.sin(v1);
		case "Cosine":
			return Math.cos(v1);
		default:
			return 0.0;
		}
	}
}
