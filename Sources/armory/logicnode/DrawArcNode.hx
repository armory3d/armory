package armory.logicnode;

import kha.Color;

using kha.graphics2.GraphicsExtension;

class DrawArcNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		OnRender2DNode.ensure2DContext("DrawArcNode");

		final colorVec = inputs[1].get();
		OnRender2DNode.g.color = Color.fromFloats(colorVec.x, colorVec.y, colorVec.z, colorVec.w);

		final segments = inputs[4].get();
		final cx = inputs[5].get();
		final cy = inputs[6].get();
		final radius = inputs[7].get();
		final sAngle = inputs[8].get();
		final eAngle = inputs[9].get();
		final ccw = inputs[10].get();

		if (inputs[2].get()) {
			OnRender2DNode.g.fillArc(cx, cy, radius, sAngle, eAngle, ccw, segments);
		} else {
			OnRender2DNode.g.drawArc(cx, cy, radius, sAngle, eAngle, inputs[3].get(), ccw, segments);
		}

		runOutput(0);
	}
}
