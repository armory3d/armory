package armory.logicnode;

import iron.math.Vec4;
import iron.data.MaterialData;
import iron.object.Object;

class SetMaterialRgbParamNode extends LogicNode {

	static var registered = false;
	static var map = new Map<MaterialData, Map<String, Vec4>>();

	public function new(tree: LogicTree) {
		super(tree);
		if (!registered) {
			registered = true;
			iron.object.Uniforms.externalVec3Links.push(vec3Link);
		}
	}

	override function run(from: Int) {
		var mat = inputs[1].get();
		if (mat == null) return;
		var entry = map.get(mat);
		if (entry == null) {
			entry = new Map();
			map.set(mat, entry);
		}
		entry.set(inputs[2].get(), inputs[3].get()); // Node name, value
		runOutput(0);
	}

	static function vec3Link(object: Object, mat: MaterialData, link: String): iron.math.Vec4 {
		if (mat == null) return null;
		var entry = map.get(mat);
		if (entry == null) return null;
		return entry.get(link);
	}
}
