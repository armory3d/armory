package armory.logicnode;

import kha.Image;
import kha.Color;
import armory.renderpath.RenderToTexture;

class DrawImageNode extends LogicNode {
	var img: Image;
	var lastImgName = "";

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		RenderToTexture.ensure2DContext("DrawImageNode");

		final imgName = inputs[1].get();
		if (imgName != lastImgName) {
			// Load new image
			lastImgName = imgName;
			iron.data.Data.getImage(imgName, (image: Image) -> {
				img = image;
			});
		}

		if (img == null) {
			runOutput(0);
			return;
		}

		final colorVec = inputs[2].get();
		RenderToTexture.g.color = Color.fromFloats(colorVec.x, colorVec.y, colorVec.z, colorVec.w);

		RenderToTexture.g.drawScaledImage(img, inputs[3].get(), inputs[4].get(), inputs[5].get(), inputs[6].get());

		runOutput(0);
	}
}
