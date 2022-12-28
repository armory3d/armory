package armory.logicnode;

class CaseIndexNode extends LogicNode {

	var value: Dynamic = null;

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Dynamic): Int {

	var value = inputs[0].get();
	
	for(index in 0...inputs.length-1)
		if(value == inputs[index+1].get())
			return index;
			
	return null;

	}
}
