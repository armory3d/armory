package armory.logicnode;

class VolumetricFogGetNode extends LogicNode {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function get(from:Int):Dynamic {
		return switch (from) {
			case 0: armory.renderpath.Postprocess.volumetric_fog_uniforms[0];
			case 1: armory.renderpath.Postprocess.volumetric_fog_uniforms[1][0];
			case 2: armory.renderpath.Postprocess.volumetric_fog_uniforms[2][0];
			default: 0.0;
		}
	}
}
