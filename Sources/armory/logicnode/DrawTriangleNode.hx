package armory.logicnode;

import kha.Color;
import armory.renderpath.RenderToTexture;

class DrawTriangleNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		RenderToTexture.ensure2DContext("DrawTriangleNode");

		final colorVec = inputs[1].get();
		RenderToTexture.g.color = Color.fromFloats(colorVec.x, colorVec.y, colorVec.z, colorVec.w);

		final strength = inputs[3].get();
		final x1 = inputs[4].get();
		final y1 = inputs[5].get();
		final x2 = inputs[6].get();
		final y2 = inputs[7].get();
		final x3 = inputs[8].get();
		final y3 = inputs[9].get();

		if (inputs[2].get()) {
			RenderToTexture.g.fillTriangle(x1, y1, x2, y2, x3, y3);
		} else {
			RenderToTexture.g.drawLine(x1, y1, x2, y2, strength);
			RenderToTexture.g.drawLine(x2, y2, x3, y3, strength);
			RenderToTexture.g.drawLine(x3, y3, x1, y1, strength);
		}

		runOutput(0);
	}
}
