package armory.logicnode;

import iron.math.Quat;
import iron.math.Vec4;
import iron.object.Object;

class GetRootMotionNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	#if arm_skin
	override function get(from: Int):Dynamic {
		var object: Object = inputs[0].get();
		assert(Error, object != null, "Object input must not be null");
		var animation = object.getBoneAnimation(object.uid);
		if(animation == null) return null;
		var rootMotion = animation.rootMotion;
		if(rootMotion == null) return null;
		switch (from) {
			case 0: 
				return rootMotion.name;
			case 1:
				var vel = animation.rootMotionVelocity;
				if(vel != null) return new Vec4().setFrom(vel);
				else return new Vec4();
			case 2:
				var rot = animation.rootMotionRotation;
				if(rot != null) return new Quat().setFrom(rot);
				else return new Quat();
		}
		return null;
	}
	#end
}