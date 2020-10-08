package armory.logicnode;

class SetTraitEnabledNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		var trait: Dynamic = inputs[1].get();
		var enabled: Bool = inputs[2].get();

		if (trait == null || !Std.is(trait, LogicTree)) return;

		enabled ? cast(trait, LogicTree).resume() : cast(trait, LogicTree).pause();

		runOutput(0);
	}
}
