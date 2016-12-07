package armory.logicnode;

import iron.math.Mat4;
import iron.math.Vec4;
import iron.math.Quat;
import iron.object.Transform;

class TransformNode extends Node {

	public static inline var _location = 0; // Vector
	public static inline var _rotation = 1; // Vector
	public static inline var _scale = 2; // Vector
	
	public var matrix:Mat4 = null;
	
	var loc:Vec4 = null;
	var rot:Quat = null;
	var scale:Vec4 = null;

	var buildMatrix:Bool;

	public function new(buildMatrix = true) {
		super();

		this.buildMatrix = buildMatrix;
		if (buildMatrix) {
			matrix = Mat4.identity();
			loc = new Vec4();
			rot = new Quat();
			scale = new Vec4();
		}
	}

	public override function inputChanged() {
		if (buildMatrix) {
			loc.set(inputs[_location].inputs[VectorNode._x].val,
					inputs[_location].inputs[VectorNode._y].val,
					inputs[_location].inputs[VectorNode._z].val);

			rot.fromEuler(inputs[_rotation].inputs[VectorNode._x].val,
						  inputs[_rotation].inputs[VectorNode._y].val,
						  inputs[_rotation].inputs[VectorNode._z].val);

			scale.set(inputs[_scale].inputs[VectorNode._x].val,
					  inputs[_scale].inputs[VectorNode._y].val,
					  inputs[_scale].inputs[VectorNode._z].val);

			matrix.compose(loc, rot, scale);
		}

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
