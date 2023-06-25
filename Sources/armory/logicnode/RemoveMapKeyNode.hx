package armory.logicnode;


class RemoveMapKeyNode extends LogicNode {
  
	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		var map: Map<Dynamic,Dynamic> = inputs[1].get();
		if (map == null) return;
		var key: Dynamic = inputs[2].get();
		map.remove(key);
		runOutput(0);
	}
	
}

