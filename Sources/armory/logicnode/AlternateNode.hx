package armory.logicnode;

class AlternateNode extends LogicNode {

	var i = 0;

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
	
	if(i >= outputs.length) i = 0;
	runOutput(i);
	++i;

	}
}
