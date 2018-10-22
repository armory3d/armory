package armory.logicnode;

import iron.math.Vec4;
import iron.data.MaterialData;
import iron.object.Object;

class SetMaterialRgbParamNode extends LogicNode {

	static var registered = false;
	static var mat:MaterialData = null;
	static var node = "";
	static var col:Vec4 = null;

	public function new(tree:LogicTree) {
		super(tree);
		if (!registered) {
			registered = true;
			iron.object.Uniforms.externalVec3Links.push(vec3Link);
		}
	}

	override function run(from:Int) {
		mat = inputs[1].get();
		node = inputs[2].get();
		col = inputs[3].get();

		runOutput(0);
	}

	static function vec3Link(object:Object, mat:MaterialData, link:String):iron.math.Vec4 {
		if (link == node) {
			return col;
		}
		return null;
	}
}
