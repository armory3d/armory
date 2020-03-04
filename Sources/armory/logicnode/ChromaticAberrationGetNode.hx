package armory.logicnode;

class ChromaticAberrationGetNode extends LogicNode {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function get(from:Int):Dynamic {
        if(from == 0) {
            return armory.renderpath.Postprocess.chromatic_aberration_uniforms[0];
        } else if (from == 1) {
            return armory.renderpath.Postprocess.chromatic_aberration_uniforms[1];
        } else {
            return 0.0;
        }
    }
}
