package armory.logicnode;

class WaitForNode extends LogicNode {

	var froms: Array<Int> = [];

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {

		if(!froms.contains(from)) froms.push(from);
		if(inputs.length == froms.length){ runOutput(0); froms = []; }

	}

}
