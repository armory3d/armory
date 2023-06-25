package armory.logicnode;

class GetTraitPausedNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		var trait: Dynamic = inputs[0].get();

		if (trait == null) return null;

		return trait.paused;
	}
}
