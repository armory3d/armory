package armory.logicnode;

class ChromaticAberrationGetNode extends LogicNode {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function get(from:Int):Dynamic {
		return switch (from) {
			case 0: armory.renderpath.Postprocess.chromatic_aberration_uniforms[0];
			case 1: armory.renderpath.Postprocess.chromatic_aberration_uniforms[1];
			default: 0.0;
		}
	}
}
