package armory.logicnode;

#if arm_skin
import armory.object.AnimationExtension;
import kha.FastFloat;
import iron.math.Mat4;
import iron.math.Vec3;
import iron.math.Vec2;
import iron.object.Object;
import iron.object.Animation;
import iron.object.BoneAnimation;
#end

class BlendSpaceNode extends LogicNode {

	
	public var property0: Array<Float>;
	public var property1: Array<Bool>;
	public var property2: Bool;
	#if arm_skin
	var value: Dynamic;
	var object: Object;
	var animationBone: BoneAnimation;
	var tempMats: Array<Mat4>;
	var tempMats2: Array<Mat4>;
	var ready = false;
	var func: Dynamic = null;
	static var totalAnims = 10;
	#end

	public function new(tree: LogicTree) {
		super(tree);
	}

	#if arm_skin
	public function init(){
		object = inputs[0].get();
		assert(Error, object != null, "The object input not be null");
		animationBone = object.getBoneAnimation(object.uid);
		tempMats = animationBone.initMatsEmpty();
		tempMats2 = animationBone.initMatsEmpty();
		func = blendBones;
		ready = true;
	}

	public function getBlendWeights(): Map<Int, FastFloat> {
		var vecs = [];
		var sampleVec = new Vec2();

		for(i in 0...totalAnims){

			if(property1[i]) vecs.push(new Vec2(property0[i * 2], property0[i * 2 + 1]));
		}

		if(property2) {
			sampleVec.set(property0[2 * totalAnims], property0[2 * totalAnims + 1]);
		}
		else {
			sampleVec.set(inputs[2].get(), inputs[3].get());
		}

		return AnimationExtension.getBlend2DWeights(vecs, sampleVec);

	}

	public function blendBones(animMats: Array<Mat4>) {
		var anims = inputs[1].get();
		var weightsIndex = getBlendWeights();

		var indices: Array<Int> = [];
		var weights: Array<FastFloat> = [];
		
		for(key in weightsIndex.keys()){
			indices.push(key);
			weights.push(weightsIndex.get(key));
		}

		var factor1 = weights[1] / (weights[0] + weights[1]);
		var factor2 = (weights[0] + weights[1]) / (weights[0] + weights[1] + weights[2]);

		anims[indices[0]](tempMats);
		anims[indices[1]](tempMats2);
		anims[indices[2]](animMats);

		animationBone.blendAction(tempMats, tempMats2, tempMats, factor1);
		animationBone.blendAction(animMats, tempMats, animMats, factor2);
	
	}

	override function get(from: Int): Dynamic {
		if(!ready) init();

		return blendBones;
	}
	#end
}