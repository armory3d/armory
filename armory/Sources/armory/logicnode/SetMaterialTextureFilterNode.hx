package armory.logicnode;

import iron.object.MeshObject;
import iron.data.MaterialData;

class SetMaterialTextureFilterNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		var object: MeshObject = inputs[1].get();
		var mat: MaterialData = inputs[2].get();
		var slot: Int = inputs[3].get();
		var name: String = inputs[4].get();
		var filter: Int = inputs[5].get();

		if (object == null) return;
		if (slot >= object.materials.length) return;

		var mo = cast(object, iron.object.MeshObject);

		for (i => node in mo.materials[slot].contexts[0].raw.bind_textures)
			if (node.name == name){
				var moImgt = mo.materials[slot].contexts[0].raw.bind_textures[i];
				switch(filter){
					case 0: //Linear
						moImgt.min_filter = null;
						moImgt.mag_filter = null;
						moImgt.mipmap_filter = null;
						moImgt.generate_mipmaps = null;
					case 1: //Closest
						moImgt.min_filter = 'point';
						moImgt.mag_filter = 'point';
						moImgt.mipmap_filter = null;
						moImgt.generate_mipmaps = null;
					case 2: //Cubic
						moImgt.min_filter = null;
						moImgt.mag_filter = null;
						moImgt.mipmap_filter = 'linear';
						moImgt.generate_mipmaps = true;
					case 3: //Smart
						moImgt.min_filter = 'anisotropic';
						moImgt.mag_filter = null;
						moImgt.mipmap_filter = 'linear';
						moImgt.generate_mipmaps = true;
				}

				break;
			}

		runOutput(0);
	}
}