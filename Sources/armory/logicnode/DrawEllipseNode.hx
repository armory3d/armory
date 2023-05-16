package armory.logicnode;

import iron.math.Vec4;
import kha.Color;
import armory.renderpath.RenderToTexture;

using zui.GraphicsExtension;

class DrawEllipseNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		RenderToTexture.ensure2DContext("DrawEllipseNode");

		final colorVec: Vec4 = inputs[1].get();
		RenderToTexture.g.color = Color.fromFloats(colorVec.x, colorVec.y, colorVec.z, colorVec.w);

		final filled: Bool = inputs[2].get();
		final strength: Float = inputs[3].get();
		final segments: Int = inputs[4].get();
		final cx: Float = inputs[5].get();
		final cy: Float = inputs[6].get();
		final width: Float = inputs[7].get();
		final height: Float = inputs[8].get();
		final angle: Float = inputs[9].get();
		final scale = height / width;
		final scaleInv = width / height;

		RenderToTexture.g.scale(1.0, scale);
		RenderToTexture.g.rotate(angle, cx, cy);

		if (filled) {
			RenderToTexture.g.fillCircle(cx, cy * scaleInv, 0.5 * width, segments);
		}
		else {
			RenderToTexture.g.drawCircle(cx, cy * scaleInv, 0.5 * width, strength, segments);
		}

		RenderToTexture.g.rotate(-angle, cx, cy);
		RenderToTexture.g.scale(1.0, scaleInv);

		runOutput(0);
	}
}
