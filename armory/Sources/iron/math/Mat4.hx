package iron.math;

import kha.FastFloat;

class Mat4 {

	public var self: kha.math.FastMatrix4;
	static var helpVec = new Vec4();
	static var helpMat = Mat4.identity();

	public inline function new(_00: FastFloat, _10: FastFloat, _20: FastFloat, _30: FastFloat,
							   _01: FastFloat, _11: FastFloat, _21: FastFloat, _31: FastFloat,
							   _02: FastFloat, _12: FastFloat, _22: FastFloat, _32: FastFloat,
							   _03: FastFloat, _13: FastFloat, _23: FastFloat, _33: FastFloat) {
		self = new kha.math.FastMatrix4(_00, _10, _20, _30, _01, _11, _21, _31, _02, _12, _22, _32, _03, _13, _23, _33);
	}

	/**
		Set the transform from a location, rotation and scale.
		@param	loc The location to use.
		@param	quat The rotation to use.
		@param	sc The scale to use.
		@return	This matrix.
	**/
	public inline function compose(loc: Vec4, quat: Quat, sc: Vec4): Mat4 {
		fromQuat(quat);
		scale(sc);
		setLoc(loc);
		return this;
	}

	/**
		Decompose this matrix into its location, rotation and scale components.
		Additional transforms (skew, projection) will be ignored.
		@param	loc A vector to write the location to.
		@param	quat A quaternion to write the rotation to.
		@param	scale A vector to write the scale to.
		@return	This matrix.
	**/
	public inline function decompose(loc: Vec4, quat: Quat, scale: Vec4): Mat4 {
		loc.x = _30; loc.y = _31; loc.z = _32;
		scale.x = helpVec.set(_00, _01, _02).length();
		scale.y = helpVec.set(_10, _11, _12).length();
		scale.z = helpVec.set(_20, _21, _22).length();
		if (self.determinant() < 0.0) scale.x = -scale.x;
		var invs = 1.0 / scale.x; // Scale the rotation part
		helpMat._00 = _00 * invs;
		helpMat._01 = _01 * invs;
		helpMat._02 = _02 * invs;
		invs = 1.0 / scale.y;
		helpMat._10 = _10 * invs;
		helpMat._11 = _11 * invs;
		helpMat._12 = _12 * invs;
		invs = 1.0 / scale.z;
		helpMat._20 = _20 * invs;
		helpMat._21 = _21 * invs;
		helpMat._22 = _22 * invs;
		quat.fromRotationMat(helpMat);
		return this;
	}

	/**
		Set the location component of this matrix.
		@param	v The location to use.
		@return	This matrix.
	**/
	public inline function setLoc(v: Vec4): Mat4 {
		_30 = v.x;
		_31 = v.y;
		_32 = v.z;
		return this;
	}

	/**
		Set the transform to a rotation from a quaternion. Other existing
		transforms will be removed.
		@param	q The rotation to use.
		@return	This matrix.
	**/
	public inline function fromQuat(q: Quat): Mat4 {
		var x = q.x; var y = q.y; var z = q.z; var w = q.w;
		var x2 = x + x; var y2 = y + y; var z2 = z + z;
		var xx = x * x2; var xy = x * y2; var xz = x * z2;
		var yy = y * y2; var yz = y * z2; var zz = z * z2;
		var wx = w * x2; var wy = w * y2; var wz = w * z2;

		_00 = 1.0 - (yy + zz);
		_10 = xy - wz;
		_20 = xz + wy;

		_01 = xy + wz;
		_11 = 1.0 - (xx + zz);
		_21 = yz - wx;

		_02 = xz - wy;
		_12 = yz + wx;
		_22 = 1.0 - (xx + yy);

		_03 = 0.0;
		_13 = 0.0;
		_23 = 0.0;
		_30 = 0.0;
		_31 = 0.0;
		_32 = 0.0;
		_33 = 1.0;

		return this;
	}

	/**
		Set all components of this matrix from an array.
		@param	a The 16-component array to use. Components should be in the
				same order as for `Mat4.new()`.
		@param	offset An offset index to the start of the data in the array.
				Defaults to 0.
		@return	A new matrix.
	**/
	public static inline function fromFloat32Array(a: kha.arrays.Float32Array, offset = 0): Mat4 {
		return new Mat4(
			a[0 + offset], a[1 + offset], a[2 + offset], a[3 + offset],
			a[4 + offset], a[5 + offset], a[6 + offset], a[7 + offset],
			a[8 + offset], a[9 + offset], a[10 + offset], a[11 + offset],
			a[12 + offset], a[13 + offset], a[14 + offset], a[15 + offset]
		);
	}

	/**
		Create a matrix that represents no transform - located at the origin,
		zero rotation, and a uniform scale of 1.
		@return	A new matrix.
	**/
	public static inline function identity(): Mat4 {
		return new Mat4(
			1.0, 0.0, 0.0, 0.0,
			0.0, 1.0, 0.0, 0.0,
			0.0, 0.0, 1.0, 0.0,
			0.0, 0.0, 0.0, 1.0
		);
	}

	/**
		Set this matrix to the identity (see `identity()`).
		@return	This matrix.
	**/
	public inline function setIdentity(): Mat4 {
		_00 = 1.0; _01 = 0.0; _02 = 0.0; _03 = 0.0;
		_10 = 0.0; _11 = 1.0; _12 = 0.0; _13 = 0.0;
		_20 = 0.0; _21 = 0.0; _22 = 1.0; _23 = 0.0;
		_30 = 0.0; _31 = 0.0; _32 = 0.0; _33 = 1.0;
		return this;
	}

	/**
		Reset this matrix to the identity and set its location.
		@param	x The x location.
		@param	y The y location.
		@param	z The z location.
		@return	This matrix.
	**/
	public inline function initTranslate(x: FastFloat = 0.0, y: FastFloat = 0.0, z: FastFloat = 0.0): Mat4 {
		_00 = 1.0; _01 = 0.0; _02 = 0.0; _03 = 0.0;
		_10 = 0.0; _11 = 1.0; _12 = 0.0; _13 = 0.0;
		_20 = 0.0; _21 = 0.0; _22 = 1.0; _23 = 0.0;
		_30 = x;   _31 = y;   _32 = z;   _33 = 1.0;
		return this;
	}

	/**
		Apply an additional translation to this matrix.
		@param	x The distance to move in the x direction.
		@param	y The distance to move in the x direction.
		@param	z The distance to move in the x direction.
		@return	This matrix
	**/
	public inline function translate(x: FastFloat, y: FastFloat, z: FastFloat): Mat4 {
		_00 += x * _03; _01 += y * _03; _02 += z * _03;
		_10 += x * _13; _11 += y * _13; _12 += z * _13;
		_20 += x * _23; _21 += y * _23; _22 += z * _23;
		_30 += x * _33; _31 += y * _33; _32 += z * _33;
		return this;
	}

	/**
		Apply an additional scale to this matrix.
		@param	v The vector to scale by.
		@return	This matrix.
	**/
	public inline function scale(v: Vec4): Mat4 {
		var x = v.x; var y = v.y; var z = v.z;
		_00 *= x;
		_01 *= x;
		_02 *= x;
		_03 *= x;
		_10 *= y;
		_11 *= y;
		_12 *= y;
		_13 *= y;
		_20 *= z;
		_21 *= z;
		_22 *= z;
		_23 *= z;
		return this;
	}

	public inline function multmats3x4(a: Mat4, b: Mat4): Mat4 {
		var a00 = a._00; var a01 = a._01; var a02 = a._02; var a03 = a._03;
		var a10 = a._10; var a11 = a._11; var a12 = a._12; var a13 = a._13;
		var a20 = a._20; var a21 = a._21; var a22 = a._22; var a23 = a._23;
		var a30 = a._30; var a31 = a._31; var a32 = a._32; var a33 = a._33;

		var b0 = b._00; var b1 = b._10; var b2 = b._20; var b3 = b._30;
		_00 = a00 * b0 + a01 * b1 + a02 * b2 + a03 * b3;
		_10 = a10 * b0 + a11 * b1 + a12 * b2 + a13 * b3;
		_20 = a20 * b0 + a21 * b1 + a22 * b2 + a23 * b3;
		_30 = a30 * b0 + a31 * b1 + a32 * b2 + a33 * b3;

		b0 = b._01; b1 = b._11; b2 = b._21; b3 = b._31;
		_01 = a00 * b0 + a01 * b1 + a02 * b2 + a03 * b3;
		_11 = a10 * b0 + a11 * b1 + a12 * b2 + a13 * b3;
		_21 = a20 * b0 + a21 * b1 + a22 * b2 + a23 * b3;
		_31 = a30 * b0 + a31 * b1 + a32 * b2 + a33 * b3;

		b0 = b._02; b1 = b._12; b2 = b._22; b3 = b._32;
		_02 = a00 * b0 + a01 * b1 + a02 * b2 + a03 * b3;
		_12 = a10 * b0 + a11 * b1 + a12 * b2 + a13 * b3;
		_22 = a20 * b0 + a21 * b1 + a22 * b2 + a23 * b3;
		_32 = a30 * b0 + a31 * b1 + a32 * b2 + a33 * b3;

		_03 = 0;
		_13 = 0;
		_23 = 0;
		_33 = 1;
		return this;
	}

	public inline function multmats(b: Mat4, a: Mat4): Mat4 {
		var a00 = a._00; var a01 = a._01; var a02 = a._02; var a03 = a._03;
		var a10 = a._10; var a11 = a._11; var a12 = a._12; var a13 = a._13;
		var a20 = a._20; var a21 = a._21; var a22 = a._22; var a23 = a._23;
		var a30 = a._30; var a31 = a._31; var a32 = a._32; var a33 = a._33;

		var b0 = b._00; var b1 = b._10; var b2 = b._20; var b3 = b._30;
		_00 = a00 * b0 + a01 * b1 + a02 * b2 + a03 * b3;
		_10 = a10 * b0 + a11 * b1 + a12 * b2 + a13 * b3;
		_20 = a20 * b0 + a21 * b1 + a22 * b2 + a23 * b3;
		_30 = a30 * b0 + a31 * b1 + a32 * b2 + a33 * b3;

		b0 = b._01; b1 = b._11; b2 = b._21; b3 = b._31;
		_01 = a00 * b0 + a01 * b1 + a02 * b2 + a03 * b3;
		_11 = a10 * b0 + a11 * b1 + a12 * b2 + a13 * b3;
		_21 = a20 * b0 + a21 * b1 + a22 * b2 + a23 * b3;
		_31 = a30 * b0 + a31 * b1 + a32 * b2 + a33 * b3;

		b0 = b._02; b1 = b._12; b2 = b._22; b3 = b._32;
		_02 = a00 * b0 + a01 * b1 + a02 * b2 + a03 * b3;
		_12 = a10 * b0 + a11 * b1 + a12 * b2 + a13 * b3;
		_22 = a20 * b0 + a21 * b1 + a22 * b2 + a23 * b3;
		_32 = a30 * b0 + a31 * b1 + a32 * b2 + a33 * b3;

		b0 = b._03; b1 = b._13; b2 = b._23; b3 = b._33;
		_03 = a00 * b0 + a01 * b1 + a02 * b2 + a03 * b3;
		_13 = a10 * b0 + a11 * b1 + a12 * b2 + a13 * b3;
		_23 = a20 * b0 + a21 * b1 + a22 * b2 + a23 * b3;
		_33 = a30 * b0 + a31 * b1 + a32 * b2 + a33 * b3;

		return this;
	}

	public inline function multmat(m: Mat4): Mat4 {
		var a00 = _00; var a01 = _01; var a02 = _02; var a03 = _03;
		var a10 = _10; var a11 = _11; var a12 = _12; var a13 = _13;
		var a20 = _20; var a21 = _21; var a22 = _22; var a23 = _23;
		var a30 = _30; var a31 = _31; var a32 = _32; var a33 = _33;

		var b0 = m._00; var b1 = m._10; var b2 = m._20; var b3 = m._30;
		_00 = a00 * b0 + a01 * b1 + a02 * b2 + a03 * b3;
		_10 = a10 * b0 + a11 * b1 + a12 * b2 + a13 * b3;
		_20 = a20 * b0 + a21 * b1 + a22 * b2 + a23 * b3;
		_30 = a30 * b0 + a31 * b1 + a32 * b2 + a33 * b3;

		b0 = m._01; b1 = m._11; b2 = m._21; b3 = m._31;
		_01 = a00 * b0 + a01 * b1 + a02 * b2 + a03 * b3;
		_11 = a10 * b0 + a11 * b1 + a12 * b2 + a13 * b3;
		_21 = a20 * b0 + a21 * b1 + a22 * b2 + a23 * b3;
		_31 = a30 * b0 + a31 * b1 + a32 * b2 + a33 * b3;

		b0 = m._02; b1 = m._12; b2 = m._22; b3 = m._32;
		_02 = a00 * b0 + a01 * b1 + a02 * b2 + a03 * b3;
		_12 = a10 * b0 + a11 * b1 + a12 * b2 + a13 * b3;
		_22 = a20 * b0 + a21 * b1 + a22 * b2 + a23 * b3;
		_32 = a30 * b0 + a31 * b1 + a32 * b2 + a33 * b3;

		b0 = m._03; b1 = m._13; b2 = m._23; b3 = m._33;
		_03 = a00 * b0 + a01 * b1 + a02 * b2 + a03 * b3;
		_13 = a10 * b0 + a11 * b1 + a12 * b2 + a13 * b3;
		_23 = a20 * b0 + a21 * b1 + a22 * b2 + a23 * b3;
		_33 = a30 * b0 + a31 * b1 + a32 * b2 + a33 * b3;

		return this;
	}

	/**
		Invert a matrix and store the result in this one.
		@param	m The matrix to invert.
		@return	This matrix.
	**/
	public inline function getInverse(m: Mat4): Mat4 {
		var a00 = m._00; var a01 = m._01; var a02 = m._02; var a03 = m._03;
		var a10 = m._10; var a11 = m._11; var a12 = m._12; var a13 = m._13;
		var a20 = m._20; var a21 = m._21; var a22 = m._22; var a23 = m._23;
		var a30 = m._30; var a31 = m._31; var a32 = m._32; var a33 = m._33;
		var b00 = a00 * a11 - a01 * a10;
		var b01 = a00 * a12 - a02 * a10;
		var b02 = a00 * a13 - a03 * a10;
		var b03 = a01 * a12 - a02 * a11;
		var b04 = a01 * a13 - a03 * a11;
		var b05 = a02 * a13 - a03 * a12;
		var b06 = a20 * a31 - a21 * a30;
		var b07 = a20 * a32 - a22 * a30;
		var b08 = a20 * a33 - a23 * a30;
		var b09 = a21 * a32 - a22 * a31;
		var b10 = a21 * a33 - a23 * a31;
		var b11 = a22 * a33 - a23 * a32;

		var det = b00 * b11 - b01 * b10 + b02 * b09 + b03 * b08 - b04 * b07 + b05 * b06;
		if (det == 0.0) return setIdentity();
		det = 1.0 / det;

		_00 = (a11 * b11 - a12 * b10 + a13 * b09) * det;
		_01 = (a02 * b10 - a01 * b11 - a03 * b09) * det;
		_02 = (a31 * b05 - a32 * b04 + a33 * b03) * det;
		_03 = (a22 * b04 - a21 * b05 - a23 * b03) * det;
		_10 = (a12 * b08 - a10 * b11 - a13 * b07) * det;
		_11 = (a00 * b11 - a02 * b08 + a03 * b07) * det;
		_12 = (a32 * b02 - a30 * b05 - a33 * b01) * det;
		_13 = (a20 * b05 - a22 * b02 + a23 * b01) * det;
		_20 = (a10 * b10 - a11 * b08 + a13 * b06) * det;
		_21 = (a01 * b08 - a00 * b10 - a03 * b06) * det;
		_22 = (a30 * b04 - a31 * b02 + a33 * b00) * det;
		_23 = (a21 * b02 - a20 * b04 - a23 * b00) * det;
		_30 = (a11 * b07 - a10 * b09 - a12 * b06) * det;
		_31 = (a00 * b09 - a01 * b07 + a02 * b06) * det;
		_32 = (a31 * b01 - a30 * b03 - a32 * b00) * det;
		_33 = (a20 * b03 - a21 * b01 + a22 * b00) * det;

		return this;
	}

	/**
		Transpose this matrix.
		@return	This matrix.
	**/
	public inline function transpose(): Mat4 {
		var f = _01; _01 = _10; _10 = f;
		f = _02; _02 = _20; _20 = f;
		f = _03; _03 = _30; _30 = f;
		f = _12; _12 = _21; _21 = f;
		f = _13; _13 = _31; _31 = f;
		f = _23; _23 = _32; _32 = f;
		return this;
	}

	public inline function transpose3x3(): Mat4 {
		var f = _01; _01 = _10; _10 = f;
		f = _02; _02 = _20; _20 = f;
		f = _12; _12 = _21; _21 = f;
		return this;
	}

	/**
		Create a copy of this matrix.
		@return	A new matrix.
	**/
	public inline function clone(): Mat4 {
		return new Mat4(
			_00, _10, _20, _30,
			_01, _11, _21, _31,
			_02, _12, _22, _32,
			_03, _13, _23, _33
		);
	}

	public inline function setF32(a: kha.arrays.Float32Array, offset = 0): Mat4 {
		_00 = a[0 + offset]; _10 = a[1 + offset]; _20 = a[2 + offset]; _30 = a[3 + offset];
		_01 = a[4 + offset]; _11 = a[5 + offset]; _21 = a[6 + offset]; _31 = a[7 + offset];
		_02 = a[8 + offset]; _12 = a[9 + offset]; _22 = a[10 + offset]; _32 = a[11 + offset];
		_03 = a[12 + offset]; _13 = a[13 + offset]; _23 = a[14 + offset]; _33 = a[15 + offset];
		return this;
	}

	public inline function setFrom(m: Mat4): Mat4 {
		_00 = m._00; _01 = m._01; _02 = m._02; _03 = m._03;
		_10 = m._10; _11 = m._11; _12 = m._12; _13 = m._13;
		_20 = m._20; _21 = m._21; _22 = m._22; _23 = m._23;
		_30 = m._30; _31 = m._31; _32 = m._32; _33 = m._33;
		return this;
	}

	/**
		Get the location component.
		@return	A new vector.
	**/
	public inline function getLoc(): Vec4 {
		return new Vec4(_30, _31, _32, _33);
	}

	/**
		Get the scale component.
		@return	A new vector.
	**/
	public inline function getScale(): Vec4 {
		return new Vec4(
			Math.sqrt(_00 * _00 + _10 * _10 + _20 * _20),
			Math.sqrt(_01 * _01 + _11 * _11 + _21 * _21),
			Math.sqrt(_02 * _02 + _12 * _12 + _22 * _22)
		);
	}

	/**
		Multiply this vector by a scalar.
		@param	s The value to multiply by.
		@return	This matrix.
	**/
	public inline function mult(s: FastFloat): Mat4 {
		_00 *= s; _10 *= s; _20 *= s; _30 *= s;
		_01 *= s; _11 *= s; _21 *= s; _31 *= s;
		_02 *= s; _12 *= s; _22 *= s; _32 *= s;
		_03 *= s; _13 *= s; _23 *= s; _33 *= s;
		return this;
	}

	/**
		Convert this matrix to a rotation matrix, and discard location and
		scale information.
		@return	This matrix.
	**/
	public inline function toRotation(): Mat4 {
		var scale = 1.0 / helpVec.set(_00, _01, _02).length();
		_00 = _00 * scale;
		_01 = _01 * scale;
		_02 = _02 * scale;
		scale = 1.0 / helpVec.set(_10, _11, _12).length();
		_10 = _10 * scale;
		_11 = _11 * scale;
		_12 = _12 * scale;
		scale = 1.0 / helpVec.set(_20, _21, _22).length();
		_20 = _20 * scale;
		_21 = _21 * scale;
		_22 = _22 * scale;
		_03 = 0.0;
		_13 = 0.0;
		_23 = 0.0;
		_30 = 0.0;
		_31 = 0.0;
		_32 = 0.0;
		_33 = 1.0;
		return this;
	}

	/**
		Create a new perspective projection matrix.
		@param	fovY The vertical field of view.
		@param	aspect The aspect ratio.
		@param	zn The depth of the near floor of the frustum.
		@param	zf The depth of the far floor of the frustum.
		@return	A new matrix.
	**/
	public static inline function persp(fovY: FastFloat, aspect: FastFloat, zn: FastFloat, zf: FastFloat): Mat4 {
		var uh = 1.0 / Math.tan(fovY / 2);
		var uw = uh / aspect;
		return new Mat4(
			uw, 0, 0, 0,
			0, uh, 0, 0,
			0, 0, (zf + zn) / (zn - zf), 2 * zf * zn / (zn - zf),
			0, 0, -1, 0
		);
	}

	/**
		Create a new orthographic projection matrix.
		@param	left The left of the box.
		@param	right The right of the box.
		@param	bottom The bottom of the box.
		@param	top The top of the box.
		@param	near The depth of the near floor of the box.
		@param	far The depth of the far floor of the box.
		@return	A new matrix.
	**/
	public static inline function ortho(left: FastFloat, right: FastFloat, bottom: FastFloat, top: FastFloat, near: FastFloat, far: FastFloat): Mat4 {
		var rl = right - left;
		var tb = top - bottom;
		var fn = far - near;
		var tx = -(right + left) / (rl);
		var ty = -(top + bottom) / (tb);
		var tz = -(far + near) / (fn);
		return new Mat4(
			2 / rl,	0,		0,		 tx,
			0,		2 / tb,	0,		 ty,
			0,		0,		-2 / fn, tz,
			0,		0,		0,		 1
		);
	}

	public inline function setLookAt(eye: Vec4, center: Vec4, up: Vec4): Mat4 {
		var f0 = center.x - eye.x;
		var f1 = center.y - eye.y;
		var f2 = center.z - eye.z;
		var n = 1.0 / Math.sqrt(f0 * f0 + f1 * f1 + f2 * f2);
		f0 *= n;
		f1 *= n;
		f2 *= n;

		var s0 = f1 * up.z - f2 * up.y;
		var s1 = f2 * up.x - f0 * up.z;
		var s2 = f0 * up.y - f1 * up.x;
		n = 1.0 / Math.sqrt(s0 * s0 + s1 * s1 + s2 * s2);
		s0 *= n;
		s1 *= n;
		s2 *= n;

		var u0 = s1 * f2 - s2 * f1;
		var u1 = s2 * f0 - s0 * f2;
		var u2 = s0 * f1 - s1 * f0;
		var d0 = -eye.x * s0 - eye.y * s1 - eye.z * s2;
		var d1 = -eye.x * u0 - eye.y * u1 - eye.z * u2;
		var d2 =  eye.x * f0 + eye.y * f1 + eye.z * f2;

		_00 = s0;
		_10 = s1;
		_20 = s2;
		_30 = d0;
		_01 = u0;
		_11 = u1;
		_21 = u2;
		_31 = d1;
		_02 = -f0;
		_12 = -f1;
		_22 = -f2;
		_32 = d2;
		_03 = 0.0;
		_13 = 0.0;
		_23 = 0.0;
		_33 = 1.0;
		return this;
	}

	/**
		Apply an additional rotation to this matrix.
		@param	q The quaternion to rotate by.
	**/
	public inline function applyQuat(q: Quat) {
		helpMat.fromQuat(q);
		multmat(helpMat);
	}

	/**
		@return	The right vector; the positive x axis of the space defined by
				this matrix.
	**/
	public inline function right(): Vec4 {
		return new Vec4(_00, _01, _02);
	}
	/**
		@return	The look vector; the positive y axis of the space defined by
				this matrix.
	**/
	public inline function look(): Vec4 {
		return new Vec4(_10, _11, _12);
	}
	/**
		@return	The up vector; the positive z axis of the space defined by
				this matrix.
	**/
	public inline function up(): Vec4 {
		return new Vec4(_20, _21, _22);
	}

	public var _00(get, set): FastFloat; inline function get__00(): FastFloat { return self._00; } inline function set__00(f: FastFloat): FastFloat { return self._00 = f; }
	public var _01(get, set): FastFloat; inline function get__01(): FastFloat { return self._01; } inline function set__01(f: FastFloat): FastFloat { return self._01 = f; }
	public var _02(get, set): FastFloat; inline function get__02(): FastFloat { return self._02; } inline function set__02(f: FastFloat): FastFloat { return self._02 = f; }
	public var _03(get, set): FastFloat; inline function get__03(): FastFloat { return self._03; } inline function set__03(f: FastFloat): FastFloat { return self._03 = f; }
	public var _10(get, set): FastFloat; inline function get__10(): FastFloat { return self._10; } inline function set__10(f: FastFloat): FastFloat { return self._10 = f; }
	public var _11(get, set): FastFloat; inline function get__11(): FastFloat { return self._11; } inline function set__11(f: FastFloat): FastFloat { return self._11 = f; }
	public var _12(get, set): FastFloat; inline function get__12(): FastFloat { return self._12; } inline function set__12(f: FastFloat): FastFloat { return self._12 = f; }
	public var _13(get, set): FastFloat; inline function get__13(): FastFloat { return self._13; } inline function set__13(f: FastFloat): FastFloat { return self._13 = f; }
	public var _20(get, set): FastFloat; inline function get__20(): FastFloat { return self._20; } inline function set__20(f: FastFloat): FastFloat { return self._20 = f; }
	public var _21(get, set): FastFloat; inline function get__21(): FastFloat { return self._21; } inline function set__21(f: FastFloat): FastFloat { return self._21 = f; }
	public var _22(get, set): FastFloat; inline function get__22(): FastFloat { return self._22; } inline function set__22(f: FastFloat): FastFloat { return self._22 = f; }
	public var _23(get, set): FastFloat; inline function get__23(): FastFloat { return self._23; } inline function set__23(f: FastFloat): FastFloat { return self._23 = f; }
	public var _30(get, set): FastFloat; inline function get__30(): FastFloat { return self._30; } inline function set__30(f: FastFloat): FastFloat { return self._30 = f; }
	public var _31(get, set): FastFloat; inline function get__31(): FastFloat { return self._31; } inline function set__31(f: FastFloat): FastFloat { return self._31 = f; }
	public var _32(get, set): FastFloat; inline function get__32(): FastFloat { return self._32; } inline function set__32(f: FastFloat): FastFloat { return self._32 = f; }
	public var _33(get, set): FastFloat; inline function get__33(): FastFloat { return self._33; } inline function set__33(f: FastFloat): FastFloat { return self._33 = f; }

	public function toString(): String {
        return '[[$_00, $_10, $_20, $_30], [$_01, $_11, $_21, $_31], [$_02, $_12, $_22, $_32], [$_03, $_13, $_23, $_33]]';
	}

	public function toFloat32Array(): kha.arrays.Float32Array {
		var array = new kha.arrays.Float32Array(16);
		array[0] = _00;
		array[1] = _10;
		array[2] = _20;
		array[3] = _30;
		array[4] = _01;
		array[5] = _11;
		array[6] = _21;
		array[7] = _31;
		array[8] = _02;
		array[9] = _12;
		array[10] = _22;
		array[11] = _32;
		array[12] = _03;
		array[13] = _13;
		array[14] = _23;
		array[15] = _33;
		return array;
	}
}
