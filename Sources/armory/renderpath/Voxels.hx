package armory.renderpath;

import iron.RenderPath;
import iron.Scene;
import iron.math.Vec3;

class Voxels {

	public static var voxelFrame = 0;
	public static var voxelFreq = 6;

	public static function voxelize(voxels)
	{
		var path = RenderPath.active;

        path.clearImage(voxels, 0x00000000);

		path.setTarget("");
		var res = Inc.getVoxelRes();
		path.setViewport(res, res);
		path.bindTarget(voxels, "voxels");

		#if rp_shadowmap
		{
			#if arm_shadowmap_atlas
			Inc.bindShadowMapAtlas();
			#else
			Inc.bindShadowMap();
			#end
		}
		#end

		path.drawMeshes("voxel");
		path.generateMipmaps(voxels);
	}
}
