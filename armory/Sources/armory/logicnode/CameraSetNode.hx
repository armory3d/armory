package armory.logicnode;

class CameraSetNode extends LogicNode {

	public var property0: String;

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run(from:Int) {

		switch (property0) {
			case 'F-stop':
				armory.renderpath.Postprocess.camera_uniforms[0] = inputs[1].get();//Camera: F-Number
			case 'Shutter Time':	
				armory.renderpath.Postprocess.camera_uniforms[1] = inputs[1].get();//Camera: Shutter time
			case 'ISO':
				armory.renderpath.Postprocess.camera_uniforms[2] = inputs[1].get();//Camera: ISO
			case 'Exposure Compensation':
				armory.renderpath.Postprocess.camera_uniforms[3] = inputs[1].get();//Camera: Exposure Compensation
			case 'Fisheye Distortion':
				armory.renderpath.Postprocess.camera_uniforms[4] = inputs[1].get();//Fisheye Distortion
			case 'Auto Focus':
				armory.renderpath.Postprocess.camera_uniforms[5] = inputs[1].get();//DoF AutoFocus §§ If true, it ignores the DoF Distance setting
			case 'DoF Distance':
				armory.renderpath.Postprocess.camera_uniforms[6] = inputs[1].get();//DoF Distance
			case 'DoF Length':
				armory.renderpath.Postprocess.camera_uniforms[7] = inputs[1].get();//DoF Focal Length mm
			case 'DoF F-Stop':
				armory.renderpath.Postprocess.camera_uniforms[8] = inputs[1].get();//DoF F-Stop
			case 'Tonemapping':
				armory.renderpath.Postprocess.camera_uniforms[9] = inputs[1].get();//Tonemapping Method
			case 'Distort':
				armory.renderpath.Postprocess.camera_uniforms[10] = inputs[1].get();//Distort
			case 'Film Grain':
				armory.renderpath.Postprocess.camera_uniforms[11] = inputs[1].get();//Film Grain
			case 'Sharpen':
				armory.renderpath.Postprocess.camera_uniforms[12] = inputs[1].get();//Sharpen
			case 'Vignette':
				armory.renderpath.Postprocess.camera_uniforms[13] = inputs[1].get();//Vignette
			case 'Exposure':
				armory.renderpath.Postprocess.exposure[0] = inputs[1].get();//Exposure
			default: 
				null;
			}

		runOutput(0);
	}
}
