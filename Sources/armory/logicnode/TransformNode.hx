package armory.logicnode;

import iron.math.Mat4;
import iron.math.Vec4;
import iron.math.Quat;
import iron.object.Transform;

class TransformNode extends Node {

	public static inline var _position = 0; // Vector
	public static inline var _rotation = 1; // Vector
	public static inline var _scale = 2; // Vector
	
	public var matrix:Mat4;
	
	var pos:Vec4;
	var rot:Quat;
	var scale:Vec4;

	public function new() {
		super();

		matrix = Mat4.identity();
		pos = new Vec4();
		rot = new Quat();
		scale = new Vec4();
	}

	public override function inputChanged() {
		// Build matrix
		pos.set(inputs[_position].inputs[VectorNode._x].f,
				inputs[_position].inputs[VectorNode._y].f,
				inputs[_position].inputs[VectorNode._z].f);

		rot.fromEuler(inputs[_rotation].inputs[VectorNode._x].f,
					  inputs[_rotation].inputs[VectorNode._y].f,
					  inputs[_rotation].inputs[VectorNode._z].f);

		scale.set(inputs[_scale].inputs[VectorNode._x].f,
				  inputs[_scale].inputs[VectorNode._y].f,
				  inputs[_scale].inputs[VectorNode._z].f);

		matrix.compose(pos, rot, scale);

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
