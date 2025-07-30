package armory.logicnode;

class RpSuperSampleNode extends LogicNode {

	public var property0: String;

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int){

		switch (property0) {
		case "1":
			armory.data.Config.raw.rp_supersample = 1;
		case "1.5":
			armory.data.Config.raw.rp_supersample = 1.5;
        case "2":
			armory.data.Config.raw.rp_supersample = 2;
        case "4":
			armory.data.Config.raw.rp_supersample = 4;
		}
		armory.renderpath.RenderPathCreator.applyConfig();
        armory.data.Config.save();
		runOutput(0);
	}
}
