package armory.logicnode;

class BloomSetNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {

		armory.renderpath.Postprocess.bloom_uniforms[0] = inputs[1].get();
		armory.renderpath.Postprocess.bloom_uniforms[1] = inputs[2].get();
		armory.renderpath.Postprocess.bloom_uniforms[2] = inputs[3].get();

		final rawPostprocess = iron.Scene.active.raw.post_process;
		if (rawPostprocess != null && rawPostprocess.bloom != null) {
			rawPostprocess.bloom.radius = inputs[4].get();
		}

		runOutput(0);
	}
}
