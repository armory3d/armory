package armory.logicnode;

class ArrayRemoveNode extends LogicNode {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run() {
		var ar:Array<Dynamic> = inputs[1].get();
		var index:Int = inputs[2].get();
		ar.splice(index, 1);

		super.run();
	}
}
