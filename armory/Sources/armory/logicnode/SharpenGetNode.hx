package armory.logicnode;

class SharpenGetNode extends LogicNode {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function get(from:Int):Dynamic {
		return switch (from) {
			case 0: armory.renderpath.Postprocess.sharpen_uniforms[0];
			case 1: armory.renderpath.Postprocess.sharpen_uniforms[1][0];
			case 2: armory.renderpath.Postprocess.camera_uniforms[12];
			default: 0.0;
		}
	}
}
