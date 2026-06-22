package armory.logicnode;

class ColorgradingGetGlobalNode extends LogicNode {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function get(from:Int):Dynamic {
		return switch (from) {
			case 0: armory.renderpath.Postprocess.colorgrading_global_uniforms[0][0];
			case 1: armory.renderpath.Postprocess.colorgrading_global_uniforms[1];
			case 2: armory.renderpath.Postprocess.colorgrading_global_uniforms[2];
			case 3: armory.renderpath.Postprocess.colorgrading_global_uniforms[3];
			case 4: armory.renderpath.Postprocess.colorgrading_global_uniforms[4];
			case 5: armory.renderpath.Postprocess.colorgrading_global_uniforms[5];
			case 6: armory.renderpath.Postprocess.colorgrading_global_uniforms[6];
			default: 0.0;
		}
	}
}
