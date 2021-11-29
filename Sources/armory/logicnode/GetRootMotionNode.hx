package armory.logicnode;

import iron.math.Vec4;
import iron.object.Object;

class GetRootMotionNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

    #if arm_skin
    override function get(from:Int):Dynamic {
        var object: Object = inputs[0].get();
        assert(Error, object != null, "Object input must not be null");
        var animation = object.getParentArmature(object.name);
        if(animation == null) return null;
        var rootMotion = animation.getRootMotionBone();
        if(rootMotion == null) return null;
        switch (from) {
            case 0: 
                return rootMotion.name;
            case 1:
                var vel = animation.getRootMoptionVelocity();
                if(vel != null) return new Vec4().setFrom(vel);
                else return new Vec4();
        }
        return null;

    }
    #end
}