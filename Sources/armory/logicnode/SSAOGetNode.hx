package armory.logicnode;

class SSAOGetNode extends LogicNode {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function get(from:Int):Dynamic {
        if(from == 0) {
            return armory.renderpath.Postprocess.ssao_uniforms[0];
        } else if (from == 1) {
            return armory.renderpath.Postprocess.ssao_uniforms[1];
        }  else if (from == 2) {
            return armory.renderpath.Postprocess.ssao_uniforms[2];
        } else {
            return 0.0;
        }
    }
}
