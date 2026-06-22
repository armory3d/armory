package armory.logicnode;

import iron.math.Mat4;

class TransformMathNode extends LogicNode {

	public var property0: String;
	var m = Mat4.identity();

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function get(from: Int): Dynamic {
		var m1: Mat4 = inputs[0].get();
		var m2: Mat4 = inputs[1].get();

		if (m1 == null || m2 == null) return null;

		m.setFrom(m1);
		transformMath(m, m2);

		return m;
	}

	public static function transformMath(m1: Mat4, m2: Mat4) {
		var a00 = m1._00; var a01 = m1._01; var a02 = m1._02;
		var a10 = m1._10; var a11 = m1._11; var a12 = m1._12;
		var a20 = m1._20; var a21 = m1._21; var a22 = m1._22;

		var b0 = m2._00; var b1 = m2._10; var b2 = m2._20;
		m1._00 = a00 * b0 + a01 * b1 + a02 * b2;
		m1._10 = a10 * b0 + a11 * b1 + a12 * b2;
		m1._20 = a20 * b0 + a21 * b1 + a22 * b2;

		b0 = m2._01; b1 = m2._11; b2 = m2._21;
		m1._01 = a00 * b0 + a01 * b1 + a02 * b2;
		m1._11 = a10 * b0 + a11 * b1 + a12 * b2;
		m1._21 = a20 * b0 + a21 * b1 + a22 * b2;

		b0 = m2._02; b1 = m2._12; b2 = m2._22;
		m1._02 = a00 * b0 + a01 * b1 + a02 * b2;
		m1._12 = a10 * b0 + a11 * b1 + a12 * b2;
		m1._22 = a20 * b0 + a21 * b1 + a22 * b2;

		b0 = m2._03; b1 = m2._13; b2 = m2._23;
		m1._03 = a00 * b0 + a01 * b1 + a02 * b2;
		m1._13 = a10 * b0 + a11 * b1 + a12 * b2;
		m1._23 = a20 * b0 + a21 * b1 + a22 * b2;

		m1._30 += m2._30;
		m1._31 += m2._31;
		m1._32 += m2._32;
	}
}
