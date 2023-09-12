package armory.logicnode;

import kha.Color;
import armory.renderpath.RenderToTexture;

#if arm_ui
using zui.GraphicsExtension;
#end

class DrawCircleNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		#if arm_ui
		RenderToTexture.ensure2DContext("DrawCircleNode");

		final colorVec = inputs[1].get();
		RenderToTexture.g.color = Color.fromFloats(colorVec.x, colorVec.y, colorVec.z, colorVec.w);

		final segments = inputs[4].get();
		final cx = inputs[5].get();
		final cy = inputs[6].get();
		final radius = inputs[7].get();

		if (inputs[2].get()) {
			RenderToTexture.g.fillCircle(cx, cy, radius, segments);
		}
		else {
			RenderToTexture.g.drawCircle(cx, cy, radius, inputs[3].get(), segments);
		}
		#end

		runOutput(0);
	}
}
