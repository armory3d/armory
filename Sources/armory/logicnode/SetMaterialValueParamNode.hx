package armory.logicnode;

import iron.math.Vec4;
import iron.data.MaterialData;
import iron.object.Object;

class SetMaterialValueParamNode extends LogicNode {

	static var registered = false;
	static var mat:MaterialData = null;
	static var node = "";
	static var value:Null<kha.FastFloat> = null;

	public function new(tree:LogicTree) {
		super(tree);
		if (!registered) {
			registered = true;
			iron.object.Uniforms.externalFloatLinks.push(floatLink);
		}
	}

	override function run(from:Int) {
		mat = inputs[1].get();
		node = inputs[2].get();
		value = inputs[3].get();

		runOutput(0);
	}

	static function floatLink(object:Object, mat:MaterialData, link:String):Null<kha.FastFloat> {
		if (link == node) {
			return value;
		}
		return null;
	}
}
