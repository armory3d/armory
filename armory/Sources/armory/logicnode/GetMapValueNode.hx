package armory.logicnode;


class GetMapValueNode extends LogicNode {
  
	public function new(tree:LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		var map: Map<Dynamic,Dynamic> = inputs[0].get();
		if (map == null) return null;

		var key: Dynamic = inputs[1].get();
		return map.get(key);   
	}
}
