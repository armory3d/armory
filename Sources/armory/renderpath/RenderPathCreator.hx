// Reference: https://github.com/armory3d/armory_docs/blob/master/dev/renderpath.md
package armory.renderpath;

import iron.RenderPath;

class RenderPathCreator {

	public static var path: RenderPath;

	public static var commands: Void->Void = function() {};

	#if (rp_renderer == "Forward")
	public static var setTargetMeshes: Void->Void = RenderPathForward.setTargetMeshes;
	public static var drawMeshes: Void->Void = RenderPathForward.drawMeshes;
	public static var applyConfig: Void->Void = RenderPathForward.applyConfig;
	#elseif (rp_renderer == "Deferred")
	public static var setTargetMeshes: Void->Void = RenderPathDeferred.setTargetMeshes;
	public static var drawMeshes: Void->Void = RenderPathDeferred.drawMeshes;
	public static var applyConfig: Void->Void = RenderPathDeferred.applyConfig;
	#else
	public static var setTargetMeshes: Void->Void = function() {};
	public static var drawMeshes: Void->Void = function() {};
	public static var applyConfig: Void->Void = function() {};
	#end

	public static function get(): RenderPath {
		path = new RenderPath();
		Inc.init(path);

		#if rp_pp
		iron.App.notifyOnInit(function() {
			Postprocess.init();
		});
		#end

		#if (rp_renderer == "Forward")
			RenderPathForward.init(path);
			path.commands = function() {
				RenderPathForward.commands();
				commands();
			}
			path.setupDepthTexture = RenderPathForward.setupDepthTexture;
		#elseif (rp_renderer == "Deferred")
			RenderPathDeferred.init(path);
			path.commands = function() {
				RenderPathDeferred.commands();
				commands();
			}
			path.setupDepthTexture = RenderPathDeferred.setupDepthTexture;
		#elseif (rp_renderer == "Raytracer")
			RenderPathRaytracer.init(path);
			path.commands = function() {
				RenderPathRaytracer.commands();
				commands();
			}
		#end
		return path;
	}

	#if rp_voxels
	public static var voxelFrame = 0;
	public static var voxelFreq = 4; // Revoxelizing frequency
	#end

	// Last target before drawing to framebuffer
	public static var finalTarget: RenderTarget = null;
}
