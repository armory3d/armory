package armory.logicnode;

import armory.renderpath.RenderToTexture;

class OnRender2DNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
		tree.notifyOnRender2D(onRender2D);
	}

	function onRender2D(g: kha.graphics2.Graphics) {
		RenderToTexture.ensureEmptyRenderTarget("OnRender2DNode");
		RenderToTexture.g = g;
		runOutput(0);
		RenderToTexture.g = null;
	}
}
