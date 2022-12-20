package armory.logicnode;

import armory.renderpath.RenderToTexture;

class RotateRenderTargetNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		RenderToTexture.ensure2DContext("RotateRenderTargetNode");

		final angle: Float = inputs[1].get();
		final centerX: Float = inputs[2].get();
		final centerY: Float = inputs[3].get();
		final revert: Bool = inputs[4].get();

		//Rotate render target
		RenderToTexture.g.rotate(angle, centerX, centerY);

		//Execute all outputs
		runOutput(0);

		//Revert rotation if enabled
		if(revert) RenderToTexture.g.rotate(-angle, centerX, centerY);
	}
}
