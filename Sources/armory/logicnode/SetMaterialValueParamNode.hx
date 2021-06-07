package armory.logicnode;

import iron.Scene;
import iron.data.MaterialData;
import iron.object.Object;

class SetMaterialValueParamNode extends LogicNode {

	public var property0: Bool; // per object

	static var registered = false;
	static var map = new Map<Object, Map<MaterialData, Map<String, Null<kha.FastFloat>>>>();

	public function new(tree: LogicTree) {
		super(tree);
		if (!registered) {
			registered = true;
			iron.object.Uniforms.externalFloatLinks.push(floatLink);
		}
	}

	override function run(from: Int) {
		var object = inputs[1].get();
		if(object == null) return;

		var mat = inputs[2].get();
		if(mat == null) return;

		if(! property0){
			object = Scene.active.root;
		}

		var matMap = map.get(object);
		if (matMap == null) {
			matMap = new Map();
			map.set(object, matMap);
		}

		var entry = matMap.get(mat);
		if (entry == null) {
			entry = new Map();
			matMap.set(mat, entry);
		}
		
		entry.set(inputs[3].get(), inputs[4].get()); // Node name, value
		runOutput(0);
	}

	static function floatLink(object: Object, mat: MaterialData, link: String): Null<kha.FastFloat> {
		if(object == null) return null;
		if (mat == null) return null;

		if(! map.exists(object)){
			object = Scene.active.root;
		}

		var material = map.get(object);
		if (material == null) return null;

		var entry = material.get(mat);
		if (entry == null) return null;

		return entry.get(link);
	}
}
