package armory.logicnode;

class ChromaticAberrationSetNode extends LogicNode {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run(from:Int) {

        armory.renderpath.Postprocess.chromatic_aberration_uniforms[0] = inputs[1].get();
        armory.renderpath.Postprocess.chromatic_aberration_uniforms[1] = inputs[2].get();

		runOutput(0);
	}
}
