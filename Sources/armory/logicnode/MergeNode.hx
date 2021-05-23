package armory.logicnode;

class MergeNode extends LogicNode {

	/** Execution mode. **/
	public var property0: String;

	var lastInputIndex = -1;

	public function new(tree: LogicTree) {
		super(tree);
		tree.notifyOnLateUpdate(lateUpdate);
	}

	override function run(from: Int) {
		// Check if there already were executions on the same frame
		if (lastInputIndex != -1 && property0 == "once_per_frame") {
			return;
		}

		lastInputIndex = from;
		runOutput(0);
	}

	override function get(from: Int): Dynamic {
		return lastInputIndex;
	}

	function lateUpdate() {
		lastInputIndex = -1;
	}
}
