package armory.logicnode;

class CameraGetNode extends LogicNode {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function get(from:Int):Dynamic {
        if(from == 0) {
            return armory.renderpath.Postprocess.camera_uniforms[0];
        } else if (from == 1) {
            return armory.renderpath.Postprocess.camera_uniforms[1];
        }  else if (from == 2) {
            return armory.renderpath.Postprocess.camera_uniforms[2];
        }  else if (from == 3) {
            return armory.renderpath.Postprocess.camera_uniforms[3];
        }  else if (from == 4) {
            return armory.renderpath.Postprocess.camera_uniforms[4];
        }  else if (from == 5) {
            return armory.renderpath.Postprocess.camera_uniforms[5];
        }  else if (from == 6) {
            return armory.renderpath.Postprocess.camera_uniforms[6];
        }  else if (from == 7) {
            return armory.renderpath.Postprocess.camera_uniforms[7];
        }  else if (from == 8) {
            return armory.renderpath.Postprocess.camera_uniforms[8];
        } else {
            return 0.0;
        }
    }
}
