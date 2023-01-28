package armory.logicnode;

class RandomStringNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		var length: Int = inputs[0].get();
		var chars: Array<String> = inputs[1].get();

		var string: String = '';

		while(string.length < length)
			string += chars[Std.random(chars.length)];

		return string;
	}
}
