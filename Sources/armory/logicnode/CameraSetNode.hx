package armory.logicnode;

class CameraSetNode extends LogicNode {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run(from:Int) {
		armory.renderpath.Postprocess.camera_uniforms[0] = inputs[1].get();
		armory.renderpath.Postprocess.camera_uniforms[1] = inputs[2].get();
		armory.renderpath.Postprocess.camera_uniforms[2] = inputs[3].get();
		armory.renderpath.Postprocess.camera_uniforms[3] = inputs[4].get();
		armory.renderpath.Postprocess.camera_uniforms[4] = inputs[5].get();
		armory.renderpath.Postprocess.camera_uniforms[5] = inputs[6].get();
		armory.renderpath.Postprocess.camera_uniforms[6] = inputs[7].get();
		armory.renderpath.Postprocess.camera_uniforms[7] = inputs[8].get();
		armory.renderpath.Postprocess.camera_uniforms[8] = inputs[9].get();
		armory.renderpath.Postprocess.camera_uniforms[9] = inputs[10].get();
		armory.renderpath.Postprocess.camera_uniforms[10] = inputs[11].get();

		runOutput(0);
	}
}
