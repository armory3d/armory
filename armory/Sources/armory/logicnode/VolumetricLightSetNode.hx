package armory.logicnode;

class VolumetricLightSetNode extends LogicNode {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run(from:Int) {
        armory.renderpath.Postprocess.volumetric_light_uniforms[0][0] = inputs[1].get().x;
        armory.renderpath.Postprocess.volumetric_light_uniforms[0][1] = inputs[1].get().y;
        armory.renderpath.Postprocess.volumetric_light_uniforms[0][2] = inputs[1].get().z;
        armory.renderpath.Postprocess.volumetric_light_uniforms[1][0] = inputs[2].get();
        armory.renderpath.Postprocess.volumetric_light_uniforms[2][0] = inputs[3].get();

		runOutput(0);
	}
}
