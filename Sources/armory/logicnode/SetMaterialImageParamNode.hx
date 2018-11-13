package armory.logicnode;

import iron.math.Vec4;
import iron.data.MaterialData;
import iron.object.Object;

class SetMaterialImageParamNode extends LogicNode {

	static var registered = false;
	static var mat:MaterialData = null;
	static var map = new Map<String, kha.Image>();

	public function new(tree:LogicTree) {
		super(tree);
		if (!registered) {
			registered = true;
			iron.object.Uniforms.externalTextureLinks.push(textureLink);
		}
	}

	override function run(from:Int) {
		mat = inputs[1].get();
		if (mat == null) return;
		
		iron.data.Data.getImage(inputs[3].get(), function(image:kha.Image) {
			map.set(inputs[2].get(), image);
		});

		runOutput(0);
	}

	static function textureLink(object:Object, mat:MaterialData, link:String):kha.Image {
		return map.get(link);
	}
}
