package armory.logicnode;

class BloomSetNode extends LogicNode {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run(from:Int) {

        armory.renderpath.Postprocess.bloom_uniforms[0] = inputs[1].get();
        armory.renderpath.Postprocess.bloom_uniforms[1] = inputs[2].get();
        armory.renderpath.Postprocess.bloom_uniforms[2] = inputs[3].get();

		runOutput(0);
	}
}
