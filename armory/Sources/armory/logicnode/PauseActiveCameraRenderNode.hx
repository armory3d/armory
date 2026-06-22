package armory.logicnode;

import iron.RenderPath;

class PauseActiveCameraRenderNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		final isPaused: Bool = inputs[1].get();

		RenderPath.active.paused = isPaused;
		runOutput(0);
	}
}