package armory.logicnode;

class ArrayBooleanNode extends LogicNode {

	public var value: Array<Bool> = [];
	var initialized = false;

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		if (!initialized) {
			initialized = true;
			for (inp in inputs) {
				var val: Bool = inp.get();
				value.push(val);
			}
		}

		return from == 0 ? value : value.length;
	}

	override function set(value: Dynamic) {
		this.value = value;
	}
}
