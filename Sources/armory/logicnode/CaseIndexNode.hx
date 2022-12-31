package armory.logicnode;

import iron.math.Vec4;

class CaseIndexNode extends LogicNode {

	var value: Dynamic = null;

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Dynamic): Int {

	var value = inputs[0].get();
	
	for(index in 0...inputs.length-1)
		if(Std.isOfType(value, Vec4) ? value.equals(inputs[index+1].get()) : value == inputs[index+1].get())
			return index;
			
	return null;

	}
}
