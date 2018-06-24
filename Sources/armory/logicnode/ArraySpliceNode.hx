package armory.logicnode;

class ArraySpliceNode extends LogicNode {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run() {
		var ar:Array<Dynamic> = inputs[1].get();
		if (ar == null) return;

        var i = inputs[2].get();
        var len = inputs[3].get();

        ar.splice(i, len);

		super.run();
	}
}
