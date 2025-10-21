package armory.math;

import kha.FastFloat;
import iron.math.Vec4;

class Helper {
	/**
		Returns angle in radians between 2 vectors perpendicular to the z axis.
	**/
	public static function getAngle(va:Vec4, vb:Vec4):Float {
		var vn = Vec4.zAxis();
		var dot = va.dot(vb);
		var det = va.x * vb.y * vn.z
			+ vb.x * vn.y * va.z
			+ vn.x * va.y * vb.z
			- va.z * vb.y * vn.x
			- vb.z * vn.y * va.x
			- vn.z * va.y * vb.x;
		return Math.atan2(det, dot);
	}

	/**
		Returns a copy of the current vector summed by delta towards the target vector without passing it.
	**/
	public static function moveTowards(current:Vec4, target:Vec4, delta:FastFloat):Vec4 {
		var v1 = current.clone();
		var v2 = target.clone();

		var diff = v2.clone().sub(v1);
		var length = diff.length();

		if (length <= delta || length == 0.0)
			v1.setFrom(v2);
		else
			v1.add(diff.mult(1.0 / length * delta));

		return v1;
	}

	/**
		Converts an angle in radians to degrees.
		@return angle in degrees
	**/
	inline public static function radToDeg(radians:Float):Float {
		return 180 / Math.PI * radians;
	}

	/**
		Converts an angle in degrees to radians.
		@return angle in radians
	**/
	inline public static function degToRad(degrees:Float):Float {
		return Math.PI / 180 * degrees;
	}

	/**
		Converts a FastFloat to Float.
		@return a Float
	**/
	inline public static function fastFloatToFloat(ff:FastFloat):Float {
		return Std.parseFloat('${ff}');
	}

	/**
		Rounds the precision of a float (default 2).
		@return float with rounded precision
	**/
	public static function roundfp(f:Float, precision = 2):Float {
		f *= std.Math.pow(10, precision);
		return std.Math.round(f) / std.Math.pow(10, precision);
	}

	/**
		Clamps a float within some limits.
		@return same float, min or max if exceeded limits.
	**/
	public static function clamp(f:Float, min:Float, max:Float):Float {
		return f < min ? min : f > max ? max : f;
	}

	/**
		Clamps an integer within some limits.
		@return same integer, min or max if exceeded limits.
	**/
	public static function clampInt(f:Int, min:Int, max:Int):Int {
		return f < min ? min : f > max ? max : f;
	}

	/**
		Convenience function to map a variable from one coordinate space to
		another. Equivalent to unlerp() followed by lerp().
		@param value
		@param leftMin The lower bound of the input coordinate space
		@param leftMax The higher bound of the input coordinate space
		@param rightMin The lower bound of the output coordinate space
		@param rightMax The higher bound of the output coordinate space
		@return Float
	**/
	public static inline function map(value:Float, leftMin:Float, leftMax:Float, rightMin:Float, rightMax:Float):Float {
		return rightMin + (value - leftMin) / (leftMax - leftMin) * (rightMax - rightMin);
	}

	public static inline function mapInt(value:Int, leftMin:Int, leftMax:Int, rightMin:Int, rightMax:Int):Int {
		var result = Std.int(map(value, leftMin, leftMax, rightMin, rightMax));
		return result;
	}

	public static inline function mapClamped(value:Float, leftMin:Float, leftMax:Float, rightMin:Float, rightMax:Float):Float {
		if (value >= leftMax)
			return rightMax;
		if (value <= leftMin)
			return rightMin;
		return map(value, leftMin, leftMax, rightMin, rightMax);
	}

	/**
		Return the sign of the given value represented as `1.0` (positive value)
		or `-1.0` (negative value). The sign of `0` is `0`.
	**/
	public static inline function sign(value:Float):Float {
		if (value == 0)
			return 0;
		return (value < 0) ? -1.0 : 1.0;
	}

	/**
		Return the base-2 logarithm of a number.
	**/
	public static inline function log2(v:Float):Float {
		// 1.44269504089 = 1.0 / ln(2.0)
		return Math.log(v) * 1.44269504089;
	}
}
