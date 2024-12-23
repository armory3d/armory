package armory.logicnode;

class SSAOGetNode extends LogicNode {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function get(from:Int):Dynamic {

		return switch (from) {
			case 0: armory.renderpath.Postprocess.ssao_uniforms[0];
			case 1: armory.renderpath.Postprocess.ssao_uniforms[1];
			case 2: armory.renderpath.Postprocess.ssao_uniforms[2];
			default: 0.0;
		}
	}
}
