package iron.math;

import kha.FastFloat;

class Vec2 {
	public var x: FastFloat;
	public var y: FastFloat;

	public inline function new(x: FastFloat = 0.0, y: FastFloat = 0.0) {
		this.x = x;
		this.y = y;
	}

	public inline function cross(v: Vec2): FastFloat {
		return x * v.y - y * v.x;
	}

	public inline function set(x: FastFloat, y: FastFloat): Vec2{
		this.x = x;
		this.y = y;
		return this;
	}

	public inline function add(v: Vec2): Vec2 {
		x += v.x;
		y += v.y;
		return this;
	}

	public inline function addf(x: FastFloat, y: FastFloat): Vec2 {
		this.x += x;
		this.y += y;
		return this;
	}

	public inline function addvecs(a: Vec2, b: Vec2): Vec2 {
		x = a.x + b.x;
		y = a.y + b.y;
		return this;
	}

	public inline function subvecs(a: Vec2, b: Vec2): Vec2 {
		x = a.x - b.x;
		y = a.y - b.y;
		return this;
	}

	public inline function normalize(): Vec2 {
		var a = this.x;
        var b = this.y;
        var l = a * a + b * b;
        if (l > 0.0) {
            l = 1.0 / Math.sqrt(l);
            this.x = a * l;
            this.y = b * l;
        }
        return this;
	}

	public inline function mult(f: FastFloat): Vec2 {
		x *= f;
		y *= f;
		return this;
	}

	public inline function dot(v: Vec2): FastFloat {
		return x * v.x + y * v.y;
	}

	public inline function setFrom(v: Vec2): Vec2 {
		x = v.x;
		y = v.y;
		return this;
	}

	public inline function clone(): Vec2 {
		return new Vec2(x, y);
	}

	public inline function lerp(from: Vec2, to: Vec2, s: FastFloat): Vec2 {
		x = from.x + (to.x - from.x) * s;
		y = from.y + (to.y - from.y) * s;
		return this;
	}

	public inline function equals(v: Vec2): Bool {
		return x == v.x && y == v.y;
	}

	public inline function length(): FastFloat {
		return Math.sqrt(x * x + y * y);
	}

	public inline function sub(v: Vec2): Vec2 {
		x -= v.x;
		y -= v.y;
		return this;
	}

	public inline function exp(v: Vec2): Vec2 {
		x = Math.exp(v.x);
		y = Math.exp(v.y);
		return this;
	}

	public static inline function distance(v1: Vec2, v2: Vec2): FastFloat {
		return distancef(v1.x, v1.y, v2.x, v2.y);
	}

	public static inline function distancef(v1x: FastFloat, v1y: FastFloat, v2x: FastFloat, v2y: FastFloat): FastFloat {
		var vx = v1x - v2x;
		var vy = v1y - v2y;
		return Math.sqrt(vx * vx + vy * vy);
	}

	public inline function distanceTo(p: Vec2): FastFloat {
		return Math.sqrt((p.x - x) * (p.x - x) + (p.y - y) * (p.y - y));
	}

	public inline function clamp(min: FastFloat, max: FastFloat): Vec2 {
		var l = length();
		if (l < min) normalize().mult(min);
		else if (l > max) normalize().mult(max);
		return this;
	}

	public static inline function xAxis(): Vec2 {
		return new Vec2(1.0, 0.0);
	}

	public static inline function yAxis(): Vec2 {
		return new Vec2(0.0, 1.0);
	}

	public function toString(): String {
		return "(" + this.x + ", " + this.y + ")";
	}
}
