package armory.logicnode;

import iron.system.Tween;
import iron.math.Vec4;

class VectorMixNode extends LogicNode {

	public var property0:String; // Type
	public var property1:String; // Ease
	public var property2:String; // Clamp

	var v = new Vec4();

	var ease:Float->Float = null;

	public function new(tree:LogicTree) {
		super(tree);
	}

	function init() {
		switch (property0) {
			case "Linear":
				ease = Tween.easeLinear;
			case "Sine":
				ease = property1 == "In" ? Tween.easeSineIn : (property1 == "Out" ? Tween.easeSineOut : Tween.easeSineInOut);
			case "Quad":
				ease = property1 == "In" ? Tween.easeQuadIn : (property1 == "Out" ? Tween.easeQuadOut : Tween.easeQuadInOut);
			case "Cubic":
				ease = property1 == "In" ? Tween.easeCubicIn : (property1 == "Out" ? Tween.easeCubicOut : Tween.easeCubicInOut);
			case "Quart":
				ease = property1 == "In" ? Tween.easeQuartIn : (property1 == "Out" ? Tween.easeQuartOut : Tween.easeQuartInOut);
			case "Quint":
				ease = property1 == "In" ? Tween.easeQuintIn : (property1 == "Out" ? Tween.easeQuintOut : Tween.easeQuintInOut);
			case "Expo":
				ease = property1 == "In" ? Tween.easeExpoIn : (property1 == "Out" ? Tween.easeExpoOut : Tween.easeExpoInOut);
			case "Circ":
				ease = property1 == "In" ? Tween.easeCircIn : (property1 == "Out" ? Tween.easeCircOut : Tween.easeCircInOut);
			case "Back":
				ease = property1 == "In" ? Tween.easeBackIn : (property1 == "Out" ? Tween.easeBackOut : Tween.easeBackInOut);
			default:
				ease = Tween.easeLinear;
		}
	}

	override function get(from:Int):Dynamic {
		if (ease == null) init();
		var k:Float = inputs[0].get();
		var v1:Vec4 = inputs[1].get();
		var v2:Vec4 = inputs[2].get();
		var f = ease(k);
		v.x = v1.x + (v2.x - v1.x) * f;
		v.y = v1.y + (v2.y - v1.y) * f;
		v.z = v1.z + (v2.z - v1.z) * f;
		if (property1 == "true") {
			v.x = v.x < 0.0 ? 0.0 : (v.x > 1.0 ? 1.0 : v.x);
			v.y = v.y < 0.0 ? 0.0 : (v.y > 1.0 ? 1.0 : v.y);
			v.z = v.z < 0.0 ? 0.0 : (v.z > 1.0 ? 1.0 : v.z);
		}
		return v;
	}
}
