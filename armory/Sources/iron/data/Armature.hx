package iron.data;

#if arm_skin

import iron.data.SceneFormat;
import iron.math.Mat4;

class Armature {
	public var uid: Int;
	public var name: String;
	public var actions: Array<TAction> = [];
	var matsReady = false;

	public function new(uid: Int, name: String, actions: Array<TSceneFormat>) {
		this.uid = uid;
		this.name = name;

		for (a in actions) {
			for (o in a.objects) setParents(o);
			var bones: Array<TObj> = [];
			traverseBones(a.objects, function(object: TObj) { bones.push(object); });
			this.actions.push({ name: a.name, bones: bones, mats: null });
		}
	}

	public function initMats() {
		if (matsReady) return;
		matsReady = true;

		for (a in actions) {
			if (a.mats != null) continue;
			a.mats = [];
			for (b in a.bones) {
				a.mats.push(Mat4.fromFloat32Array(b.transform.values));
			}
		}
	}

	public function getAction(name: String): TAction {
		for (a in actions) if (a.name == name) return a;
		return null;
	}

	static function setParents(object: TObj) {
		if (object.children == null) return;
		for (o in object.children) {
			o.parent = object;
			setParents(o);
		}
	}

	static function traverseBones(objects: Array<TObj>, callback: TObj->Void) {
		for (i in 0...objects.length) {
			traverseBonesStep(objects[i], callback);
		}
	}

	static function traverseBonesStep(object: TObj, callback: TObj->Void) {
		if (object.type == "bone_object") callback(object);
		if (object.children == null) return;
		for (i in 0...object.children.length) {
			traverseBonesStep(object.children[i], callback);
		}
	}
}

typedef TAction = {
	var name: String;
	var bones: Array<TObj>;
	var mats: Array<Mat4>;
}

#end
