package armory.logicnode;

class MathNode extends LogicNode {

	public var property0:String;

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function get(from:Int):Dynamic {
		var v1:Float = inputs[0].get();
		var v2:Float = inputs[1].get();
		switch (property0) {
		case "Add":
			return v1 + v2;
		case "Multiply":
			return v1 * v2;
		case "Sine":
			return Math.sin(v1);
		case "Cosine":
			return Math.cos(v1);
		case "Max":
			return Math.max(v1, v2);
		case "Min":
			return Math.min(v1, v2);
		case "Abs":
			return Math.abs(v1);
		default:
			return 0.0;
		}
	}
}
