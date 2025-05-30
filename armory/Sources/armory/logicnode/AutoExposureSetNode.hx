package armory.logicnode;

class AutoExposureSetNode extends LogicNode {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run(from:Int) {
        armory.renderpath.Postprocess.auto_exposure_uniforms[0] = inputs[1].get();
        armory.renderpath.Postprocess.auto_exposure_uniforms[1] = inputs[2].get();

		runOutput(0);
	}
}
