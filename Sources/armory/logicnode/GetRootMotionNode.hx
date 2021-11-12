package armory.logicnode;

import iron.math.Vec4;
import iron.object.Object;

class GetRootMotionNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

    override function get(from:Int):Dynamic {
        var object: Object = inputs[0].get();
        assert(Error, object != null, "Object input must not be null");
        var animation = object.getParentArmature(object.name);
        if(animation == null) return null;
        assert(Error, animation.getRootMotionBone() != null, "Armature does not have root motion");
        switch (from) {
            case 0: return animation.getRootMotionBone().name;
            case 1: return new Vec4().setFrom(animation.getRootMoptionVelocity());
        }
        return null;

    }
}