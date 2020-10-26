package armory.logicnode;

class SnapshotNode extends LogicNode {

	var snapshot: Dynamic = null;

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		var value: Dynamic = inputs[1].get();

		snapshot = value;

		runOutput(0);
	}
	override function get(from: Dynamic) {
		return snapshot;
	}
}
