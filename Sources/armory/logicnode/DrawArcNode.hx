package armory.logicnode;

import kha.Color;
import armory.renderpath.RenderToTexture;

using zui.GraphicsExtension;

class DrawArcNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		RenderToTexture.ensure2DContext("DrawArcNode");

		final colorVec = inputs[1].get();
		RenderToTexture.g.color = Color.fromFloats(colorVec.x, colorVec.y, colorVec.z, colorVec.w);

		final segments = inputs[4].get();
		final cx = inputs[5].get();
		final cy = inputs[6].get();
		final radius = inputs[7].get();
		final sAngle = inputs[8].get();
		final eAngle = inputs[9].get();
		final ccw = inputs[10].get();

		if (inputs[2].get()) {
			RenderToTexture.g.fillArc(cx, cy, radius, sAngle, eAngle, ccw, segments);
		} else {
			RenderToTexture.g.drawArc(cx, cy, radius, sAngle, eAngle, inputs[3].get(), ccw, segments);
		}

		runOutput(0);
	}
}
