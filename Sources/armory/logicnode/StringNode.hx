package armory.logicnode;

class StringNode extends Node {

	public var val:String = '';

	public function new() {
		super();
	}

	public static function create(s:String) {
		var n = new StringNode();
		n.val = s;
		return n;
	}
}
