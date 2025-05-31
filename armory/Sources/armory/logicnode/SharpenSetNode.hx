package armory.logicnode;

class SharpenSetNode extends LogicNode {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run(from:Int) {
        armory.renderpath.Postprocess.sharpen_uniforms[0][0] = inputs[1].get().x;
        armory.renderpath.Postprocess.sharpen_uniforms[0][1] = inputs[1].get().y;
        armory.renderpath.Postprocess.sharpen_uniforms[0][2] = inputs[1].get().z;
        armory.renderpath.Postprocess.sharpen_uniforms[1][0] = inputs[2].get();
        armory.renderpath.Postprocess.camera_uniforms[12] = inputs[3].get();

		runOutput(0);
	}
}
