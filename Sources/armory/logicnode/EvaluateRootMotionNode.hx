package armory.logicnode;

import iron.object.BoneAnimation;
import iron.object.Object;
import iron.math.Mat4;

class EvaluateRootMotionNode extends LogicNode {

    #if arm_skin
    var object: Object;
    var animation: BoneAnimation;
    var ready = false;
    #end

    public var property0: String;

	public function new(tree: LogicTree) {
		super(tree);
	}

    #if arm_skin
    public function init(){
		object = inputs[1].get();
		assert(Error, object != null, "The object input not be null");
		animation = object.getBoneAnimation(object.uid);
        assert(Error, animation != null, "The object does not have an Armature action");
		ready = true;
	}

	override function run(from: Int) {

        if(! ready) init();
        var boneName: String = inputs[3].get();
        var bone = animation.getBone(boneName);
        assert(Error, bone != null, "Bone does not exist");
        var lockX = false;
        var lockY = false;
        var lockZ = false;

        switch (property0){
            case "X" : lockX = true;
            case "Y" : lockY = true;
            case "Z" : lockZ = true;
        }
        animation.setRootMotion(bone, lockX, lockY, lockZ);
    }

    override function get(from:Int):Dynamic {
        if(! ready) init();

        if(animation.getRootMotionBone() == null) run(0);

        return function (animMats: Array<Mat4>) {
            var boneName: String = inputs[3].get();
            inputs[2].get()(animMats);
            animation.evaluateRootMotion(animMats);
        };
    }

    #end
}