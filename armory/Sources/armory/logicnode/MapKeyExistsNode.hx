package armory.logicnode;


class MapKeyExistsNode extends LogicNode {
  
	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		var map: Map<Dynamic,Dynamic> = inputs[1].get();
		if (map == null) return null;

		var key: Dynamic = inputs[2].get();

		if (map.exists(key)) {
			runOutput(0);
			return;
		} else {
			runOutput(1);
			return;
		}
	}

}
