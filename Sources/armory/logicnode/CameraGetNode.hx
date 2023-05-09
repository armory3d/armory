package armory.logicnode;

class CameraGetNode extends LogicNode {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function get(from:Int):Dynamic {
		return switch (from) {
			case 0: armory.renderpath.Postprocess.camera_uniforms[0];//Camera: F-Number
			case 1: armory.renderpath.Postprocess.camera_uniforms[1];//Camera: Shutter time
			case 2: armory.renderpath.Postprocess.camera_uniforms[2];//Camera: ISO
			case 3: armory.renderpath.Postprocess.camera_uniforms[3];//Camera: Exposure Compensation
			case 4: armory.renderpath.Postprocess.camera_uniforms[4];//Fisheye Distortion
			case 5: armory.renderpath.Postprocess.camera_uniforms[5];//DoF AutoFocus §§ If true, it ignores the DoF Distance setting
			case 6: armory.renderpath.Postprocess.camera_uniforms[6];//DoF Distance
			case 7: armory.renderpath.Postprocess.camera_uniforms[7];//DoF Focal Length mm
			case 8: armory.renderpath.Postprocess.camera_uniforms[8];//DoF F-Stop
			case 9: armory.renderpath.Postprocess.camera_uniforms[9];//Tonemapping Method
			case 10: armory.renderpath.Postprocess.camera_uniforms[10];//Distort
			case 11: armory.renderpath.Postprocess.camera_uniforms[11];//Film Grain
			default: 0.0;
		}
	}
}
