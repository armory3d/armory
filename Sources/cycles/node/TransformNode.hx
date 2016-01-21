package cycles.node;

import lue.math.Mat4;
import lue.math.Vec3;
import lue.math.Quat;

class TransformNode extends Node {

	public static inline var _position = 0; // Vector
	public static inline var _rotation = 1; // Vector
	public static inline var _scale = 2; // Vector

	public var transform:lue.node.Transform;
	
	var matrix:Mat4;
	var pos:Vec3;
	var rot:Quat;
	var scale:Vec3;

	static var temp = Mat4.identity();

	public function new() {
		super();

		matrix = Mat4.identity();
		pos = new Vec3();
		rot = new Quat();
		scale = new Vec3();
	}

	public override function inputChanged() {
		// Build matrix
		pos.set(inputs[_position].inputs[VectorNode._x].f,
				inputs[_position].inputs[VectorNode._y].f,
				inputs[_position].inputs[VectorNode._z].f);

		rot.initRotate(inputs[_rotation].inputs[VectorNode._x].f,
					   inputs[_rotation].inputs[VectorNode._y].f,
					   inputs[_rotation].inputs[VectorNode._z].f);

		scale.set(inputs[_scale].inputs[VectorNode._x].f,
				  inputs[_scale].inputs[VectorNode._y].f,
				  inputs[_scale].inputs[VectorNode._z].f);

		matrix.setIdentity();
		matrix.scale(scale);
		rot.saveToMatrix(temp);
		matrix.mult(temp);
		//matrix.translate(pos.x, pos.y, pos.z);
		matrix._30 = pos.x;
		matrix._31 = pos.y;
		matrix._32 = pos.z;

		// Append to transform
		transform.append = matrix;
		transform.dirty = true;

		super.inputChanged();
	}

	public static function create(positionX:Float, positionY:Float, positionZ:Float,
								  rotationX:Float, rotationY:Float, rotationZ:Float,
								  scaleX:Float, scaleY:Float, scaleZ:Float):TransformNode {
		var n = new TransformNode();
		n.inputs.push(VectorNode.create(positionX, positionY, positionZ));
		n.inputs.push(VectorNode.create(rotationX, rotationY, rotationZ));
		n.inputs.push(VectorNode.create(scaleX, scaleY, scaleZ));
		return n;
	}
}
