package iron.math;

import kha.FastFloat;

class Mat3 {

	public var self: kha.math.FastMatrix3;

	public inline function new(_00: FastFloat, _10: FastFloat, _20: FastFloat,
							   _01: FastFloat, _11: FastFloat, _21: FastFloat,
							   _02: FastFloat, _12: FastFloat, _22: FastFloat) {
		self = new kha.math.FastMatrix3(_00, _10, _20, _01, _11, _21, _02, _12, _22);
	}

	public static inline function identity(): Mat3 {
		return new Mat3(
			1, 0, 0,
			0, 1, 0,
			0, 0, 1
		);
	}

	public inline function setFrom4(m: Mat4) {
		_00 = m._00;
		_01 = m._01;
		_02 = m._02;
		_10 = m._10;
		_11 = m._11;
		_12 = m._12;
		_20 = m._20;
		_21 = m._21;
		_22 = m._22;
	}

	public var _00(get, set): FastFloat; inline function get__00(): FastFloat { return self._00; } inline function set__00(f: FastFloat): FastFloat { return self._00 = f; }
	public var _01(get, set): FastFloat; inline function get__01(): FastFloat { return self._01; } inline function set__01(f: FastFloat): FastFloat { return self._01 = f; }
	public var _02(get, set): FastFloat; inline function get__02(): FastFloat { return self._02; } inline function set__02(f: FastFloat): FastFloat { return self._02 = f; }
	public var _10(get, set): FastFloat; inline function get__10(): FastFloat { return self._10; } inline function set__10(f: FastFloat): FastFloat { return self._10 = f; }
	public var _11(get, set): FastFloat; inline function get__11(): FastFloat { return self._11; } inline function set__11(f: FastFloat): FastFloat { return self._11 = f; }
	public var _12(get, set): FastFloat; inline function get__12(): FastFloat { return self._12; } inline function set__12(f: FastFloat): FastFloat { return self._12 = f; }
	public var _20(get, set): FastFloat; inline function get__20(): FastFloat { return self._20; } inline function set__20(f: FastFloat): FastFloat { return self._20 = f; }
	public var _21(get, set): FastFloat; inline function get__21(): FastFloat { return self._21; } inline function set__21(f: FastFloat): FastFloat { return self._21 = f; }
	public var _22(get, set): FastFloat; inline function get__22(): FastFloat { return self._22; } inline function set__22(f: FastFloat): FastFloat { return self._22 = f; }
}
