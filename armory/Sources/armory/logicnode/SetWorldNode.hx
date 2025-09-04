package armory.logicnode;

import iron.data.SceneFormat;

class SetWorldNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		var world: String = inputs[1].get();

		if (world != null){
			iron.Scene.active.raw.world_ref = world;
			var npath = armory.renderpath.RenderPathCreator.get();
			npath.loadShader("shader_datas/World_" + world + "/World_" + world);
			iron.RenderPath.setActive(npath);
		}

		runOutput(0);
	}
}
