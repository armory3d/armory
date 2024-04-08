package armory.logicnode;

class SelectOutputNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		//Get index to run
		var outIndex: Int = inputs[1].get();
		// Check if output index found
		if(outIndex > (outputs.length - 2) || outIndex < 0)
		{
			runOutput(0);
			return;
		}
		runOutput(outIndex + 1);
	}
}
