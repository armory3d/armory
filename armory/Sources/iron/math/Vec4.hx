package iron.math;

import kha.FastFloat;

class Vec4 {

	public var x: FastFloat;
	public var y: FastFloat;
	public var z: FastFloat;
	public var w: FastFloat;

	public inline function new(x: FastFloat = 0.0, y: FastFloat = 0.0, z: FastFloat = 0.0, w: FastFloat = 1.0) {
		this.x = x;
		this.y = y;
		this.z = z;
		this.w = w;
	}

	public inline function cross(v: Vec4): Vec4 {
		var ax = x; var ay = y; var az = z;
		var vx = v.x; var vy = v.y; var vz = v.z;
		x = ay * vz - az * vy;
		y = az * vx - ax * vz;
		z = ax * vy - ay * vx;
		return this;
	}

	public inline function crossvecs(a: Vec4, b: Vec4): Vec4 {
		var ax = a.x; var ay = a.y; var az = a.z;
		var bx = b.x; var by = b.y; var bz = b.z;
		x = ay * bz - az * by;
		y = az * bx - ax * bz;
		z = ax * by - ay * bx;
		return this;
	}

	public inline function set(x: FastFloat, y: FastFloat, z: FastFloat, w: FastFloat = 1.0): Vec4{
		this.x = x;
		this.y = y;
		this.z = z;
		this.w = w;
		return this;
	}

	public inline function add(v: Vec4): Vec4 {
		x += v.x;
		y += v.y;
		z += v.z;
		return this;
	}

	public inline function addf(x: FastFloat, y: FastFloat, z: FastFloat): Vec4 {
		this.x += x;
		this.y += y;
		this.z += z;
		return this;
	}

	public inline function addvecs(a: Vec4, b: Vec4): Vec4 {
		x = a.x + b.x;
		y = a.y + b.y;
		z = a.z + b.z;
		return this;
	}

	public inline function subvecs(a: Vec4, b: Vec4): Vec4 {
		x = a.x - b.x;
		y = a.y - b.y;
		z = a.z - b.z;
		return this;
	}

	public inline function normalize(): Vec4 {
		var n = length();
		if (n > 0.0) {
			var invN = 1.0 / n;
			this.x *= invN;
			this.y *= invN;
			this.z *= invN;
		}
		return this;
	}

	public inline function mult(f: FastFloat): Vec4 {
		x *= f;
		y *= f;
		z *= f;
		return this;
	}

	public inline function dot(v: Vec4): FastFloat {
		return x * v.x + y * v.y + z * v.z;
	}

	public inline function setFrom(v: Vec4): Vec4 {
		x = v.x;
		y = v.y;
		z = v.z;
		w = v.w;
		return this;
	}

	public inline function clone(): Vec4 {
		return new Vec4(x, y, z, w);
	}

	public inline function lerp(from: Vec4, to: Vec4, s: FastFloat): Vec4 {
		x = from.x + (to.x - from.x) * s;
		y = from.y + (to.y - from.y) * s;
		z = from.z + (to.z - from.z) * s;
		return this;
	}

	public inline function applyproj(m: Mat4): Vec4 {
		var x = this.x; var y = this.y; var z = this.z;
		var d = 1.0 / (m._03 * x + m._13 * y + m._23 * z + m._33); // Perspective divide
		this.x = (m._00 * x + m._10 * y + m._20 * z + m._30) * d;
		this.y = (m._01 * x + m._11 * y + m._21 * z + m._31) * d;
		this.z = (m._02 * x + m._12 * y + m._22 * z + m._32) * d;
		return this;
	}

	public inline function applymat(m: Mat4): Vec4 {
		var x = this.x; var y = this.y; var z = this.z;
		this.x = m._00 * x + m._10 * y + m._20 * z + m._30;
		this.y = m._01 * x + m._11 * y + m._21 * z + m._31;
		this.z = m._02 * x + m._12 * y + m._22 * z + m._32;
		return this;
	}

	public inline function applymat4(m: Mat4): Vec4 {
		var x = this.x; var y = this.y; var z = this.z; var w = this.w;
		this.x = m._00 * x + m._10 * y + m._20 * z + m._30 * w;
		this.y = m._01 * x + m._11 * y + m._21 * z + m._31 * w;
		this.z = m._02 * x + m._12 * y + m._22 * z + m._32 * w;
		this.w = m._03 * x + m._13 * y + m._23 * z + m._33 * w;
		return this;
	}

	public inline function applyAxisAngle(axis: Vec4, angle: FastFloat): Vec4 {
		var quat = new Quat();
		quat.fromAxisAngle(axis, angle);
		return applyQuat(quat);
	}

	public inline function applyQuat(q: Quat): Vec4 {
		var ix = q.w * x + q.y * z - q.z * y;
		var iy = q.w * y + q.z * x - q.x * z;
		var iz = q.w * z + q.x * y - q.y * x;
		var iw = -q.x * x - q.y * y - q.z * z;
		x = ix * q.w + iw * -q.x + iy * -q.z - iz * -q.y;
		y = iy * q.w + iw * -q.y + iz * -q.x - ix * -q.z;
		z = iz * q.w + iw * -q.z + ix * -q.y - iy * -q.x;
		return this;
	}

	public inline function equals(v: Vec4): Bool {
		return x == v.x && y == v.y && z == v.z;
	}

	public inline function almostEquals(v: Vec4, prec: FastFloat): Bool {
		return Math.abs(x - v.x) < prec && Math.abs(y - v.y) < prec && Math.abs(z - v.z) < prec;
	}

	public inline function length(): FastFloat {
		return Math.sqrt(x * x + y * y + z * z);
	}

	public inline function sub(v: Vec4): Vec4 {
		x -= v.x; y -= v.y; z -= v.z;
		return this;
	}

	public inline function exp(v: Vec4): Vec4 {
		x = Math.exp(v.x);
		y = Math.exp(v.y);
		z = Math.exp(v.z);
		return this;
	}

	public static inline function distance(v1: Vec4, v2: Vec4): FastFloat {
		return distancef(v1.x, v1.y, v1.z, v2.x, v2.y, v2.z);
	}

	public static inline function distancef(v1x: FastFloat, v1y: FastFloat, v1z: FastFloat, v2x: FastFloat, v2y: FastFloat, v2z: FastFloat): FastFloat {
		var vx = v1x - v2x;
		var vy = v1y - v2y;
		var vz = v1z - v2z;
		return Math.sqrt(vx * vx + vy * vy + vz * vz);
	}

	public inline function distanceTo(p: Vec4): FastFloat {
		return Math.sqrt((p.x - x) * (p.x - x) + (p.y - y) * (p.y - y) + (p.z - z) * (p.z - z));
	}

	public inline function reflect(n: Vec4): Vec4 {
		var d = 2 * this.dot(n);
		x = x - d * n.x;
		y = y - d * n.y;
		z = z - d * n.z;
		return this;
	}

	public inline function clamp(min: FastFloat, max: FastFloat): Vec4 {
		var l = length();
		if (l < min) normalize().mult(min);
		else if (l > max) normalize().mult(max);
		return this;
	}

	public static inline function xAxis(): Vec4 {
		return new Vec4(1.0, 0.0, 0.0);
	}

	public static inline function yAxis(): Vec4 {
		return new Vec4(0.0, 1.0, 0.0);
	}

	public static inline function zAxis(): Vec4 {
		return new Vec4(0.0, 0.0, 1.0);
	}

	public function toString(): String {
		return "(" + this.x + ", " + this.y + ", " + this.z + ", " + this.w + ")";
	}
}
