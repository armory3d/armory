package armory.logicnode;

class IsNoneNode extends LogicNode {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run(node:LogicNode) {

		var v1:Dynamic = inputs[1].get();
		if (v1 == null) super.run(this);
	}
}
