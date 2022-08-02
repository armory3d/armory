package armory.logicnode;

import kha.Image;
import kha.Color;

class DrawImageNode extends LogicNode {
	var img: Image;
	var lastImgName = "";

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		OnRender2DNode.ensure2DContext("DrawImageNode");

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
		OnRender2DNode.g.color = Color.fromFloats(colorVec.x, colorVec.y, colorVec.z, colorVec.w);

		OnRender2DNode.g.drawScaledImage(img, inputs[3].get(), inputs[4].get(), inputs[5].get(), inputs[6].get());

		runOutput(0);
	}
}
