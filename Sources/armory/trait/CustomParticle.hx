package armory.trait;

import iron.object.MeshObject;

/**
 * Trait to enable GPU instancing of Mesh objects
 */
class CustomParticle extends iron.Trait {

	@prop
	var ParticleCount: Int = 100;

	public function new() {
		super();

		notifyOnInit(function() {
			var partCount = ParticleCount;
			setupSimpleInstanced(partCount);
		});
	}

	function setupSimpleInstanced(count: Int){
		if(object.raw.type == 'mesh_object')
		{
			var meshObjGeom = cast(object, MeshObject).data.geom;
			meshObjGeom.instanced = true;
			meshObjGeom.instanceCount = count;
		}
	}

	public function updateParticleCount(count: Int){

		if(object.raw.type == 'mesh_object')
		{
			var meshObjGeom = cast(object, MeshObject).data.geom;
			meshObjGeom.instanced = true;
			meshObjGeom.instanceCount = count;
		}
	}
}
