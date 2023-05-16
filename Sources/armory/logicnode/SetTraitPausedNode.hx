package armory.logicnode;

class SetTraitPausedNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		var trait: Dynamic = inputs[1].get();
		var paused: Bool = inputs[2].get();

		if (trait == null || !Std.isOfType(trait, LogicTree)) return;

		paused ? cast(trait, LogicTree).pause() : cast(trait, LogicTree).resume();

		runOutput(0);
	}
}
