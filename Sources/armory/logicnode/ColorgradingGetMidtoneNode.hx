package armory.logicnode;

class ColorgradingGetMidtoneNode extends LogicNode {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function get(from:Int):Dynamic {
		return switch (from) {
            		case 0: armory.renderpath.Postprocess.colorgrading_midtone_uniforms[0];
            		case 1: armory.renderpath.Postprocess.colorgrading_midtone_uniforms[1];
            		case 2: armory.renderpath.Postprocess.colorgrading_midtone_uniforms[2];
            		case 3: armory.renderpath.Postprocess.colorgrading_midtone_uniforms[3];
            		case 4: armory.renderpath.Postprocess.colorgrading_midtone_uniforms[4];
            		case 5: armory.renderpath.Postprocess.colorgrading_midtone_uniforms[5];
            		default: 0.0;
		}
	}

}
