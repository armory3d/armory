package armory.object;

import iron.Scene;
import iron.math.Vec4;

// Structure for setting shader uniforms
class Uniforms {

	public static function register() {
		iron.object.Uniforms.externalTextureLinks = [externalTextureLink];
		iron.object.Uniforms.externalVec3Links = [externalVec3Link];
		iron.object.Uniforms.externalFloatLinks = [externalFloatLink];
	}

	public static function externalTextureLink(tulink:String):kha.Image {
		if (tulink == "_smaaSearch") {
			return Scene.active.embedded.get('smaa_search.png');
		}
		else if (tulink == "_smaaArea") {
			return Scene.active.embedded.get('smaa_area.png');
		}
		#if arm_ltc
		else if (tulink == "_ltcMat") {
			if (armory.data.ConstData.ltcMatTex == null) armory.data.ConstData.initLTC();
			return armory.data.ConstData.ltcMatTex;
		}
		else if (tulink == "_ltcMag") {
			if (armory.data.ConstData.ltcMagTex == null) armory.data.ConstData.initLTC();
			return armory.data.ConstData.ltcMagTex;
		}
		#end
		else if (tulink == "_lensTexture") {
			return Scene.active.embedded.get('lenstexture.jpg');
		}
		else if (tulink == "_lutTexture") {
			return Scene.active.embedded.get('luttexture.jpg');
		}
		else if (tulink == "_cloudsTexture") {
			return Scene.active.embedded.get('cloudstexture.png');
		}
		return null;
	}

	public static function externalVec3Link(clink:String):iron.math.Vec4 {
		var v:Vec4 = null;
		#if arm_hosek
		if (clink == "_hosekA") {
			if (armory.renderpath.HosekWilkie.data == null) {
				armory.renderpath.HosekWilkie.init(Scene.active.world);
			}
			v = iron.object.Uniforms.helpVec;
			v.x = armory.renderpath.HosekWilkie.data.A.x;
			v.y = armory.renderpath.HosekWilkie.data.A.y;
			v.z = armory.renderpath.HosekWilkie.data.A.z;
		}
		else if (clink == "_hosekB") {
			if (armory.renderpath.HosekWilkie.data == null) {
				armory.renderpath.HosekWilkie.init(Scene.active.world);
			}
			v = iron.object.Uniforms.helpVec;
			v.x = armory.renderpath.HosekWilkie.data.B.x;
			v.y = armory.renderpath.HosekWilkie.data.B.y;
			v.z = armory.renderpath.HosekWilkie.data.B.z;
		}
		else if (clink == "_hosekC") {
			if (armory.renderpath.HosekWilkie.data == null) {
				armory.renderpath.HosekWilkie.init(Scene.active.world);
			}
			v = iron.object.Uniforms.helpVec;
			v.x = armory.renderpath.HosekWilkie.data.C.x;
			v.y = armory.renderpath.HosekWilkie.data.C.y;
			v.z = armory.renderpath.HosekWilkie.data.C.z;
		}
		else if (clink == "_hosekD") {
			if (armory.renderpath.HosekWilkie.data == null) {
				armory.renderpath.HosekWilkie.init(Scene.active.world);
			}
			v = iron.object.Uniforms.helpVec;
			v.x = armory.renderpath.HosekWilkie.data.D.x;
			v.y = armory.renderpath.HosekWilkie.data.D.y;
			v.z = armory.renderpath.HosekWilkie.data.D.z;
		}
		else if (clink == "_hosekE") {
			if (armory.renderpath.HosekWilkie.data == null) {
				armory.renderpath.HosekWilkie.init(Scene.active.world);
			}
			v = iron.object.Uniforms.helpVec;
			v.x = armory.renderpath.HosekWilkie.data.E.x;
			v.y = armory.renderpath.HosekWilkie.data.E.y;
			v.z = armory.renderpath.HosekWilkie.data.E.z;
		}
		else if (clink == "_hosekF") {
			if (armory.renderpath.HosekWilkie.data == null) {
				armory.renderpath.HosekWilkie.init(Scene.active.world);
			}
			v = iron.object.Uniforms.helpVec;
			v.x = armory.renderpath.HosekWilkie.data.F.x;
			v.y = armory.renderpath.HosekWilkie.data.F.y;
			v.z = armory.renderpath.HosekWilkie.data.F.z;
		}
		else if (clink == "_hosekG") {
			if (armory.renderpath.HosekWilkie.data == null) {
				armory.renderpath.HosekWilkie.init(Scene.active.world);
			}
			v = iron.object.Uniforms.helpVec;
			v.x = armory.renderpath.HosekWilkie.data.G.x;
			v.y = armory.renderpath.HosekWilkie.data.G.y;
			v.z = armory.renderpath.HosekWilkie.data.G.z;
		}
		else if (clink == "_hosekH") {
			if (armory.renderpath.HosekWilkie.data == null) {
				armory.renderpath.HosekWilkie.init(Scene.active.world);
			}
			v = iron.object.Uniforms.helpVec;
			v.x = armory.renderpath.HosekWilkie.data.H.x;
			v.y = armory.renderpath.HosekWilkie.data.H.y;
			v.z = armory.renderpath.HosekWilkie.data.H.z;
		}
		else if (clink == "_hosekI") {
			if (armory.renderpath.HosekWilkie.data == null) {
				armory.renderpath.HosekWilkie.init(Scene.active.world);
			}
			v = iron.object.Uniforms.helpVec;
			v.x = armory.renderpath.HosekWilkie.data.I.x;
			v.y = armory.renderpath.HosekWilkie.data.I.y;
			v.z = armory.renderpath.HosekWilkie.data.I.z;
		}
		else if (clink == "_hosekZ") {
			if (armory.renderpath.HosekWilkie.data == null) {
				armory.renderpath.HosekWilkie.init(Scene.active.world);
			}
			v = iron.object.Uniforms.helpVec;
			v.x = armory.renderpath.HosekWilkie.data.Z.x;
			v.y = armory.renderpath.HosekWilkie.data.Z.y;
			v.z = armory.renderpath.HosekWilkie.data.Z.z;
		}
		#end
		return v;
	}

	public static function externalFloatLink(clink:String):Float {
		if (clink == "_dynamicScale") {
			return armory.renderpath.DynamicResolutionScale.dynamicScale;
		}
		return 0.0;
	}
}
