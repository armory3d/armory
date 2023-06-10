package armory.logicnode;

import kha.Color;
import armory.renderpath.RenderToTexture;

class DrawLineNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		RenderToTexture.ensure2DContext("DrawLineNode");

		final colorVec = inputs[1].get();
		RenderToTexture.g.color = Color.fromFloats(colorVec.x, colorVec.y, colorVec.z, colorVec.w);

		RenderToTexture.g.drawLine(inputs[3].get(), inputs[4].get(), inputs[5].get(), inputs[6].get(), inputs[2].get());

		runOutput(0);
	}
}
