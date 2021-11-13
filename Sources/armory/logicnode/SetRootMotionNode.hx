package armory.logicnode;

import iron.object.Object;

class SetRootMotionNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
        var object: Object = inputs[1].get();
        var boneName: String = inputs[2].get();
        assert(Error, object != null, "Object input must not be null");
        var animation = object.getParentArmature(object.name);
        if(animation == null) return;
        var bone = animation.getBone(boneName);
        assert(Error, bone != null, "Bone does not exist");
        animation.setRootMotion(bone);

        runOutput(0);

    }
}