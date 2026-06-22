package armory.logicnode;

import iron.math.Vec4;
import kha.Color;
import armory.renderpath.RenderToTexture;

class DrawRectNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		RenderToTexture.ensure2DContext("DrawRectNode");

		final colorVec: Vec4 = inputs[1].get();
		final filled: Bool = inputs[2].get();
		final strength: Float = inputs[3].get();
		final anchorH: Int = inputs[4].get();
		final anchorV: Int = inputs[5].get();
		final x: Float = inputs[6].get();
		final y: Float = inputs[7].get();
		final width: Float = inputs[8].get();
		final height: Float = inputs[9].get();
		final angle: Float = inputs[10].get();

		final drawx = x - 0.5 * width * anchorH;
		final drawy = y - 0.5 * height * anchorV;

		RenderToTexture.g.rotate(angle, x, y);
		RenderToTexture.g.color = Color.fromFloats(colorVec.x, colorVec.y, colorVec.z, colorVec.w);

		if (filled) {
			RenderToTexture.g.fillRect(drawx, drawy, width, height);
		} else {
			RenderToTexture.g.drawRect(drawx, drawy, width, height, strength);
		}

		RenderToTexture.g.rotate(-angle, x, y);
		runOutput(0);
	}
}
