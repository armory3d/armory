package iron.object;

import iron.Trait;
import iron.data.SceneFormat;
import iron.math.Vec4;
#if arm_target_n64
import iron.n64.N64Bridge;
#end

class Object {
	static var uidCounter = 0;
	public var uid: Int;
	public var urandom: Float;
	public var raw: TObj = null;

	public var name: String = "";
	public var transform: Transform;
	public var constraints: Array<Constraint> = null;
	public var traits: Array<Trait> = [];

	public var parent: Object = null;
	public var children: Array<Object> = [];
	public var lods: Array<Object> = null;

	public var animation: Animation = null;
	#if !arm_target_n64
	public var visible = true; // Skip render, keep updating
	#end
	public var visibleMesh = true;
	public var visibleShadow = true;
	public var culled = false; // Object was culled last frame
	public var culledMesh = false;
	public var culledShadow = false;
	public var vertex_groups: Map<String, Array<Vec4>> = null;
	public var properties: Map<String, Dynamic> = null;
	var isEmpty = false;

	#if arm_target_n64
	@:isVar public var visible(get, set): Bool = true;

	inline function get_visible(): Bool {
		N64Bridge.object.getVisible(this);
		return visible;
	}

	inline function set_visible(value: Bool): Bool {
		N64Bridge.object.setVisible(this, value);
		return this.visible = value;
	}
	#end

	public function new() {
		uid = uidCounter++;
		urandom = seededRandom(); // Math.random();
		transform = new Transform(this);
		isEmpty = Type.getClass(this) == Object;
		if (isEmpty && Scene.active != null) Scene.active.empties.push(this);
	}

	/**
		Set the given `parentObject` as the parent of this object.

		If `parentObject` is `null`, the object is parented to the scene's
		`sceneParent`, which is the topmost object of the scene tree.
		If you want to remove it from the scene, use `Object.remove()` instead.

		If `parentObject` is the object on which this function is called,
		nothing happens.

		@param parentObject The new parent object.
		@param parentInverse (Optional) Change the scale of the child object to be relative to the new parents 3D space or use the original scale.
		@param keepTransform (Optional) When unparenting from the old parent, keep the transform given by the old parent or revert to the object's default.
	**/
	public function setParent(parentObject: Object, parentInverse = false, keepTransform = false) {
		if (parentObject == this || parentObject == parent) return;

		if (parent != null) {
			parent.children.remove(this);
			if (keepTransform) this.transform.applyParent();
			this.parent = null; // rebuild matrix without a parent
			this.transform.buildMatrix();
		}

		if (parentObject == null) {
			parentObject = Scene.active.sceneParent;
		}
		parent = parentObject;
		parent.children.push(this);
		if (parentInverse) this.transform.applyParentInverse();
	}

	/**
		Add a game Object as a child of this game Object.
		@param	o The game Object instance to be added as a child.
		@param	parentInverse Optional (default false) change the scale of the child object to be relative to the parents 3D space or use the original scale.
	**/
	@:deprecated("addChild() is deprecated, please use setParent() instead")
	public inline function addChild(o: Object, parentInverse = false) {
		o.setParent(this, parentInverse, false);
	}

	/**
		Remove a child game Object from it's parentage. Does not remove the object from the scene.
		@param	o The game Object instance to be removed.
		@param	keepTransform Optional (defaut false) keep the transform given by the parent or revert to the objects default.
	**/
	@:deprecated("removeChild() is deprecated, please use setParent(null) instead")
	public inline function removeChild(o: Object, keepTransform = false) {
		o.setParent(null, false, keepTransform);
	}

	/**
		Removes the game object from the scene.
	**/
	public function remove() {
		if (isEmpty && Scene.active != null) Scene.active.empties.remove(this);
		if (animation != null) animation.remove();
		while (children.length > 0) children[0].remove();
		while (traits.length > 0) traits[0].remove();
		if (parent != null) {
			parent.children.remove(this);
			parent = null;
		}
	}

	/**
		Get a child game Object of this game Object. Using the childs name property as a lookup.
		@param	name A string matching the name property of the game Object to fetch.
		@return	Object or null
	**/
	public function getChild(name: String): Object {
		if (this.name == name) return this;
		else {
			for (c in children) {
				var r = c.getChild(name);
				if (r != null) return r;
			}
		}
		return null;
	}

	/**
		Returns the children of the object.

		If 'recursive' is set to `false`, only direct children will be included
		in the returned array. If `recursive` is `true`, children of children and
		so on will be included too.

		@param recursive = false Include children of children
		@return `Array<Object>`
	**/
	public function getChildren(?recursive = false): Array<Object> {
		if (!recursive) return children;

		var retChildren = children.copy();
		for (child in children) {
			retChildren = retChildren.concat(child.getChildren(recursive));
		}
		return retChildren;
	}

	public function getChildOfType<T: Object>(type: Class<T>): T {
		if (Std.isOfType(this, type)) return cast this;
		else {
			for (c in children) {
				var r = c.getChildOfType(type);
				if (r != null) return r;
			}
		}
		return null;
	}

	@:access(iron.Trait)
	public function addTrait(t: Trait) {
		traits.push(t);
		t.object = this;

		if (t._add != null) {
			for (f in t._add) f();
			t._add = null;
		}
	}

	/**
		Remove the Trait from the Object.
		@param	t The Trait to be removed from the game Object.
	**/
	@:access(iron.Trait)
	public function removeTrait(t: Trait) {
		if (t._init != null) {
			for (f in t._init) App.removeInit(f);
			t._init = null;
		}
		if (t._fixedUpdate != null) {
			for (f in t._fixedUpdate) App.removeFixedUpdate(f);
			t._fixedUpdate = null;
		}
		if (t._update != null) {
			for (f in t._update) App.removeUpdate(f);
			t._update = null;
		}
		if (t._lateUpdate != null) {
			for (f in t._lateUpdate) App.removeLateUpdate(f);
			t._lateUpdate = null;
		}
		if (t._render != null) {
			for (f in t._render) App.removeRender(f);
			t._render = null;
		}
		if (t._render2D != null) {
			for (f in t._render2D) App.removeRender2D(f);
			t._render2D = null;
		}
		if (t._remove != null) {
			for (f in t._remove) f();
			t._remove = null;
		}
		traits.remove(t);
	}

	/**
		Get the Trait instance that is attached to this game Object.
		@param	c The class of type Trait to attempt to retrieve.
		@return	Trait or null
	**/
	public function getTrait<T: Trait>(c: Class<T>): T {
		for (t in traits) if (Type.getClass(t) == cast c) return cast t;
		return null;
	}

	#if arm_skin
	public function getParentArmature(name: String): BoneAnimation {
		for (a in Scene.active.animations) if (a.armature != null && a.armature.name == name) return cast a;
		return null;
	}
	#else
	public function getParentArmature(name: String): Animation {
		return null;
	}
	#end

	public function setupAnimation(oactions: Array<TSceneFormat> = null) {
		// Parented to bone
		#if arm_skin
		if (raw.parent_bone != null) {
			Scene.active.notifyOnInit(function() {
				var banim = getParentArmature(parent.name);
				if (banim != null) banim.addBoneChild(raw.parent_bone, this);
			});
		}
		#end
		// Object actions
		if (oactions == null) return;
		animation = new ObjectAnimation(this, oactions);
	}

	#if arm_morph_target
	public function setupMorphTargets() {}
	#end

	static var seed = 1; // cpp / js not consistent
	static function seededRandom(): Float {
		seed = (seed * 9301 + 49297) % 233280;
		return seed / 233280.0;
	}
}
