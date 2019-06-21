package armory.object;

import iron.Scene;
import iron.object.Object;
import iron.data.MaterialData;
import iron.math.Vec4;

// Structure for setting shader uniforms
class Uniforms {

	public static function register() {
		iron.object.Uniforms.externalTextureLinks = [textureLink];
		iron.object.Uniforms.externalVec3Links = [vec3Link];
		iron.object.Uniforms.externalFloatLinks = [floatLink];
	}

	public static function textureLink(object:Object, mat:MaterialData, link:String):kha.Image {
		#if arm_ltc
		if (link == "_ltcMat") {
			if (armory.data.ConstData.ltcMatTex == null) armory.data.ConstData.initLTC();
			return armory.data.ConstData.ltcMatTex;
		}
		else if (link == "_ltcMag") {
			if (armory.data.ConstData.ltcMagTex == null) armory.data.ConstData.initLTC();
			return armory.data.ConstData.ltcMagTex;
		}
		#end
		return null;
	}

	public static function vec3Link(object:Object, mat:MaterialData, link:String):iron.math.Vec4 {
		var v:Vec4 = null;
		#if arm_hosek
		if (link == "_hosekA") {
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
		else if (link == "_hosekB") {
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
		else if (link == "_hosekC") {
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
		else if (link == "_hosekD") {
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
		else if (link == "_hosekE") {
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
		else if (link == "_hosekF") {
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
		else if (link == "_hosekG") {
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
		else if (link == "_hosekH") {
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
		else if (link == "_hosekI") {
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
		else if (link == "_hosekZ") {
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
		#if rp_voxelao
		if (link == "_cameraPositionSnap") {
			v = iron.object.Uniforms.helpVec;
			var camera = iron.Scene.active.camera;
			v.set(camera.transform.worldx(), camera.transform.worldy(), camera.transform.worldz());
			var l = camera.lookWorld();
			var e = Main.voxelgiHalfExtents;
			v.x += l.x * e * 0.9;
			v.y += l.y * e * 0.9;
			var f = Main.voxelgiVoxelSize * 8; // Snaps to 3 mip-maps range
			v.set(Math.floor(v.x / f) * f, Math.floor(v.y / f) * f, Math.floor(v.z / f) * f);
		}
		#end
		
		return v;
	}

	public static function floatLink(object:Object, mat:MaterialData, link:String):Null<kha.FastFloat> {
		#if rp_dynres
		if (link == "_dynamicScale") {
			return armory.renderpath.DynamicResolutionScale.dynamicScale;
		}
		#end
		#if arm_debug
		if (link == "_debugFloat") {
			return armory.trait.internal.DebugConsole.debugFloat;
		}
		#end
		#if rp_voxelao
		if (link == "_voxelBlend") { // Blend current and last voxels
			var freq = armory.renderpath.RenderPathCreator.voxelFreq;
			return (armory.renderpath.RenderPathCreator.voxelFrame % freq) / freq;
		}
		#end
		return null;
	}
}
