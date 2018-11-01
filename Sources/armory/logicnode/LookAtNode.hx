package armory.logicnode;

import iron.math.Vec4;
import iron.math.Quat;

class LookAtNode extends LogicNode {

	var v1 = new Vec4();
	var v2 = new Vec4();
	var q = new Quat();

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function get(from:Int):Dynamic {
		var vfrom:Vec4 = inputs[0].get();
		var vto:Vec4 = inputs[1].get();

		if (vfrom == null || vto == null) return null;

		v1.set(0, 0, 1);
		v2.setFrom(vto).sub(vfrom).normalize();

		q.fromTo(v1, v2);
		return q.getEuler();
	}
}
