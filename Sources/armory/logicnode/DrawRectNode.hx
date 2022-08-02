package armory.logicnode;

import kha.Color;

class DrawRectNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		OnRender2DNode.ensure2DContext("DrawRectNode");

		final colorVec = inputs[1].get();
		OnRender2DNode.g.color = Color.fromFloats(colorVec.x, colorVec.y, colorVec.z, colorVec.w);

		if (inputs[2].get()) {
			OnRender2DNode.g.fillRect(inputs[4].get(), inputs[5].get(), inputs[6].get(), inputs[7].get());
		} else {
			OnRender2DNode.g.drawRect(inputs[4].get(), inputs[5].get(), inputs[6].get(), inputs[7].get(), inputs[3].get());
		}

		runOutput(0);
	}
}
