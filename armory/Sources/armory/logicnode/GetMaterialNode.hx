package armory.logicnode;

import iron.object.MeshObject;
import iron.object.DecalObject;

class GetMaterialNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {

		var object = inputs[0].get();

		assert(Error, object != null, "The object input must not be null");

		#if rp_decals
		if (Std.isOfType(object, DecalObject)) {
			var decal = cast(object, DecalObject);
			return decal.material;
		}
		#end

		if (Std.isOfType(object, MeshObject)) {
			var mesh = cast(object, MeshObject);
			var slot: Int = inputs[1].get();
			
			if (mesh == null) return null;
			
			return mesh.materials[slot];
		}

		return null;
	}
}
