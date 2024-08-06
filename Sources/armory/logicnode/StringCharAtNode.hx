package armory.logicnode;

class StringCharAtNode extends LogicNode {
	public var char: String;

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run(from:Int) {
	    var string: String = inputs[1].get();
	    var index: Int = inputs[2].get();
	    char = string.charAt(index);
		  runOutput(0);
	}

	override function get(from: Int): String {
		return char;
	}

}
