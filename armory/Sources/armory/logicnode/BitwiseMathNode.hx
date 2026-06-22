package armory.logicnode;

class BitwiseMathNode extends LogicNode {

	/** The operation to perform. **/
	public var property0: String;

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		final op1: Int = inputs[0].get();

		if (property0 == "negation") {
			return ~op1;
		}

		final op2: Int = inputs[1].get();

		return switch (property0) {
			case "and": op1 & op2;
			case "or": op1 | op2;
			case "xor": op1 ^ op2;

			case "left_shift": op1 << op2;
			case "right_shift": op1 >> op2;
			case "unsigned_right_shift": op1 >>> op2;

			default: 0;
		}
	}
}
