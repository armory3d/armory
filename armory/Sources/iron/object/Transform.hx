package iron.object;

import iron.math.Mat4;
import iron.math.Vec4;
import iron.math.Quat;

class Transform {
	/**
		The world matrix (read-only).
	**/
	public var world: Mat4;
	/**
		Prevent applying parent matrix.
	**/
	public var localOnly = false;
	/**
		The local matrix. If you modify this, call `decompose()` to update the
		`loc`, `rot` and `scale` fields, or `buildMatrix()` to update
		everything.
	**/
	public var local: Mat4;
	/**
		The local translation. Changes to this field should be applied by
		calling `buildMatrix()`.
	**/
	public var loc: Vec4;
	/**
		The local rotation. Changes to this field should be applied by
		calling `buildMatrix()`.
	**/
	public var rot: Quat;
	/**
		The local scale. Changes to this field should be applied by
		calling `buildMatrix()`.
	**/
	public var scale: Vec4;
	/**
		Uniform scale factor for `world` matrix.
	**/
	public var scaleWorld: kha.FastFloat = 1.0;
	/**
		The world matrix with `scaleWorld` applied (read-only).
	**/
	public var worldUnpack: Mat4;
	/**
		Flag to rebuild the `world` matrix on next update.
	**/
	public var dirty: Bool;
	/**
		The object that is effected by this transform.
	**/
	public var object: Object;
	/**
		The dimensions of the object in local space (without parent, prepended
		or appended matrices applied).
	**/
	public var dim: Vec4;
	/**
		The radius of the smallest sphere that encompasses the object in local
		space.
	**/
	public var radius: kha.FastFloat;

	static var temp = Mat4.identity();
	static var q = new Quat();

	var boneParent: Mat4 = null;
	var lastWorld: Mat4 = null;

	// Wrong order returned from getEuler(), store last state for animation
	var _eulerX: kha.FastFloat;
	var _eulerY: kha.FastFloat;
	var _eulerZ: kha.FastFloat;

	// Animated delta transform
	var dloc: Vec4 = null;
	var drot: Quat = null;
	var dscale: Vec4 = null;
	var _deulerX: kha.FastFloat;
	var _deulerY: kha.FastFloat;
	var _deulerZ: kha.FastFloat;

	public function new(object: Object) {
		this.object = object;
		reset();
	}

	/**
		Reset to a null transform: zero location and rotation, and a uniform
		scale of one. Other fields such as prepended matrices and bone parents
		will not be changed.
	**/
	public function reset() {
		world = Mat4.identity();
		worldUnpack = Mat4.identity();
		local = Mat4.identity();
		loc = new Vec4();
		rot = new Quat();
		scale = new Vec4(1.0, 1.0, 1.0);
		dim = new Vec4(2.0, 2.0, 2.0);
		radius = 1.0;
		dirty = true;
	}

	/**
		Rebuild the matrices, if needed.
	**/
	public function update() {
		if (dirty) buildMatrix();
	}

	function composeDelta() {
		// Delta transform
		dloc.addvecs(loc, dloc);
		dscale.addvecs(dscale, scale);
		drot.fromEuler(_deulerX, _deulerY, _deulerZ);
		drot.multquats(rot, drot);
		local.compose(dloc, drot, dscale);
	}

	/**
		Update the transform matrix based on `loc`, `rot`, and `scale`. If any
		change is made to `loc`, `rot`, or `scale` `buildMatrix()` must be
		called to update the objects transform.
	**/
	public function buildMatrix() {
		dloc == null ? local.compose(loc, rot, scale) : composeDelta();

		if (boneParent != null) local.multmats(boneParent, local);

		if (object.parent != null && !localOnly) {
			world.multmats3x4(local, object.parent.transform.world);
		}
		else {
			world.setFrom(local);
		}

		worldUnpack.setFrom(world);
		if (scaleWorld != 1.0) {
			worldUnpack._00 *= scaleWorld;
			worldUnpack._01 *= scaleWorld;
			worldUnpack._02 *= scaleWorld;
			worldUnpack._03 *= scaleWorld;
			worldUnpack._10 *= scaleWorld;
			worldUnpack._11 *= scaleWorld;
			worldUnpack._12 *= scaleWorld;
			worldUnpack._13 *= scaleWorld;
			worldUnpack._20 *= scaleWorld;
			worldUnpack._21 *= scaleWorld;
			worldUnpack._22 *= scaleWorld;
			worldUnpack._23 *= scaleWorld;
		}

		// Constraints
		if (object.constraints != null) for (c in object.constraints) c.apply(this);

		computeDim();

		// Update children
		for (n in object.children) {
			n.transform.buildMatrix();
		}

		dirty = false;
	}

	/**
		Move the game Object by the defined amount relative to its current location.
		@param	x Amount to move on the local x axis.
		@param	y Amount to move on the local y axis.
		@param	z Amount to move on the local z axis.
	**/
	public function translate(x: kha.FastFloat, y: kha.FastFloat, z: kha.FastFloat) {
		loc.x += x;
		loc.y += y;
		loc.z += z;
		buildMatrix();
	}

	/**
		Set the local matrix and update `loc`, `rot`, `scale` and `world`.
		@param	mat The new local matrix.
	**/
	public function setMatrix(mat: Mat4) {
		local.setFrom(mat);
		decompose();
		buildMatrix();
	}

	/**
		Apply another transform to this one, i.e. multiply this transform's
		local matrix by another.
		@param	mat The other transform to apply.
	**/
	public function multMatrix(mat: Mat4) {
		local.multmat(mat);
		decompose();
		buildMatrix();
	}

	/**
		Update the `loc`, `rot` and `scale` fields according to the local
		matrix. You may need to call this after directly mutating the local
		matrix.
	**/
	public function decompose() {
		local.decompose(loc, rot, scale);
	}

	/**
		Rotate around an axis.
		@param	axis The axis to rotate around.
		@param	f The magnitude of the rotation in radians.
	**/
	public function rotate(axis: Vec4, f: kha.FastFloat) {
		q.fromAxisAngle(axis, f);
		rot.multquats(q, rot);
		buildMatrix();
	}

	/**
		Apply a scaled translation in local space.
		@param	axis The direction to move.
		@param	f A multiplier for the movement. If `axis` is a unit
	  			vector, then this is the distance to move.
	**/
	public function move(axis: Vec4, f = 1.0) {
		loc.addf(axis.x * f, axis.y * f, axis.z * f);
		buildMatrix();
	}

	/**
		Set the rotation of the object in radians.
		@param	x Set the x axis rotation in radians.
		@param	y Set the y axis rotation in radians.
		@param	z Set the z axis rotation in radians.
	**/
	public function setRotation(x: kha.FastFloat, y: kha.FastFloat, z: kha.FastFloat) {
		rot.fromEuler(x, y, z);
		_eulerX = x;
		_eulerY = y;
		_eulerZ = z;
		dirty = true;
	}

	function computeRadius() {
		radius = Math.sqrt(dim.x * dim.x + dim.y * dim.y + dim.z * dim.z);
	}

	function computeDim() {
		if (object.raw == null) {
			computeRadius();
			return;
		}
		var d = object.raw.dimensions;
		if (d == null) dim.set(2 * scale.x, 2 * scale.y, 2 * scale.z);
		else dim.set(d[0] * scale.x, d[1] * scale.y, d[2] * scale.z);
		computeRadius();
	}

	public function applyParentInverse() {
		var pt = object.parent.transform;
		pt.buildMatrix();
		temp.getInverse(pt.local);
		this.local.multmat(temp);
		this.decompose();
		this.buildMatrix();
	}

	public function applyParent() {
		var pt = object.parent.transform;
		pt.buildMatrix();
		this.local.multmat(pt.local);
		this.decompose();
		this.buildMatrix();
	}

	/**
		Check whether the transform has changed at all since the last time
		this function was called.
		@return	`true` if the transform has changed.
	**/
	public function diff(): Bool {
		if (lastWorld == null) {
			lastWorld = Mat4.identity().setFrom(world);
			return false;
		}
		var a = world;
		var b = lastWorld;
		var r = a._00 != b._00 || a._01 != b._01 || a._02 != b._02 || a._03 != b._03 ||
				a._10 != b._10 || a._11 != b._11 || a._12 != b._12 || a._13 != b._13 ||
				a._20 != b._20 || a._21 != b._21 || a._22 != b._22 || a._23 != b._23 ||
				a._30 != b._30 || a._31 != b._31 || a._32 != b._32 || a._33 != b._33;
		if (r) lastWorld.setFrom(world);
		return r;
	}

	/**
		@return	The look vector (positive local y axis) in world space.
	**/
	public inline function look(): Vec4 {
		return world.look();
	}

	/**
		@return	The right vector (positive local x axis) in world space.
	**/
	public inline function right(): Vec4 {
		return world.right();
	}

	/**
		@return	The up vector (positive local z axis) in world space.
	**/
	public inline function up(): Vec4 {
		return world.up();
	}

	/**
		@return The world x location.
	**/
	public inline function worldx(): kha.FastFloat {
		return world._30;
	}

	/**
		@return The world y location.
	**/
	public inline function worldy(): kha.FastFloat {
		return world._31;
	}

	/**
		@return The world z location.
	**/
	public inline function worldz(): kha.FastFloat {
		return world._32;
	}
}
