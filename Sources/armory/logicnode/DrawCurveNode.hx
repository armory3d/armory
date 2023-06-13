package armory.logicnode;

import kha.Color;
import armory.renderpath.RenderToTexture;

#if arm_ui
using zui.GraphicsExtension;
#end

class DrawCurveNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		#if arm_ui
		RenderToTexture.ensure2DContext("DrawCurveNode");

		final colorVec = inputs[1].get();
		RenderToTexture.g.color = Color.fromFloats(colorVec.x, colorVec.y, colorVec.z, colorVec.w);

		RenderToTexture.g.drawCubicBezier(
			[inputs[4].get(), inputs[6].get(), inputs[8].get(), inputs[10].get()],
			[inputs[5].get(), inputs[7].get(), inputs[9].get(), inputs[11].get()],
			inputs[3].get(), inputs[2].get()
		);
		#end

		runOutput(0);
	}
}
