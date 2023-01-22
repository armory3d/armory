package armory.logicnode;

class CameraGetNode extends LogicNode {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function get(from:Int):Dynamic {
		return switch (from) {
			case 0: armory.renderpath.Postprocess.camera_uniforms[0];
			case 1: armory.renderpath.Postprocess.camera_uniforms[1];
			case 2: armory.renderpath.Postprocess.camera_uniforms[2];
			case 3: armory.renderpath.Postprocess.camera_uniforms[3];
			case 4: armory.renderpath.Postprocess.camera_uniforms[4];
			case 5: armory.renderpath.Postprocess.camera_uniforms[5];
			case 6: armory.renderpath.Postprocess.camera_uniforms[6];
			case 7: armory.renderpath.Postprocess.camera_uniforms[7];
			case 8: armory.renderpath.Postprocess.camera_uniforms[8];
			case 9: armory.renderpath.Postprocess.camera_uniforms[9];
			case 10: armory.renderpath.Postprocess.camera_uniforms[10];
			default: 0.0;
		}
	}
}
