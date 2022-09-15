package armory.logicnode;

import kha.Color;
import armory.renderpath.RenderToTexture;

class DrawRectNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		RenderToTexture.ensure2DContext("DrawRectNode");

		final colorVec = inputs[1].get();
		RenderToTexture.g.color = Color.fromFloats(colorVec.x, colorVec.y, colorVec.z, colorVec.w);

		if (inputs[2].get()) {
			RenderToTexture.g.fillRect(inputs[4].get(), inputs[5].get(), inputs[6].get(), inputs[7].get());
		} else {
			RenderToTexture.g.drawRect(inputs[4].get(), inputs[5].get(), inputs[6].get(), inputs[7].get(), inputs[3].get());
		}

		runOutput(0);
	}
}
