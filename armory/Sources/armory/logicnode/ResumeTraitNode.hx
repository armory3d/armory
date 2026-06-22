package armory.logicnode;

class ResumeTraitNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		var trait: Dynamic = inputs[1].get();
		if (trait == null || !Std.isOfType(trait, LogicTree)) return;

		cast(trait, LogicTree).resume();

		runOutput(0);
	}
}
