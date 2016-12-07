package armory.logicnode;

class IntNode extends Node {

	public var val:Int = 0;

	public function new() {
		super();
	}

	public static function create(i:Int) {
		var n = new IntNode();
		n.val = i;
		return n;
	}
}
