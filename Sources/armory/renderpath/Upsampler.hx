package armory.renderpath;

import haxe.ds.ReadOnlyArray;

import iron.RenderPath;
import iron.data.MaterialData;
import iron.object.Object;

import armory.math.Helper;

abstract class Upsampler {

	public static var currentMipLevel(default, null) = 0;
	public static var numMipLevels(default, null) = 0;

	static var isRegistered = false;

	final path: RenderPath;
	final shaderPassHandle: String;
	final mipmaps: ReadOnlyArray<RenderTarget>;

	function new(path: RenderPath, shaderPassHandle: String, mipmaps: ReadOnlyArray<RenderTarget>) {
		this.path = path;
		this.shaderPassHandle = shaderPassHandle;
		this.mipmaps = mipmaps;
	}

	public static function create(path: RenderPath, shaderPassHandle: String, mipmaps: ReadOnlyArray<RenderTarget>): Upsampler {
		if (!isRegistered) {
			isRegistered = true;
			iron.object.Uniforms.externalIntLinks.push(intLink);
		}

		// TODO, see Downsampler.hx
		// if (RenderPath.hasComputeSupport()) {
		// 	return new UpsamplerCompute(path, shaderPassHandle, mipmaps);
		// }
		// else {
			return new UpsamplerFragment(path, shaderPassHandle, mipmaps);
		// }
	}

	static function intLink(object: Object, mat: MaterialData, link: String): Null<Int> {
		return switch (link) {
			case "_upsampleCurrentMip": Upsampler.currentMipLevel;
			case "_upsampleNumMips": Upsampler.numMipLevels;
			default: null;
		}
	}

	abstract public function dispatch(dstImageName: String, numMips: Int = 0): Void;
}

private class UpsamplerFragment extends Upsampler {

	public function new(path: RenderPath, shaderPassHandle: String, mipmaps: ReadOnlyArray<RenderTarget>) {
		super(path, shaderPassHandle, mipmaps);
		path.loadShader(shaderPassHandle);
	}

	public function dispatch(dstImageName: String, numMips: Int = 0) {
		Helper.clampInt(numMips, 0, mipmaps.length);
		if (numMips == 0) {
			numMips = mipmaps.length;
		}

		final srcImageRT = path.renderTargets.get(dstImageName);
		assert(Error, srcImageRT != null);

		final srcImage = srcImageRT.image;
		assert(Error, srcImage != null);

		Upsampler.numMipLevels = numMips;
		for (i in 0...Upsampler.numMipLevels) {
			final mipLevel = Upsampler.numMipLevels - 1 - i;
			Upsampler.currentMipLevel = mipLevel;

			path.setTarget(mipLevel == 0 ? dstImageName : mipmaps[mipLevel - 1].raw.name);
			path.bindTarget(mipmaps[mipLevel].raw.name, "tex");
			path.drawShader(shaderPassHandle);
		}
	}
}
