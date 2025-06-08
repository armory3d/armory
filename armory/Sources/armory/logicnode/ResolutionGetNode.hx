package armory.logicnode;

class ResolutionGetNode extends LogicNode {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function get(from:Int):Dynamic {
		return switch (from) {
			case 0: armory.renderpath.Postprocess.resolution_uniforms[0];
			case 1: armory.renderpath.Postprocess.resolution_uniforms[1];
			default: 0;
		}
	}
}
