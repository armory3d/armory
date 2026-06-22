package armory.logicnode;

class LetterboxSetNode extends LogicNode {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run(from:Int) {
        armory.renderpath.Postprocess.letterbox_uniforms[0][0] = inputs[1].get().x;
        armory.renderpath.Postprocess.letterbox_uniforms[0][1] = inputs[1].get().y;
        armory.renderpath.Postprocess.letterbox_uniforms[0][2] = inputs[1].get().z;
        armory.renderpath.Postprocess.letterbox_uniforms[1][0] = inputs[2].get();

		runOutput(0);
	}
}
