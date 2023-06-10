package armory.renderpath;

import haxe.ds.ReadOnlyArray;

import iron.RenderPath;
import iron.data.MaterialData;
import iron.object.Object;

import armory.math.Helper;

abstract class Downsampler {

	public static var currentMipLevel(default, null) = 0;
	public static var numMipLevels(default, null) = 0;

	static var isRegistered = false;

	final path: RenderPath;
	final shaderPassHandle: String;
	final maxNumMips: Int;
	final mipmaps: Array<RenderTarget>;

	function new(path: RenderPath, shaderPassHandle: String, maxNumMips: Int) {
		this.path = path;
		this.shaderPassHandle = shaderPassHandle;
		this.maxNumMips = maxNumMips;

		this.mipmaps = new Array();
		mipmaps.resize(maxNumMips);
	}

	public static function create(path: RenderPath, shaderPassHandle: String, rtName: String, maxNumMips: Int = 10): Downsampler {
		if (!isRegistered) {
			isRegistered = true;
			iron.object.Uniforms.externalIntLinks.push(intLink);
		}

		// TODO, implement when Kha supports render targets in compute shaders
		// and allows to query whether compute shaders are available
		// if (RenderPath.hasComputeSupport()) {
		// 	return new DownsamplerCompute(path, shaderPassHandle, rtName, maxNumMips);
		// }
		// else {
			return new DownsamplerFragment(path, shaderPassHandle, rtName, maxNumMips);
		// }
	}

	static function intLink(object: Object, mat: MaterialData, link: String): Null<Int> {
		return switch (link) {
			case "_downsampleCurrentMip": Downsampler.currentMipLevel;
			case "_downsampleNumMips": Downsampler.numMipLevels;
			default: null;
		}
	}

	public inline function getMipmaps(): ReadOnlyArray<RenderTarget> {
		return mipmaps;
	}

	abstract public function dispatch(srcImageName: String, numMips: Int = 0): Void;
}

private class DownsamplerFragment extends Downsampler {

	public function new(path: RenderPath, shaderPassHandle: String, rtName: String, maxNumMips: Int) {
		super(path, shaderPassHandle, maxNumMips);

		var prevScale = 1.0;
		for (i in 0...maxNumMips) {
			var t = new RenderTargetRaw();
			t.name = rtName + "_mip_" + i;
			t.width = 0;
			t.height = 0;
			t.scale = (prevScale *= 0.5);
			t.format = Inc.getHdrFormat();

			mipmaps[i] = path.createRenderTarget(t);
		}

		path.loadShader(shaderPassHandle);
	}

	public function dispatch(srcImageName: String, numMips: Int = 0) {
		Helper.clampInt(numMips, 0, maxNumMips);
		if (numMips == 0) {
			numMips = maxNumMips;
		}

		final srcImageRT = path.renderTargets.get(srcImageName);
		assert(Error, srcImageRT != null, 'Could not find render target with name $srcImageName');

		final srcImage = srcImageRT.image;
		assert(Error, srcImage != null);

		Downsampler.numMipLevels = numMips;
		for (i in 0...numMips) {
			Downsampler.currentMipLevel = i;
			path.setTarget(mipmaps[i].raw.name);
			path.clearTarget();
			path.bindTarget(i == 0 ? srcImageName : mipmaps[i - 1].raw.name, "tex");
			path.drawShader(shaderPassHandle);
		}
	}
}
