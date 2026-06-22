package armory.logicnode;

import kha.Color;
import armory.renderpath.RenderToTexture;
import armory.trait.internal.UniformsManager;

class DrawToMaterialImageNode extends LogicNode {

	var img: kha.Image = null;

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		var object = inputs[1].get();
		var mat = inputs[2].get();
		var node = inputs[3].get();
		
		img = UniformsManager.textureLink(object, mat, inputs[3].get());

		assert(Error, img != null, 'Image $node does not exist or is empty');

		assert(Error, img.depth != null, 'Image is not a render target. Use Create Render Target Node to create an image render target');

		RenderToTexture.ensureEmptyRenderTarget("DrawToMaterialImageNode");
		img.g2.begin(inputs[4].get(), Color.Transparent);
		RenderToTexture.g = img.g2;
		runOutput(0);
		RenderToTexture.g = null;
		img.g2.end();
	}

	override function get(from: Int): Dynamic {
		if(img == null) return null;

		switch(from){
			case 1: return img.width;
			case 2: return img.height;
			default: return null;
		}
	}
}
