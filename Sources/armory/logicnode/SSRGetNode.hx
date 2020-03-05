package armory.logicnode;

class SSRGetNode extends LogicNode {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function get(from:Int):Dynamic {
        if(from == 0) {
            return armory.renderpath.Postprocess.ssr_uniforms[0];
        } else if (from == 1) {
            return armory.renderpath.Postprocess.ssr_uniforms[1];
        }  else if (from == 2) {
            return armory.renderpath.Postprocess.ssr_uniforms[2];
        }  else if (from == 3) {
            return armory.renderpath.Postprocess.ssr_uniforms[3];
        }  else if (from == 4) {
            return armory.renderpath.Postprocess.ssr_uniforms[4];
        } else {
            return 0.0;
        }
    }
}
