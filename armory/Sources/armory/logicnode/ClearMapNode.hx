package armory.logicnode;


class ClearMapNode extends LogicNode {
  
	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		var map: Map<Dynamic,Dynamic> = inputs[1].get();
		if (map == null) return null;

		map.clear();
		runOutput(0);
		return;
	}
	
}
