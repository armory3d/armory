package armory.logicnode;

import iron.math.Vec4;
import kha.Image;
import kha.Color;
import armory.renderpath.RenderToTexture;

class DrawSubImageNode extends LogicNode {
	var img: Image;
	var lastImgName = "";

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		RenderToTexture.ensure2DContext("DrawImageNode");

		final imgName: String = inputs[1].get();
		final colorVec: Vec4 = inputs[2].get();
		final anchorH: Int = inputs[3].get();
		final anchorV: Int = inputs[4].get();
		final x: Float = inputs[5].get();
		final y: Float = inputs[6].get();
		final width: Float = inputs[7].get();
		final height: Float = inputs[8].get();
		final sx: Float = inputs[9].get();
		final sy: Float = inputs[10].get();
		final swidth: Float = inputs[11].get();
		final sheight: Float = inputs[12].get();
		final angle: Float = inputs[13].get();

		final drawx = x - 0.5 * width * anchorH;
		final drawy = y - 0.5 * height * anchorV;

		RenderToTexture.g.rotate(angle, x, y);

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

		RenderToTexture.g.color = Color.fromFloats(colorVec.x, colorVec.y, colorVec.z, colorVec.w);
		RenderToTexture.g.drawScaledSubImage(img, sx, sy, swidth, sheight, drawx, drawy, width, height);
		RenderToTexture.g.rotate(-angle, x, y);

		runOutput(0);
	}
}
