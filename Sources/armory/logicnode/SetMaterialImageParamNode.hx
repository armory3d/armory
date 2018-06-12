package armory.logicnode;

import iron.math.Vec4;
import iron.data.MaterialData;
import iron.object.Object;

class SetMaterialImageParamNode extends LogicNode {

	static var registered = false;
	static var mat:MaterialData = null;
	static var node = "";
	static var image:kha.Image = null;

	public function new(tree:LogicTree) {
		super(tree);
		if (!registered) {
			registered = true;
			iron.object.Uniforms.externalTextureLinks.push(textureLink);
		}
	}

	override function run() {
		mat = inputs[1].get();
		node = inputs[2].get();
		var name = inputs[3].get();
		iron.data.Data.getImage(name, function(img:kha.Image) {
			image = img;
		});

		super.run();
	}

	static function textureLink(object:Object, mat:MaterialData, link:String):kha.Image {
		if (link == node) {
			return image;
		}
		return null;
	}
}
