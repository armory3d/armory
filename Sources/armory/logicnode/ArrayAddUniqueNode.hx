package armory.logicnode;

class ArrayAddUniqueNode extends LogicNode {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run() {
		var ar:Array<Dynamic> = inputs[1].get();
		
		if (inputs.length > 2) {
			for (i in 2...inputs.length) {
				var value:Dynamic = inputs[i].get();
				if (ar.indexOf(value) == -1) ar.push(value);
			}
		}

		super.run();
	}
}
