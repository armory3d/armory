package armory.logicnode;

class BloomGetNode extends LogicNode {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function get(from:Int):Dynamic {
		return switch (from) {
			case 0: armory.renderpath.Postprocess.bloom_uniforms[0];
			case 1: armory.renderpath.Postprocess.bloom_uniforms[1];
			case 2: armory.renderpath.Postprocess.bloom_uniforms[2];
			default: 0.0;
		}
	}
}
