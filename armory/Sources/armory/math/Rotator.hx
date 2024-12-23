package armory.math;

import kha.FastFloat;
import iron.math.Mat4;

class Rotator {
	public var pitch: FastFloat; // X - look up or down around the X axis
	public var roll: FastFloat; // Y - axis tilt left or right around the Y axis
	public var yaw: FastFloat; // Z - heading or facing angle around the Z (up) axis

	public function new(pitch: FastFloat = 0.0, roll: FastFloat = 0.0, yaw: FastFloat = 0.0) {
		this.pitch = pitch;
		this.roll = roll;
		this.yaw = yaw;
	}

	public function toDegrees(): Rotator {
		pitch = Helper.radToDeg(pitch);
		roll = Helper.radToDeg(roll);
		yaw = Helper.radToDeg(yaw);
		return this;
	}

	public function toRadians(): Rotator {
		pitch = Helper.degToRad(pitch);
		roll = Helper.degToRad(roll);
		yaw = Helper.degToRad(yaw);
		return this;
	}

	public function cross(r: Rotator): Rotator {
		var x2 = roll * r.yaw - yaw * r.roll;
		var y2 = yaw * r.pitch - pitch * r.yaw;
		var z2 = pitch * r.roll - roll * r.pitch;
		pitch = x2;
		roll = y2;
		yaw = z2;
		return this;
	}

	public function crossvecs(a: Rotator, b: Rotator): Rotator {
		var x2 = a.roll * b.yaw - a.yaw * b.roll;
		var y2 = a.yaw * b.pitch - a.pitch * b.yaw;
		var z2 = a.pitch * b.roll - a.roll * b.pitch;
		pitch = x2;
		roll = y2;
		yaw = z2;
		return this;
	}

	public function set(pitch: FastFloat, roll: FastFloat, yaw: FastFloat): Rotator{
		this.pitch = pitch;
		this.roll = roll;
		this.yaw = yaw;
		return this;
	}

	public function add(r: Rotator): Rotator {
		pitch += r.pitch;
		roll += r.roll;
		yaw += r.yaw;
		return this;
	}

	public function addf(pitch: FastFloat, roll: FastFloat, yaw: FastFloat): Rotator {
		this.pitch += pitch;
		this.roll += roll;
		this.yaw += yaw;
		return this;
	}

	public function addvecs(a: Rotator, b: Rotator): Rotator {
		pitch = a.pitch + b.pitch;
		roll = a.roll + b.roll;
		yaw = a.yaw + b.yaw;
		return this;
	}

	public function subvecs(a: Rotator, b: Rotator): Rotator {
		pitch = a.pitch - b.pitch;
		roll = a.roll - b.roll;
		yaw = a.yaw - b.yaw;
		return this;
	}

	public function normalize(): Rotator {
		var n = length();
		if (n > 0.0) {
			var invN = 1.0 / n;
			this.pitch *= invN; this.roll *= invN; this.yaw *= invN;
		}
		return this;
	}

	public function mult(f: FastFloat): Rotator {
		pitch *= f; roll *= f; yaw *= f;
		return this;
	}

	public function dot(r: Rotator): FastFloat {
		return pitch * r.pitch + roll * r.roll + yaw * r.yaw;
	}

	public function setFrom(r: Rotator): Rotator {
		pitch = r.pitch; roll = r.roll; yaw = r.yaw;
		return this;
	}

	public function clone(): Rotator {
		return new Rotator(pitch, roll, yaw);
	}

	public static function lerp(from: Rotator, to: Rotator, s: FastFloat): Rotator {
		var target = new Rotator();
		target.pitch = from.pitch + (to.pitch - from.pitch) * s;
		target.roll = from.roll + (to.roll - from.roll) * s;
		target.yaw = from.yaw + (to.yaw - from.yaw) * s;
		return target;
	}

	public function applyproj(m: Mat4): Rotator {
		var pitch = this.pitch; var roll = this.roll; var yaw = this.yaw;

		// Perspective divide
		var d = 1.0 / (m._03 * pitch + m._13 * roll + m._23 * yaw + m._33);

		this.pitch = (m._00 * pitch + m._10 * roll + m._20 * yaw + m._30) * d;
		this.roll = (m._01 * pitch + m._11 * roll + m._21 * yaw + m._31) * d;
		this.yaw = (m._02 * pitch + m._12 * roll + m._22 * yaw + m._32) * d;

		return this;
	}

	public function applymat(m: Mat4): Rotator {
		var pitch = this.pitch; var roll = this.roll; var yaw = this.yaw;

		this.pitch = m._00 * pitch + m._10 * roll + m._20 * yaw + m._30;
		this.roll = m._01 * pitch + m._11 * roll + m._21 * yaw + m._31;
		this.yaw = m._02 * pitch + m._12 * roll + m._22 * yaw + m._32;

		return this;
	}

	public inline function equals(r: Rotator): Bool {
		return pitch == r.pitch && roll == r.roll && yaw == r.yaw;
	}

	public inline function length(): FastFloat {
		return Math.sqrt(pitch * pitch + roll * roll + yaw * yaw);
	}

	public inline function normalizeTo(newLength: FastFloat): Rotator {
		var v = normalize();
		v = mult(newLength);
		return v;
	}

	public function sub(r: Rotator): Rotator {
		pitch -= r.pitch; roll -= r.roll; yaw -= r.yaw;
		return this;
	}

	public static inline function distance(r1: Rotator, r2: Rotator): FastFloat {
		return distancef(r1.pitch, r1.roll, r1.yaw, r2.pitch, r2.roll, r2.yaw);
	}

	public static inline function distancef(r1pitch: FastFloat, r1roll: FastFloat, r1yaw: FastFloat, r2pitch: FastFloat, r2roll: FastFloat, r2yaw: FastFloat): FastFloat {
		var pitch = r1pitch - r2pitch;
		var roll = r1roll - r2roll;
		var yaw = r1yaw - r2yaw;
		return Math.sqrt(pitch * pitch + roll * roll + yaw * yaw);
	}

	public function distanceTo(r: Rotator): FastFloat {
		return Math.sqrt((r.pitch - pitch) * (r.pitch - pitch) + (r.roll - roll) * (r.roll - roll) + (r.yaw - yaw) * (r.yaw - yaw));
	}

	public function clamp(): Rotator {
		this.pitch = clampAxis(this.pitch);
		this.roll = clampAxis(this.roll);
		this.yaw = clampAxis(this.yaw);
		return this;
	}

	public static inline function clampAxis(angle: FastFloat): FastFloat {
		angle = angle % 360; // Makes the angle between -360 and +360
		if (angle < 0.0) angle += 360.0;
		return angle;
	}

	public static function xAxis(): Rotator { return new Rotator(1.0, 0.0, 0.0); }
	public static function yAxis(): Rotator { return new Rotator(0.0, 1.0, 0.0); }
	public static function zAxis(): Rotator { return new Rotator(0.0, 0.0, 1.0); }
	public static function one(): Rotator { return new Rotator(1.0, 1.0, 1.0); }
	public static function zero(): Rotator { return new Rotator(0.0, 0.0, 0.0); }
	public static function back(): Rotator { return new Rotator(0.0, -1.0, 0.0); }
	public static function forward(): Rotator { return new Rotator(0.0, 1.0, 0.0); }
	public static function down(): Rotator { return new Rotator(0.0, 0.0, -1.0); }
	public static function up(): Rotator { return new Rotator(0.0, 0.0, 1.0); }
	public static function left(): Rotator { return new Rotator(-1.0, 0.0, 0.0); }
	public static function right(): Rotator { return new Rotator(1.0, 0.0, 0.0); }
	public static function negativeInfinity(): Rotator { return new Rotator(Math.NEGATIVE_INFINITY, Math.NEGATIVE_INFINITY, Math.NEGATIVE_INFINITY); }
	public static function positiveInfinity(): Rotator { return new Rotator(Math.POSITIVE_INFINITY, Math.POSITIVE_INFINITY, Math.POSITIVE_INFINITY); }

	public function toString(): String {
		return "(" + this.pitch + ", " + this.roll + ", " + this.yaw + ")";
	}
}
