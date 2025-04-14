package armory.object;

import iron.Scene;
import iron.object.Object;
import iron.data.MaterialData;
import iron.math.Vec4;

import kha.arrays.Float32Array;

import armory.renderpath.Postprocess;

using StringTools;

// Structure for setting shader uniforms
class Uniforms {

	public static function register() {
		iron.object.Uniforms.externalTextureLinks = [textureLink];
		iron.object.Uniforms.externalVec2Links = [vec2Link];
		iron.object.Uniforms.externalVec3Links = [vec3Link];
		iron.object.Uniforms.externalVec4Links = [];
		iron.object.Uniforms.externalFloatLinks = [floatLink];
		iron.object.Uniforms.externalFloatsLinks = [floatsLink];
		iron.object.Uniforms.externalIntLinks = [intLink];
	}

	public static function textureLink(object: Object, mat: MaterialData, link: String): Null<kha.Image> {
		switch (link) {
			case "_nishitaLUT": {
				if (armory.renderpath.Nishita.data == null) armory.renderpath.Nishita.recompute(Scene.active.world);
				return armory.renderpath.Nishita.data.lut;
			}
			#if arm_ltc
			case "_ltcMat": {
				if (armory.data.ConstData.ltcMatTex == null) armory.data.ConstData.initLTC();
				return armory.data.ConstData.ltcMatTex;
			}
			case "_ltcMag": {
				if (armory.data.ConstData.ltcMagTex == null) armory.data.ConstData.initLTC();
				return armory.data.ConstData.ltcMagTex;
			}
			#end
			#if arm_morph_target
			case "_morphDataPos": {
				return cast(object, iron.object.MeshObject).morphTarget.morphDataPos;
			}
			case "_morphDataNor": {
				return cast(object, iron.object.MeshObject).morphTarget.morphDataNor;
			}
			#end
		}

		var target = iron.RenderPath.active.renderTargets.get(link.endsWith("_depth") ? link.substr(0, link.length - 6) : link);
		return target != null ? target.image : null;
	}

	public static function vec3Link(object: Object, mat: MaterialData, link: String): Null<iron.math.Vec4> {
		var v: Vec4 = null;
		switch (link) {
			#if arm_hosek
			case "_hosekA": {
				if (armory.renderpath.HosekWilkie.data == null) {
					armory.renderpath.HosekWilkie.recompute(Scene.active.world);
				}
				if (armory.renderpath.HosekWilkie.data != null) {
					v = iron.object.Uniforms.helpVec;
					v.x = armory.renderpath.HosekWilkie.data.A.x;
					v.y = armory.renderpath.HosekWilkie.data.A.y;
					v.z = armory.renderpath.HosekWilkie.data.A.z;
				}
			}
			case "_hosekB": {
				if (armory.renderpath.HosekWilkie.data == null) {
					armory.renderpath.HosekWilkie.recompute(Scene.active.world);
				}
				if (armory.renderpath.HosekWilkie.data != null) {
					v = iron.object.Uniforms.helpVec;
					v.x = armory.renderpath.HosekWilkie.data.B.x;
					v.y = armory.renderpath.HosekWilkie.data.B.y;
					v.z = armory.renderpath.HosekWilkie.data.B.z;
				}
			}
			case "_hosekC": {
				if (armory.renderpath.HosekWilkie.data == null) {
					armory.renderpath.HosekWilkie.recompute(Scene.active.world);
				}
				if (armory.renderpath.HosekWilkie.data != null) {
					v = iron.object.Uniforms.helpVec;
					v.x = armory.renderpath.HosekWilkie.data.C.x;
					v.y = armory.renderpath.HosekWilkie.data.C.y;
					v.z = armory.renderpath.HosekWilkie.data.C.z;
				}
			}
			case "_hosekD": {
				if (armory.renderpath.HosekWilkie.data == null) {
					armory.renderpath.HosekWilkie.recompute(Scene.active.world);
				}
				if (armory.renderpath.HosekWilkie.data != null) {
					v = iron.object.Uniforms.helpVec;
					v.x = armory.renderpath.HosekWilkie.data.D.x;
					v.y = armory.renderpath.HosekWilkie.data.D.y;
					v.z = armory.renderpath.HosekWilkie.data.D.z;
				}
			}
			case "_hosekE": {
				if (armory.renderpath.HosekWilkie.data == null) {
					armory.renderpath.HosekWilkie.recompute(Scene.active.world);
				}
				if (armory.renderpath.HosekWilkie.data != null) {
					v = iron.object.Uniforms.helpVec;
					v.x = armory.renderpath.HosekWilkie.data.E.x;
					v.y = armory.renderpath.HosekWilkie.data.E.y;
					v.z = armory.renderpath.HosekWilkie.data.E.z;
				}
			}
			case "_hosekF": {
				if (armory.renderpath.HosekWilkie.data == null) {
					armory.renderpath.HosekWilkie.recompute(Scene.active.world);
				}
				if (armory.renderpath.HosekWilkie.data != null) {
					v = iron.object.Uniforms.helpVec;
					v.x = armory.renderpath.HosekWilkie.data.F.x;
					v.y = armory.renderpath.HosekWilkie.data.F.y;
					v.z = armory.renderpath.HosekWilkie.data.F.z;
				}
			}
			case "_hosekG": {
				if (armory.renderpath.HosekWilkie.data == null) {
					armory.renderpath.HosekWilkie.recompute(Scene.active.world);
				}
				if (armory.renderpath.HosekWilkie.data != null) {
					v = iron.object.Uniforms.helpVec;
					v.x = armory.renderpath.HosekWilkie.data.G.x;
					v.y = armory.renderpath.HosekWilkie.data.G.y;
					v.z = armory.renderpath.HosekWilkie.data.G.z;
				}
			}
			case "_hosekH": {
				if (armory.renderpath.HosekWilkie.data == null) {
					armory.renderpath.HosekWilkie.recompute(Scene.active.world);
				}
				if (armory.renderpath.HosekWilkie.data != null) {
					v = iron.object.Uniforms.helpVec;
					v.x = armory.renderpath.HosekWilkie.data.H.x;
					v.y = armory.renderpath.HosekWilkie.data.H.y;
					v.z = armory.renderpath.HosekWilkie.data.H.z;
				}
			}
			case "_hosekI": {
				if (armory.renderpath.HosekWilkie.data == null) {
					armory.renderpath.HosekWilkie.recompute(Scene.active.world);
				}
				if (armory.renderpath.HosekWilkie.data != null) {
					v = iron.object.Uniforms.helpVec;
					v.x = armory.renderpath.HosekWilkie.data.I.x;
					v.y = armory.renderpath.HosekWilkie.data.I.y;
					v.z = armory.renderpath.HosekWilkie.data.I.z;
				}
			}
			case "_hosekZ": {
				if (armory.renderpath.HosekWilkie.data == null) {
					armory.renderpath.HosekWilkie.recompute(Scene.active.world);
				}
				if (armory.renderpath.HosekWilkie.data != null) {
					v = iron.object.Uniforms.helpVec;
					v.x = armory.renderpath.HosekWilkie.data.Z.x;
					v.y = armory.renderpath.HosekWilkie.data.Z.y;
					v.z = armory.renderpath.HosekWilkie.data.Z.z;
				}
			}
			#end
		}
		return v;
	}

	public static function vec2Link(object: Object, mat: MaterialData, link: String): Null<iron.math.Vec4> {
		var v: Vec4 = null;
		switch (link) {
			case "_nishitaDensity": {
				var w = Scene.active.world;
				if (w != null) {
					v = iron.object.Uniforms.helpVec;
					// We only need Rayleigh and Mie density in the sky shader -> Vec2
					v.x = w.raw.nishita_density[0];
					v.y = w.raw.nishita_density[1];
				}
			}
		}

		return v;
	}

	public static function floatLink(object: Object, mat: MaterialData, link: String): Null<kha.FastFloat> {
		switch (link) {
			#if rp_dynres
			case "_dynamicScale": {
				return armory.renderpath.DynamicResolutionScale.dynamicScale;
			}
			#end
			#if arm_debug
			case "_debugFloat": {
				return armory.trait.internal.DebugConsole.debugFloat;
			}
			#end
			#if rp_bloom
			case "_bloomSampleScale": {
				return Postprocess.bloom_uniforms[3];
			}
			#end
		}
		return null;
	}

	public static function floatsLink(object: Object, mat: MaterialData, link: String): Float32Array {
		switch (link) {
			#if (rp_voxels != "Off")
			case "_clipmaps": {
				var clipmaps = iron.RenderPath.clipmaps;
				var fa:Float32Array = new Float32Array(Main.voxelgiClipmapCount * 10);
				for (i in 0...Main.voxelgiClipmapCount) {
					fa[i * 10] = clipmaps[i].voxelSize;
					fa[i * 10 + 1] = clipmaps[i].extents.x;
					fa[i * 10 + 2] = clipmaps[i].extents.y;
					fa[i * 10 + 3] = clipmaps[i].extents.z;
					fa[i * 10 + 4] = clipmaps[i].center.x;
					fa[i * 10 + 5] = clipmaps[i].center.y;
					fa[i * 10 + 6] = clipmaps[i].center.z;
					fa[i * 10 + 7] = clipmaps[i].offset_prev.x;
					fa[i * 10 + 8] = clipmaps[i].offset_prev.y;
					fa[i * 10 + 9] = clipmaps[i].offset_prev.z;
				}
				return fa;
			}
			#end
		}
		return null;
	}

	public static function intLink(object: Object, mat: MaterialData, link: String): Null<Int> {
		switch (link) {
			#if (rp_voxels != "Off")
			case "_clipmapLevel": {
				return iron.RenderPath.clipmapLevel;
			}
			#end
		}
		return null;
	}
}
