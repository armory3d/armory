package armory.logicnode;

class SetTraitPausedNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		var trait: Dynamic = inputs[1].get();
		var paused: Bool = inputs[2].get();

		if (trait == null || !Std.is(trait, LogicTree)) return;

		paused ? cast(trait, LogicTree).resume() : cast(trait, LogicTree).pause();

		runOutput(0);
	}
}
