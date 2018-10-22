package armory.logicnode;

class ArrayAddUniqueNode extends LogicNode {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run(from:Int) {
		var ar:Array<Dynamic> = inputs[1].get();
		if (ar == null) return;
		
		if (inputs.length > 2) {
			for (i in 2...inputs.length) {
				var value:Dynamic = inputs[i].get();
				if (ar.indexOf(value) == -1) ar.push(value);
			}
		}

		runOutput(0);
	}
}
