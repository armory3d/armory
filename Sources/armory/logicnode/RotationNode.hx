package armory.logicnode;

import iron.math.Vec4;
import iron.math.Quat;
import kha.FastFloat;

class RotationNode extends LogicNode {

        static inline var toRAD: FastFloat = 0.017453292519943295;  // 180/pi
	
	public var property0: String;  // type of input (EulerAngles, AxisAngle, Quaternion)
	public var property1: String;  // angle unit (Deg, Rad)
	public var property2: String;  // euler order (XYZ, XZY, etc…)

	public var value: Quat;
	//var input0_cache: Vec4 = new Vec4();
	//var input1_cache: Float = 0;
	var input_length: Int = 0;
	
	public function new(tree: LogicTree, x: Null<Float> = null,
	                                     y: Null<Float> = null,
					     z: Null<Float> = null,
					     w: Null<Float> = null
					     ) {
		super(tree);
		this.value = new Quat();
		if (x!=null) this.value.set(x,y,z,w);
		for (input in inputs) {
		    if (input !=null)
		        this.input_length +=1;
		    else
		        break;
		}
	}

	override function get(from: Int): Dynamic {
	        //var inp0 = inputs[0].get();
		//var inp
	        //if (inputs[0].get())
		if (inputs.length == 0){
			return this.value;
		}
	
		switch (property0){
		case "Quaternion": {
			if (inputs[0]!=null && inputs[1]!=null) {
				var vect: Vec4 = inputs[0].get();
				value.x = vect.x;
				value.y = vect.y;
				value.z = vect.z;
				value.w = inputs[1].get();
			}
		}
		case "AxisAngle": {
			if (inputs[0]!=null && inputs[1]!=null){
				var vec: Vec4 = inputs[0].get();
				var angle: FastFloat = inputs[1].get();
				if (property1=="Deg")
					angle *= toRAD;
				value.fromAxisAngle(vec, angle);
			}
		}
		case "EulerAngles": {
			if (inputs[0] != null){
				var vec: Vec4 = new Vec4().setFrom(inputs[0].get());
				if (property1=="Deg"){
					vec.x *= toRAD;
					vec.y *= toRAD;
				     	vec.z *= toRAD;
				}
				this.value.fromEulerOrdered(vec, property2);
			}
		}
		default: {
		    return property0;
		}
		}
		return this.value;
	}

	override function set(value: Dynamic) {
		switch (property0){
		case "Quaternion": {
			if (input_length>1) {
				var vect = new Vec4();
				vect.x = value.x;
				vect.y = value.y;
				vect.z = value.z;
				inputs[0].set(vect);
				inputs[1].set(value.w);
			}
		}
		case "AxisAngle": {
			if (input_length>1){
				var vec = new Vec4();
				var angle = this.value.toAxisAngle(vec);
				if (property1=="Deg")
					angle /= toRAD;
				inputs[0].set(vec);
				inputs[1].set(angle);

			}
		}
		case "EulerAngles": {
			if (input_length>0){
			  var vec:Vec4 = value.toEulerOrdered(property2);
				if (property1=="Deg"){
					vec.x /= toRAD;
					vec.y /= toRAD;
				     	vec.z /= toRAD;
				}
				inputs[0].set(vec);
			}
		}
		}
	        if (input_length > 0){
			// NYI
		}else this.value=value;
	}
}
