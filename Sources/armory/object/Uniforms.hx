package armory.object;

import iron.Scene;
import iron.object.Object;
import iron.data.MaterialData;
import iron.math.Vec4;
import iron.math.Vec3;

import armory.renderpath.Postprocess;
import armory.renderpath.Voxels;
import armory.renderpath.Inc;

using StringTools;

// Structure for setting shader uniforms
class Uniforms {

	public static function register() {
		iron.object.Uniforms.externalTextureLinks = [textureLink];
		iron.object.Uniforms.externalVec2Links = [vec2Link];
		iron.object.Uniforms.externalVec3Links = [vec3Link];
		iron.object.Uniforms.externalVec4Links = [];
		iron.object.Uniforms.externalFloatLinks = [floatLink];
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

			#if (rp_voxels != "Off")
			case "_eyeSnap": {
				/* This snipet is served by CHATGPT */
				var camera = iron.Scene.active.camera;
				var viewerPos = new iron.math.Vec3(camera.transform.worldx(), camera.transform.worldy(), camera.transform.worldz());
				var voxelPos = new iron.math.Vec3(0, 0, 0);

				var voxelDist = Vec3.distance(voxelPos, viewerPos);
				var clipmapLevel = Math.floor(Math.log(voxelDist / Main.voxelgiVoxelSize)) + 1;
				var l = camera.lookWorld();

				viewerPos.x += l.x;
				viewerPos.y += l.y;
				viewerPos.z += l.z;

				var f = Main.voxelgiVoxelSize / (Inc.getVoxelRes() * Math.pow(2.0, clipmapLevel-1));
				voxelPos.x = Math.floor(viewerPos.x / f) * f;
				voxelPos.y = Math.floor(viewerPos.y / f) * f;
				voxelPos.z = Math.floor(viewerPos.z / f) * f;

				v = iron.object.Uniforms.helpVec;
				v.set(voxelPos.x, voxelPos.y, voxelPos.z);
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
			#if (rp_voxels != 'Off')
			case "_voxelSize": {
				var camera = iron.Scene.active.camera;
				var viewerPos = new iron.math.Vec3(camera.transform.worldx(), camera.transform.worldy(), camera.transform.worldz());
				var voxelPos = new iron.math.Vec3(0, 0, 0);

				var voxelDist = Vec3.distance(voxelPos, viewerPos);
				var clipmapLevel = Math.floor(Math.log(voxelDist / Main.voxelgiVoxelSize)) + 1;
				Voxels.voxelsize = ((Main.voxelgiHalfExtents * 2 * (1 + 2 + 3 + 4 + 5)) / (armory.renderpath.Inc.getVoxelRes() * (Math.pow(2, clipmapLevel))));
				return Voxels.voxelsize;
			}
			case "_voxelBlend": { // Blend current and last voxels
				var freq = Voxels.voxelFreq;
				return (Voxels.voxelFrame % freq) / freq;
			}
			case "_clipmapLevelSize": {
				var camera = iron.Scene.active.camera;
				var viewerPos = new iron.math.Vec3(camera.transform.worldx(), camera.transform.worldy(), camera.transform.worldz());
				var voxelPos = new iron.math.Vec3(0, 0, 0);

				var voxelDist = Vec3.distance(voxelPos, viewerPos);
				var clipmapLevel = Math.floor(Math.log(voxelDist / Main.voxelgiVoxelSize)) + 1;

				Voxels.clipmapLevelSize = Main.voxelgiHalfExtents * 2 * Math.pow(2.0, clipmapLevel-1);
				return Voxels.clipmapLevelSize;
			}
			#end
		}
		return null;
	}

	public static function intLink(object: Object, mat: MaterialData, link: String): Null<Int> {
		switch (link) {
			#if (rp_voxels != 'Off')
			case "_clipmap_to_update": {
				return Voxels.clipmap_to_update;
			}
			#end
		}
		return null;
	}
}
