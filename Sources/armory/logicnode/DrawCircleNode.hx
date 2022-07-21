package armory.logicnode;

import kha.Color;

using kha.graphics2.GraphicsExtension;

class DrawCircleNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		OnRender2DNode.ensure2DContext("DrawCircleNode");

		final colorVec = inputs[1].get();
		OnRender2DNode.g.color = Color.fromFloats(colorVec.x, colorVec.y, colorVec.z, colorVec.w);

		final segments = inputs[4].get();
		final cx = inputs[5].get();
		final cy = inputs[6].get();
		final radius = inputs[7].get();

		if (inputs[2].get()) {
			OnRender2DNode.g.fillCircle(cx, cy, radius, segments);
		}
		else {
			OnRender2DNode.g.drawCircle(cx, cy, radius, inputs[3].get(), segments);
		}

		runOutput(0);
	}
}
