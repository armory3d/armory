package armory.logicnode;

import iron.math.Vec4;
import iron.data.MaterialData;
import iron.object.Object;

class SetMaterialValueParamNode extends LogicNode {

	static var registered = false;
	static var mat:MaterialData = null;
	static var map = new Map<String, Null<kha.FastFloat>>();

	public function new(tree:LogicTree) {
		super(tree);
		if (!registered) {
			registered = true;
			iron.object.Uniforms.externalFloatLinks.push(floatLink);
		}
	}

	override function run(from:Int) {
		mat = inputs[1].get();
		if (mat == null) return;
		map.set(inputs[2].get(), inputs[3].get()); // Node name, value
		runOutput(0);
	}

	static function floatLink(object:Object, mat:MaterialData, link:String):Null<kha.FastFloat> {
		return map.get(link);
	}
}
