package armory.logicnode;

using StringTools;

class RandomStringNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		var length: Int = inputs[0].get();
		var characters: String = inputs[1].get();

		var buf = new StringBuf();

		while(buf.length < length) {
			buf.addChar(characters.fastCodeAt(Std.random(characters.length)));
		}

		return buf.toString();
	}
}
