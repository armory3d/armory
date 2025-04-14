package iron.math;

import kha.FastFloat;

class Quat {

	public var x: FastFloat;
	public var y: FastFloat;
	public var z: FastFloat;
	public var w: FastFloat;

	static var helpVec0 = new Vec4();
	static var helpVec1 = new Vec4();
	static var helpVec2 = new Vec4();
	static var helpMat = Mat4.identity();
	static var xAxis = Vec4.xAxis();
	static var yAxis = Vec4.yAxis();
	
	static inline var SQRT2: FastFloat = 1.4142135623730951;

	public inline function new(x: FastFloat = 0.0, y: FastFloat = 0.0, z: FastFloat = 0.0, w: FastFloat = 1.0) {
		this.x = x;
		this.y = y;
		this.z = z;
		this.w = w;
	}

	public inline function set(x: FastFloat, y: FastFloat, z: FastFloat, w: FastFloat): Quat {
		this.x = x;
		this.y = y;
		this.z = z;
		this.w = w;
		return this;
	}

	public inline function add(q: Quat): Quat {
		this.x += q.x;
		this.y += q.y;
		this.z += q.z;
		this.w += q.w;
		return this;
	}

	public inline function addquat(a: Quat, b: Quat): Quat {
		this.x = a.x + b.x;
		this.y = a.y + b.y;
		this.z = a.z + b.z;
		this.w = a.w + b.w;
		return this;
	}

	public inline function sub(q: Quat): Quat {
		this.x -= q.x;
		this.y -= q.y;
		this.z -= q.z;
		this.w -= q.w;
		return this;
	}

	public inline function subquat(a: Quat, b: Quat): Quat {
		this.x = a.x - b.x;
		this.y = a.y - b.y;
		this.z = a.z - b.z;
		this.w = a.w - b.w;
		return this;
	}

	public inline function fromAxisAngle(axis: Vec4, angle: FastFloat): Quat {
		var s: FastFloat = Math.sin(angle * 0.5);
		x = axis.x * s;
		y = axis.y * s;
		z = axis.z * s;
		w = Math.cos(angle * 0.5);
		return normalize();
	}

	public inline function toAxisAngle(axis: Vec4): FastFloat {
		normalize();
		var angle = 2 * Math.acos(w);
		var s = Math.sqrt(1 - w * w);
		if (s < 0.001) {
			axis.x = this.x;
			axis.y = this.y;
			axis.z = this.z;
		}
		else {
			axis.x = this.x / s;
			axis.y = this.y / s;
			axis.z = this.z / s;
		}
		return angle;
	}

	public inline function fromMat(m: Mat4): Quat {
		helpMat.setFrom(m);
		helpMat.toRotation();
		return fromRotationMat(helpMat);
	}

	public inline function fromRotationMat(m: Mat4): Quat {
		// Assumes the upper 3x3 is a pure rotation matrix
		var m11 = m._00; var m12 = m._10; var m13 = m._20;
		var m21 = m._01; var m22 = m._11; var m23 = m._21;
		var m31 = m._02; var m32 = m._12; var m33 = m._22;
		var tr = m11 + m22 + m33;
		var s = 0.0;

		if (tr > 0) {
			s = 0.5 / Math.sqrt(tr + 1.0);
			this.w = 0.25 / s;
			this.x = (m32 - m23) * s;
			this.y = (m13 - m31) * s;
			this.z = (m21 - m12) * s;
		}
		else if (m11 > m22 && m11 > m33) {
			s = 2.0 * Math.sqrt(1.0 + m11 - m22 - m33);
			this.w = (m32 - m23) / s;
			this.x = 0.25 * s;
			this.y = (m12 + m21) / s;
			this.z = (m13 + m31) / s;
		}
		else if (m22 > m33) {
			s = 2.0 * Math.sqrt(1.0 + m22 - m11 - m33);
			this.w = (m13 - m31) / s;
			this.x = (m12 + m21) / s;
			this.y = 0.25 * s;
			this.z = (m23 + m32) / s;
		}
		else {
			s = 2.0 * Math.sqrt(1.0 + m33 - m11 - m22);
			this.w = (m21 - m12) / s;
			this.x = (m13 + m31) / s;
			this.y = (m23 + m32) / s;
			this.z = 0.25 * s;
		}
		return this;
	}

	// Multiply this quaternion by float
	public inline function scale(scale: FastFloat): Quat {
		this.x *= scale;
		this.y *= scale;
		this.z *= scale;
		this.w *= scale;
		return this;
	}

	public inline function scalequat(q: Quat, scale: FastFloat): Quat {
		q.x *= scale;
		q.y *= scale;
		q.z *= scale;
		q.w *= scale;
		return q;
	}

	/**
		Multiply this quaternion by another.
		@param	q The quaternion to multiply this one with.
		@return	This quaternion.
	**/
	public inline function mult(q: Quat): Quat {
		return multquats(this, q);
	}

	/**
		Multiply two other quaternions and store the result in this one.
		@param	q1 The first operand.
		@param	q2 The second operand.
		@return	This quaternion.
	**/
	public inline function multquats(q1: Quat, q2: Quat): Quat {
		var q1x = q1.x; var q1y = q1.y; var q1z = q1.z; var q1w = q1.w;
		var q2x = q2.x; var q2y = q2.y; var q2z = q2.z; var q2w = q2.w;
		x = q1x * q2w + q1w * q2x + q1y * q2z - q1z * q2y;
		y = q1w * q2y - q1x * q2z + q1y * q2w + q1z * q2x;
		z = q1w * q2z + q1x * q2y - q1y * q2x + q1z * q2w;
		w = q1w * q2w - q1x * q2x - q1y * q2y - q1z * q2z;
		return this;
	}

	public inline function module(): FastFloat {
		return Math.sqrt(this.x * this.x + this.y * this.y + this.z * this.z + this.w * this.w);
	}

	/**
		Scale this quaternion to have a magnitude of 1.
		@return	This quaternion.
	**/
	public inline function normalize(): Quat {
		var l = Math.sqrt(x * x + y * y + z * z + w * w);
		if (l == 0.0) {
			x = 0;
			y = 0;
			z = 0;
			w = 0;
		}
		else {
			l = 1.0 / l;
			x *= l;
			y *= l;
			z *= l;
			w *= l;
		}
		return this;
	}

	/**
		Invert the given quaternion and store the result in this one.
		@param	q Quaternion to invert.
		@return	This quaternion.
	**/
	public inline function inverse(q: Quat): Quat {
		var sqsum = q.x * q.x + q.y * q.y + q.z * q.z + q.w * q.w;
		sqsum = -1 / sqsum;
		x = q.x * sqsum;
		y = q.y * sqsum;
		z = q.z * sqsum;
		w = -q.w * sqsum;
		return this;
	}

	/**
		Copy the rotation of another quaternion to this one.
		@param	q A quaternion to copy.
		@return	This quaternion.
	**/
	public inline function setFrom(q: Quat): Quat {
		x = q.x;
		y = q.y;
		z = q.z;
		w = q.w;
		return this;
	}

	/**
		Convert this quaternion to a YZX Euler (note: XZY in blender order terms).
		@return	A new YZX Euler that represents the same rotation as this
				quaternion.
	**/
	public inline function getEuler(): Vec4 {
		var a = -2 * (x * z - w * y);
		var b =  w *  w + x * x - y * y - z * z;
		var c =  2 * (x * y + w * z);
		var d = -2 * (y * z - w * x);
		var e =  w *  w - x * x + y * y - z * z;
		return new Vec4(Math.atan2(d, e), Math.atan2(a, b), Math.asin(c));
	}

	/**
		Set this quaternion to the rotation represented by a YZX Euler (XZY in blender terms).
		@param	x The Euler's x component.
		@param	y The Euler's y component.
		@param	z The Euler's z component.
		@return	This quaternion.
	**/
	public inline function fromEuler(x: FastFloat, y: FastFloat, z: FastFloat): Quat {
		var f = x / 2;
		var c1 = Math.cos(f);
		var s1 = Math.sin(f);
		f = y / 2;
		var c2 = Math.cos(f);
		var s2 = Math.sin(f);
		f = z / 2;
		var c3 = Math.cos(f);
		var s3 = Math.sin(f);
		// YZX
		this.x = s1 * c2 * c3 + c1 * s2 * s3;
		this.y = c1 * s2 * c3 + s1 * c2 * s3;
		this.z = c1 * c2 * s3 - s1 * s2 * c3;
		this.w = c1 * c2 * c3 - s1 * s2 * s3;
		return this;
	}

	/**
		Convert this quaternion to an Euler of arbitrary order.
		@param	the order of the euler to obtain
			(in blender order, opposite from mathematical order)
			can be "XYZ", "XZY", "YXZ", "YZX", "ZXY", or "ZYX".
		@return	A new YZX Euler that represents the same rotation as this
				quaternion.
	**/
	// this method use matrices as a middle ground
	// (and is copied from blender's internal code in mathutils)
	// note: there are two possible eulers for the same rotation, blender defines the 'best' as the one with the smallest sum of absolute components
	//	should we actually make that choice, or is just getting one of them randomly good?
	// note2: it seems that this engine transforms a vector by using vector×matrix instead of matrix×vector, meaning that the outer transformations are on the RIGHT.
	//	(…Except for quaternions, where the outer quaternions are on the LEFT.)
	//	anywho, the way the elements of the matrix are ordered makes sense (first digit-> row ID, second digit->column ID) in this system.
	public inline function toEulerOrdered(p: String): Vec4{
		// normalize quat ?

		var q0: FastFloat = SQRT2 * this.w;
		var q1: FastFloat = SQRT2 * this.x;
		var q2: FastFloat = SQRT2 * this.y;
		var q3: FastFloat = SQRT2 * this.z;

		var qda: FastFloat = q0 * q1;
		var qdb: FastFloat = q0 * q2;
		var qdc: FastFloat = q0 * q3;
		var qaa: FastFloat = q1 * q1;
		var qab: FastFloat = q1 * q2;
		var qac: FastFloat = q1 * q3;
		var qbb: FastFloat = q2 * q2;
		var qbc: FastFloat = q2 * q3;
		var qcc: FastFloat = q3 * q3;

		var m = new Mat3(
			// OK, *this* matrix is transposed with respect to what armory expects.
			// it is transposed again in the next step though

			(1.0 - qbb - qcc),
			(qdc + qab),
			(-qdb + qac),

			(-qdc + qab),
			(1.0 - qaa - qcc),
			(qda + qbc),

			(qdb + qac),
			(-qda + qbc),
			(1.0 - qaa - qbb)
		);

		// now define what is necessary to perform look-ups in that matrix
		var ml: Array<Array<FastFloat>> = [[m._00, m._10, m._20],
		                                   [m._01, m._11, m._21],
		                                   [m._02, m._12, m._22]];
		var eull: Array<FastFloat> = [0, 0, 0];

		var i: Int = p.charCodeAt(0) - "X".charCodeAt(0);
		var j: Int = p.charCodeAt(1) - "X".charCodeAt(0);
		var k: Int = p.charCodeAt(2) - "X".charCodeAt(0);

		// now the dumber version (isolating code)
		if (p.charAt(0) == "X") i = 0;
		else if (p.charAt(0) == "Y") i = 1;
		else i = 2;
		if (p.charAt(1) == "X") j = 0;
		else if (p.charAt(1) == "Y") j = 1;
		else j = 2;
		if (p.charAt(2) == "X") k = 0;
		else if (p.charAt(2) == "Y") k = 1;
		else k = 2;

		var cy: FastFloat = Math.sqrt(ml[i][i] * ml[i][i] + ml[i][j] * ml[i][j]);

		var eul1 = new Vec4();

		if (cy > 16.0 * 1e-3) {
			eull[i] = Math.atan2(ml[j][k], ml[k][k]);
			eull[j] = Math.atan2(-ml[i][k], cy);
			eull[k] = Math.atan2(ml[i][j], ml[i][i]);
		}
		else {
			eull[i] = Math.atan2(-ml[k][j], ml[j][j]);
			eull[j] = Math.atan2(-ml[i][k], cy);
			eull[k] = 0; // 2 * Math.PI;
		}
		eul1.x = eull[0];
		eul1.y = eull[1];
		eul1.z = eull[2];

		if (p == "XZY" || p == "YXZ" || p == "ZYX") {
			eul1.x *= -1;
			eul1.y *= -1;
			eul1.z *= -1;
		}
		return eul1;
	}

	/**
		Set this quaternion to the rotation represented by an Euler.
		@param	x The Euler's x component.
		@param	y The Euler's y component.
		@param	z The Euler's z component.
		@param	order: the (blender) order of the euler
			(which is the OPPOSITE of the mathematical order)
			can be "XYZ", "XZY", "YXZ", "YZX", "ZXY", or "ZYX".
		@return	This quaternion.
	**/
	public inline function fromEulerOrdered(e: Vec4, order: String): Quat {
		var c1 = Math.cos(e.x / 2);
		var c2 = Math.cos(e.y / 2);
		var c3 = Math.cos(e.z / 2);
		var s1 = Math.sin(e.x / 2);
		var s2 = Math.sin(e.y / 2);
		var s3 = Math.sin(e.z / 2);

		var qx = new Quat(s1, 0, 0, c1);
		var qy = new Quat(0, s2, 0, c2);
		var qz = new Quat(0, 0, s3, c3);

		if (order.charAt(2) == 'X')
			this.setFrom(qx);
		else if (order.charAt(2) == 'Y')
			this.setFrom(qy);
		else
			this.setFrom(qz);
		if (order.charAt(1) == 'X')
			this.mult(qx);
		else if (order.charAt(1) == 'Y')
			this.mult(qy);
		else
			this.mult(qz);
		if (order.charAt(0) == 'X')
			this.mult(qx);
		else if (order.charAt(0) == 'Y')
			this.mult(qy);
		else
			this.mult(qz);

		return this;
	}

	/**
		Linearly interpolate between two other quaterions, and store the
		result in this one. This is not a so-called slerp operation.
		@param	from The quaterion to interpolate from.
		@param	to The quaterion to interpolate to.
		@param	s The amount to interpolate, with 0 being `from` and 1 being
				`to`, and 0.5 being half way between the two.
		@return	This quaternion.
	**/
	public inline function lerp(from: Quat, to: Quat, s: FastFloat): Quat {
		var fromx = from.x;
		var fromy = from.y;
		var fromz = from.z;
		var fromw = from.w;
		var dot: FastFloat = from.dot(to);
		if (dot < 0.0) {
			fromx = -fromx;
			fromy = -fromy;
			fromz = -fromz;
			fromw = -fromw;
		}
		x = fromx + (to.x - fromx) * s;
		y = fromy + (to.y - fromy) * s;
		z = fromz + (to.z - fromz) * s;
		w = fromw + (to.w - fromw) * s;
		return normalize();
	}

	// Slerp is shorthand for spherical linear interpolation
	public inline function slerp(from: Quat, to: Quat, t: FastFloat): Quat {
		var epsilon: Float = 0.0005;

		var dot = from.dot(to);
		if (dot > 1 - epsilon) {
			var result: Quat = to.add((from.sub(to)).scale(t));
			result.normalize();
			return result;
		}
		if (dot < 0) dot = 0;
		if (dot > 1) dot = 1;

		var theta0: Float = Math.acos(dot);
		var theta: Float = theta0 * t;
		var q2: Quat = to.sub(scale(dot));
		q2.normalize();
		var result: Quat = scale(Math.cos(theta)).add(q2.scale(Math.sin(theta)));
		result.normalize();
		return result;
	}

	/**
		Find the dot product of this quaternion with another.
		@param	q The other quaternion.
		@return	The dot product.
	**/
	public inline function dot(q: Quat): FastFloat {
		return (x * q.x) + (y * q.y) + (z * q.z) + (w * q.w);
	}

	public inline function fromTo(v1: Vec4, v2: Vec4): Quat {
		// Rotation formed by direction vectors
		// v1 and v2 should be normalized first
		var a = helpVec0;
		var dot = v1.dot(v2);
		if (dot < -0.999999) {
			a.crossvecs(xAxis, v1);
			if (a.length() < 0.000001) a.crossvecs(yAxis, v1);
			a.normalize();
			fromAxisAngle(a, Math.PI);
		}
		else if (dot > 0.999999) {
			set(0, 0, 0, 1);
		}
		else {
			a.crossvecs(v1, v2);
			set(a.x, a.y, a.z, 1 + dot);
			normalize();
		}
		return this;
	}

	public function toString(): String {
		return this.x + ", " + this.y + ", " + this.z + ", " + this.w;
	}
}
