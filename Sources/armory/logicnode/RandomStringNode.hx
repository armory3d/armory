package armory.logicnode;

class RandomStringNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		var length: Int = inputs[0].get();
		var characters: String = inputs[1].get();

		var chars: Array<String> = characters.split('');

		var buf = new StringBuf();

		while(buf.length < length)
			buf.add(chars[Std.random(chars.length)]);

		return buf.toString();
	}
}
