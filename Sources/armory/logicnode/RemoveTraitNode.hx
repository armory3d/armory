package armory.logicnode;

import iron.object.Object;

class RemoveTraitNode extends LogicNode {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run() {
		var trait:Dynamic = inputs[1].get();
		if (trait == null) return;
		trait.remove();

		super.run();
	}
}
