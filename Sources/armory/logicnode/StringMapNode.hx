package armory.logicnode;


class StringMapNode extends LogicNode {

	public var property0: Int;
	public var map: Map<String, String> = [];
	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		map.clear();
		for(i in 0...property0) {
			map.set(inputs[i * 2 + 1].get(), inputs[i * 2 + 2].get());
		}
		runOutput(0);
	}

	override function get(from: Int):Dynamic {
		return map;
	}
	
}
