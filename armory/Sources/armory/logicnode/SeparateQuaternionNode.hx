package armory.logicnode;

import iron.math.Quat;
import kha.FastFloat;

class SeparateQuaternionNode extends LogicNode {
	var q:Quat = null;

	public function new(tree:LogicTree) { super(tree); }
    
	override function get(from:Int):Dynamic{
		q = inputs[0].get();
		if (from==0)
			return q.x;
		else if (from==1)
			return q.y;
		else if (from==2)
			return q.z;
		else
			return q.w;

	}
}
