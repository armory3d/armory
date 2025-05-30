package armory.logicnode;

class AutoExposureGetNode extends LogicNode {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function get(from:Int):Dynamic {
		return switch (from) {
			case 0: armory.renderpath.Postprocess.auto_exposure[0];
			case 1: armory.renderpath.Postprocess.auto_exposure[1];
			default: 0.0;
		}
	}
}
