package armory.logicnode;

class RpMSAANode extends LogicNode {

	public var property0: String;

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int){

		switch (property0) {
		case "1":
			armory.data.Config.raw.window_msaa = 1;
		case "2":
			armory.data.Config.raw.window_msaa = 2;
        case "4":
			armory.data.Config.raw.window_msaa = 4;
        case "8":
			armory.data.Config.raw.window_msaa = 8;
		case "16":
			armory.data.Config.raw.window_msaa = 16;
		}
		armory.renderpath.RenderPathCreator.applyConfig();
        armory.data.Config.save();
		runOutput(0);
	}
}
