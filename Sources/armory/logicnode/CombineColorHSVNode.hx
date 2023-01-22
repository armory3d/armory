package armory.logicnode;

import iron.math.Vec4;

class CombineColorHSVNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		var h = inputs[0].get();
		var s = inputs[1].get();
		var v = inputs[2].get();
		var a = inputs[3].get();
				
		var r = 0.0; var g = 0.0; var b = 0.0;

		var i = Math.floor(h * 6);
		var f = h * 6 - i;
		var p = v * (1 - s);
		var q = v * (1 - f * s);
		var t = v * (1 - (1 - f) * s);

		switch (i % 6) {
			case 0: { r = v; g = t; b = p; }
			case 1: { r = q; g = v; b = p; }
			case 2: { r = p; g = v; b = t; }
			case 3: { r = p; g = q; b = v; }
			case 4: { r = t; g = p; b = v; }
			case 5: { r = v; g = p; b = q; }
		}

		return new Vec4(r, g, b, a);
	}
}
