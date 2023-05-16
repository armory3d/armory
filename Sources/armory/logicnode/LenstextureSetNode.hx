package armory.logicnode;

class LenstextureSetNode extends LogicNode {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run(from:Int) {

        armory.renderpath.Postprocess.lenstexture_uniforms[0] = inputs[1].get();
        armory.renderpath.Postprocess.lenstexture_uniforms[1] = inputs[2].get();
        armory.renderpath.Postprocess.lenstexture_uniforms[2] = inputs[3].get();
		armory.renderpath.Postprocess.lenstexture_uniforms[3] = inputs[4].get();
		armory.renderpath.Postprocess.lenstexture_uniforms[4] = inputs[5].get();

		runOutput(0);
	}
}
