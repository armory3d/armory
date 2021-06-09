package armory.trait.internal;

import haxe.ds.Map;
import iron.math.Vec4;
import iron.data.MaterialData;
import iron.Scene;
import iron.object.Object;
import iron.object.Uniforms;


class UniformsManager{

    static var floatsRegistered = false;
    static var floatsMap = new Map<Object, Map<MaterialData, Map<String, Null<kha.FastFloat>>>>();

    static var vectorsRegistered = false;
    static var vectorsMap = new Map<Object, Map<MaterialData, Map<String, Vec4>>>();

    static var texturesRegistered = false;
	static var texturesMap = new Map<Object, Map<MaterialData, Map<String, kha.Image>>>();

    public function new(type: UniformType){
        switch (type){
            case Float:{
                if(! floatsRegistered){
                    floatsRegistered = true;
                    Uniforms.externalFloatLinks.push(floatLink);
                }
            }

            case Vector:{
                if(! vectorsRegistered){
                    vectorsRegistered = true;
                    Uniforms.externalVec3Links.push(vec3Link);
                }
            }

            case Texture:{
                if(! texturesRegistered){
                    texturesRegistered = true;
                    Uniforms.externalTextureLinks.push(textureLink);
                }
            }
        }
    }

    public function setFloatValue(material: MaterialData, object: Object, link: String, value: Null<kha.FastFloat>){
        
        var map = floatsMap;

        var matMap = map.get(object);
        if (matMap == null) {
			matMap = new Map();
			map.set(object, matMap);
		}

		var entry = matMap.get(material);
		if (entry == null) {
			entry = new Map();
			matMap.set(material, entry);
		}

		entry.set(link, value); // parameter name, value
    }

    public function setVec3Value(material: MaterialData, object: Object, link: String, value: Vec4){
        
        var map = vectorsMap;

        var matMap = map.get(object);
        if (matMap == null) {
			matMap = new Map();
			map.set(object, matMap);
		}

		var entry = matMap.get(material);
		if (entry == null) {
			entry = new Map();
			matMap.set(material, entry);
		}

		entry.set(link, value); // parameter name, value
    }

    public function setTextureValue(material: MaterialData, object: Object, link: String, value: kha.Image){
        
        var map = texturesMap;

        var matMap = map.get(object);
        if (matMap == null) {
			matMap = new Map();
			map.set(object, matMap);
		}

		var entry = matMap.get(material);
		if (entry == null) {
			entry = new Map();
			matMap.set(material, entry);
		}

		entry.set(link, value); // parameter name, value
    }

    static function floatLink(object: Object, mat: MaterialData, link: String): Null<kha.FastFloat> {
		if(object == null) return null;
		if (mat == null) return null;

		if(! floatsMap.exists(object)){
			object = Scene.active.root;
		}

		var material = floatsMap.get(object);
		if (material == null) return null;

		var entry = material.get(mat);
		if (entry == null) return null;

		return entry.get(link);
	}

    static function vec3Link(object: Object, mat: MaterialData, link: String): iron.math.Vec4 {
		if(object == null) return null;
		if (mat == null) return null;

        if(! vectorsMap.exists(object)){
			object = Scene.active.root;
		}

        var material = vectorsMap.get(object);
		if (material == null) return null;

		var entry = material.get(mat);
		if (entry == null) return null;

		return entry.get(link);
	}

    static function textureLink(object: Object, mat: MaterialData, link: String): kha.Image {
		if(object == null) return null;
		if (mat == null) return null;

        if(! texturesMap.exists(object)){
			object = Scene.active.root;
		}

        var material = texturesMap.get(object);
		if (material == null) return null;

		var entry = material.get(mat);
		if (entry == null) return null;

		return entry.get(link);
	}
}

@:enum abstract UniformType(Int) from Int to Int {
	var Float = 0;
	var Vector = 1;
	var Texture = 2;
}