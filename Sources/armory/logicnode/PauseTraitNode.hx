package armory.logicnode;

class PauseTraitNode extends LogicNode {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run() {
		var trait:Dynamic = inputs[1].get();
		if (trait == null || !Std.is(trait, LogicTree)) return;

		cast(trait, LogicTree).pause();

		super.run();
	}
}
