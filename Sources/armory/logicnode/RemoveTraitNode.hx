package armory.logicnode;

import armory.object.Object;

class RemoveTraitNode extends LogicNode {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run() {
		var trait:Dynamic = inputs[1].get();
		trait.remove();

		super.run();
	}
}
