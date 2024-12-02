package armory.logicnode;

import iron.math.Vec4;
import iron.math.Ray;
import iron.object.Object;

class RaycastRayNode extends LogicNode {

	var o: Object;
	var v: Vec4;
	var dist: Float;

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {

		o = null;
		v = null;
		dist = Math.POSITIVE_INFINITY;

		var objects: Array<Object> = inputs[1].get();

		var ray: Ray = new Ray(inputs[2].get(), inputs[3].get());

		for (obj in objects){
			var t = obj.transform;
			var c = new Vec4(t.worldx(), t.worldy(), t.worldz());
			var s = new Vec4(t.dim.x, t.dim.y, t.dim.z);
			var intersect = ray.intersectBox(c, s);
			if (intersect != null){
				var d = Vec4.distance(intersect, inputs[2].get());
				if (d < dist){
					o = obj;
					v = intersect;
					dist = d;
				} 
			}		
		}

		if (o == null) runOutput(2); else runOutput(1);
		
		runOutput(0);
	}
	
	override function get(from: Int): Dynamic {
		return 
		switch (from) {
			case 3: o;
			case 4: v;
			case 5: dist; 
			default: null;
		}

	}
}