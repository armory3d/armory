package armory.logicnode;

class RpConfigNode extends LogicNode {

	public var property0: String;

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int){
        var on: Bool = inputs[1].get();

		switch (property0) {
		case "SSGI":
			on ? armory.data.Config.raw.rp_ssgi = true : armory.data.Config.raw.rp_ssgi = false;
		case "SSR":
			on ? armory.data.Config.raw.rp_ssr = true : armory.data.Config.raw.rp_ssr = false;
        	case "Bloom":
			on ? armory.data.Config.raw.rp_bloom = true : armory.data.Config.raw.rp_bloom = false;
        	case "GI":
			on ? armory.data.Config.raw.rp_voxels = true : armory.data.Config.raw.rp_voxels = false;
		case "Motion Blur":
			on ? armory.data.Config.raw.rp_motionblur = true : armory.data.Config.raw.rp_motionblur = false;
		}
		armory.renderpath.RenderPathCreator.applyConfig();
        armory.data.Config.save();
		runOutput(0);
	}
}
