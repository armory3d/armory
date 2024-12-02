package armory.logicnode;

class SSRSetNode extends LogicNode {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run(from:Int) {

        armory.renderpath.Postprocess.ssr_uniforms[0] = inputs[1].get();
        armory.renderpath.Postprocess.ssr_uniforms[1] = inputs[2].get();
        armory.renderpath.Postprocess.ssr_uniforms[2] = inputs[3].get();
        armory.renderpath.Postprocess.ssr_uniforms[3] = inputs[4].get();
		armory.renderpath.Postprocess.ssr_uniforms[4] = inputs[5].get();

		runOutput(0);
	}
}
