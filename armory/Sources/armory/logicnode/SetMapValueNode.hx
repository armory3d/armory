package armory.logicnode;


class SetMapValueNode extends LogicNode {
  
	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run(from:Int) {
		var map: Map<Dynamic,Dynamic> = inputs[1].get();
		if (map == null) return null;
		var key: Dynamic = inputs[2].get();
		var value: Dynamic = inputs[3].get();
		map[key] = value;
        runOutput(0);
        return;
	}

}
