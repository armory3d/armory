package armory.logicnode;

import iron.math.Vec4;

class SeparateColorHSVNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		var vector: Vec4 = inputs[0].get();
		if (vector == null) return 0.0;
		
		var r = vector.x;
		var g = vector.y;
		var b = vector.z;
		var a = vector.w;		
		

		var max = Math.max(Math.max(r, g), b);
		var min = Math.min(Math.min(r, g), b);
		var h: Float = max;
		var s: Float = max;
		var	v: Float = max;

		var d = max - min;
		s = max == 0 ? 0 : d / max;

		if(max == min){
			h = 0; // achromatic
		}else{
			if(max == r) h = (g - b) / d + (g < b ? 6 : 0);
				else if(max == g) h = (b - r) / d + 2;
					else h = (r - g) / d + 4;
			h /= 6;
		}

		return switch (from) {
			case 0: h;
			case 1: s;
			case 2: v;
			case 3: a;
			default: throw "Unreachable";
		}
	}
}
