// Reference: https://github.com/armory3d/armory_docs/blob/master/dev/renderpath.md
package armory.renderpath;

import iron.RenderPath;

class RenderPathCreator {

	public static var path:RenderPath;

	#if (rp_renderer == "Forward")
	public static var drawMeshes:Void->Void = RenderPathForward.drawMeshes;
	#else
	public static var drawMeshes:Void->Void = RenderPathDeferred.drawMeshes;
	#end

	public static function get():RenderPath {
		path = new RenderPath();
		Inc.init(path);
		#if (rp_renderer == "Forward")
		RenderPathForward.init(path);
		path.commands = RenderPathForward.commands;
		#else
		RenderPathDeferred.init(path);
		path.commands = RenderPathDeferred.commands;
		#end
		return path;
	}

	#if (rp_gi != "Off")
	public static var voxelFrame = 0;
	public static var voxelFreq = 6; // Revoxelizing frequency
	#end

	// Last target before drawing to framebuffer
	public static var finalTarget:RenderTarget = null;
}
