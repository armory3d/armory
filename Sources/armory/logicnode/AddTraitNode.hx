package armory.logicnode;

import iron.object.Object;

class AddTraitNode extends LogicNode {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run(from:Int) {
		var object:Object = inputs[1].get();
		var trait:Dynamic = inputs[2].get();
		
		if (object == null || trait == null) return;

		object.addTrait(trait);

		runOutput(0);
	}
}
