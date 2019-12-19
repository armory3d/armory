package armory.logicnode;

class RpShadowQualityNode extends LogicNode {

    public var property0: String;

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int){

        switch (property0) {
		case "High":
            armory.data.Config.raw.rp_shadowmap_cascade = 4096;
        case "Medium":
            armory.data.Config.raw.rp_shadowmap_cascade = 2048;
        case "Low":
            armory.data.Config.raw.rp_shadowmap_cascade = 1024;
        }

        armory.renderpath.RenderPathCreator.applyConfig();
        armory.data.Config.save();
		runOutput(0);
	}
}
