package armory.logicnode;

import kha.Color;

class DrawLineNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		OnRender2DNode.ensure2DContext("DrawLineNode");

		final colorVec = inputs[1].get();
		OnRender2DNode.g.color = Color.fromFloats(colorVec.x, colorVec.y, colorVec.z, colorVec.w);

		OnRender2DNode.g.drawLine(inputs[3].get(), inputs[4].get(), inputs[5].get(), inputs[6].get(), inputs[2].get());

		runOutput(0);
	}
}
