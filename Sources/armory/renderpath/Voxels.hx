package armory.renderpath;

import iron.RenderPath;
import iron.Scene;
import iron.math.Vec3;

class Voxels {

	public static var voxelFrame = 0;
	public static var voxelFreq = 6; // Revoxelizing frequency
	public static var CLIPMAP_COUNT = 6;
	public static var clipmap_to_update = 0;
	public static var voxelsize = 0.0;
	public static var clipmapLevelSize = 0.0;

	public static function voxelize(voxels)
	{
		var path = RenderPath.active;

		path.clearImage(voxels, 0x00000000);

		if(path != null)
		{
			for(i in 0...6)
			{
				path.setTarget("");
				var res = Inc.getVoxelRes();
				path.setViewport(res, res);
				path.bindTarget(voxels, "voxels");
				#if (rp_voxels == "Voxel GI")
				path.bindTarget("voxelsNor", "voxelsNor");
				#end
				path.drawMeshes("voxel");
				Voxels.clipmap_to_update = (Voxels.clipmap_to_update + 1) % Voxels.CLIPMAP_COUNT;
			}
		}
		path.generateMipmaps(voxels);
	}
}
