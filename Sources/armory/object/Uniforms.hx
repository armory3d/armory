package armory.object;

import iron.Scene;
import iron.math.Vec4;

class Uniforms {

	public static function register() {
		iron.object.Uniforms.externalTextureLink = externalTextureLink;
		iron.object.Uniforms.externalVec3Link = externalVec3Link;
	}

	public static function externalTextureLink(tulink:String):kha.Image {
		if (tulink == "_smaaSearch") {
			return Scene.active.embedded.get('smaa_search.png');
		}
		else if (tulink == "_smaaArea") {
			return Scene.active.embedded.get('smaa_area.png');
		}
		else if (tulink == "_ltcMat") {
			if (armory.data.ConstData.ltcMatTex == null) armory.data.ConstData.initLTC();
			return armory.data.ConstData.ltcMatTex;
		}
		else if (tulink == "_ltcMag") {
			if (armory.data.ConstData.ltcMagTex == null) armory.data.ConstData.initLTC();
			return armory.data.ConstData.ltcMagTex;
		}
		return null;
	}

	public static function externalVec3Link(clink:String):iron.math.Vec4 {
		var v:Vec4 = null;
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
		return v;
	}
}
