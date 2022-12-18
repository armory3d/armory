package armory.logicnode;

import iron.Scene;

class PauseActiveCameraRenderNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		final isPaused: Bool = inputs[1].get();

		Scene.active.pauseActiveCameraRender = isPaused;
		runOutput(0);
	}
}