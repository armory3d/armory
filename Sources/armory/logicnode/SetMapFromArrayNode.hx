package armory.logicnode;


class SetMapFromArrayNode extends LogicNode {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run(from:Int) {
		var map: Map<Dynamic,Dynamic> = inputs[1].get();
		if (map == null) return;
		
		var keys: Array<Dynamic> = inputs[2].get();
		var values: Array<Dynamic> = inputs[3].get();
		
		assert(Error, keys.length == values.length, "Number of keys and values should be equal");
		
		for(i in 0...keys.length) {
			map[keys[i]] = values[i];
		}
		runOutput(0);
	}

}
