package armory.logicnode;

import kha.graphics4.TextureFilter;

class ResolutionSetNode extends LogicNode {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run(from:Int) {

		var size: Int = inputs[1].get();
		var filter: Int = inputs[2].get();

	#if rp_resolution_filter 
		if (filter == 0)
			iron.object.Uniforms.defaultFilter = TextureFilter.LinearFilter;
		else
			iron.object.Uniforms.defaultFilter = TextureFilter.PointFilter;

		armory.renderpath.Postprocess.resolution_uniforms[0] = size;
		armory.renderpath.Postprocess.resolution_uniforms[1] = filter;

		var npath = armory.renderpath.RenderPathCreator.get();
		var world = iron.Scene.active.raw.world_ref;
		npath.loadShader("shader_datas/World_" + world + "/World_" + world);
		iron.RenderPath.setActive(npath);
    #end

		runOutput(0);
	}
}
