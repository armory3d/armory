package armory.logicnode;

import iron.math.Vec4;
import iron.data.MaterialData;
import iron.object.Object;

class SetMaterialImageParamNode extends LogicNode {

	static var registered = false;
	static var map = new Map<MaterialData, Map<String, kha.Image>>();

	public function new(tree:LogicTree) {
		super(tree);
		if (!registered) {
			registered = true;
			iron.object.Uniforms.externalTextureLinks.push(textureLink);
		}
	}

	override function run(from:Int) {
		var mat = inputs[1].get();
		if (mat == null) return;
		var entry = map.get(mat);
		if (entry == null) {
			entry = new Map();
			map.set(mat, entry);
		}

		iron.data.Data.getImage(inputs[3].get(), function(image:kha.Image) {
			entry.set(inputs[2].get(), image); // Node name, value
		});
		runOutput(0);
	}

	static function textureLink(object:Object, mat:MaterialData, link:String):kha.Image {
		if (mat == null) return null;
		var entry = map.get(mat);
		if (entry == null) return null;
		return entry.get(link);
	}
}
