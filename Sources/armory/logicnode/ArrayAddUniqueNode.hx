package armory.logicnode;

class ArrayAddUniqueNode extends LogicNode {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run() {
		var ar:Array<Dynamic> = inputs[1].get();
		var value:Dynamic = inputs[2].get();
		if (ar.indexOf(value) == -1) ar.push(value);

		super.run();
	}
}
