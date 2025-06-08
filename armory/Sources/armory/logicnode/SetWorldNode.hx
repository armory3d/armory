package armory.logicnode;

class SetWorldNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		var world: String = inputs[1].get();

		if (world != null){

			//check if world shader data exists
			var file: String = 'World_'+world+'_data';
			#if arm_json
				file += ".json";
			#elseif arm_compress
				file += ".lz4";
			#else
				file += '.arm';
			#end

			var exists: Bool = false;
		
			iron.data.Data.getBlob(file, function(b: kha.Blob) {
				if (b != null) exists = true;
			});

			assert(Error, exists == true, "World must be either associated to a scene or have fake user");

			iron.Scene.active.raw.world_ref = world;
			var npath = armory.renderpath.RenderPathCreator.get();
			npath.loadShader("shader_datas/World_" + world + "/World_" + world);
			iron.RenderPath.setActive(npath);
		}

		runOutput(0);
	}
}
