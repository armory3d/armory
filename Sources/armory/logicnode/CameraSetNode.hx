package armory.logicnode;

class CameraSetNode extends LogicNode {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run(from:Int) {
		armory.renderpath.Postprocess.camera_uniforms[0] = inputs[1].get();//Camera: F-Number
		armory.renderpath.Postprocess.camera_uniforms[1] = inputs[2].get();//Camera: Shutter time
		armory.renderpath.Postprocess.camera_uniforms[2] = inputs[3].get();//Camera: ISO
		armory.renderpath.Postprocess.camera_uniforms[3] = inputs[4].get();//Camera: Exposure Compensation
		armory.renderpath.Postprocess.camera_uniforms[4] = inputs[5].get();//Fisheye Distortion
		armory.renderpath.Postprocess.camera_uniforms[5] = inputs[6].get();//DoF AutoFocus §§ If true, it ignores the DoF Distance setting
		armory.renderpath.Postprocess.camera_uniforms[6] = inputs[7].get();//DoF Distance
		armory.renderpath.Postprocess.camera_uniforms[7] = inputs[8].get();//DoF Focal Length mm
		armory.renderpath.Postprocess.camera_uniforms[8] = inputs[9].get();//DoF F-Stop
		armory.renderpath.Postprocess.camera_uniforms[9] = inputs[10].get();//Tonemapping Method
		armory.renderpath.Postprocess.camera_uniforms[10] = inputs[11].get();//Distort
		armory.renderpath.Postprocess.camera_uniforms[11] = inputs[12].get();//Film Grain

		runOutput(0);
	}
}
