package armory.logicnode;
#if arm_skin
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

	var vecSorted = [];
	var sortIndex = [];

	static var totalAnims = 10;
	static var maxAnims = 3;

	#end

	public function new(tree: LogicTree) {
		super(tree);
	}

	#if arm_skin
	public function init(){
		object = inputs[0].get();
		assert(Error, object != null, "The object input not be null");
		animationBone = object.getParentArmature(object.name);
		tempMats = animationBone.initMatsEmpty();
		tempMats2 = animationBone.initMatsEmpty();
		func = blendBones;
		ready = true;
	}

	public function getBlendWeights(): Vec3 {

		var dist = [];
		var vecs = [];
		var weightIndex: Array<WeightIndex> = [];
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

		var i = 0;
		for (vec in vecs){
			weightIndex.push({weight: Vec2.distance(vec, sampleVec), index: i} );
			i++;
		}

		weightIndex.sort(sortCompare);

		vecSorted = [];
		sortIndex = [];
		for (i in 0...maxAnims) {
			var index = weightIndex[i].index;
			sortIndex.push(index);
			vecSorted.push(vecs[index]);
		}
		

		return Animation.getBlend2DWeights(vecSorted, sampleVec);

	}

	public function sortCompare(a: WeightIndex, b: WeightIndex): Int {
		return Reflect.compare(a.weight, b.weight);
	}

	public function blendBones(animMats: Array<Mat4>) {
	
		var anims = inputs[1].get();
		var weights = getBlendWeights();

		var factor1 = weights.y / (weights.x + weights.y);
		var factor2 = (weights.x + weights.y) / (weights.x + weights.y + weights.z);

		anims[sortIndex[0]](tempMats);
		anims[sortIndex[1]](tempMats2);
		anims[sortIndex[2]](animMats);

		animationBone.blendAction(tempMats, tempMats2, tempMats, factor1);
		animationBone.blendAction(animMats, tempMats, animMats, factor2);
	
	}

	override function get(from: Int): Dynamic {

		if(!ready) init();

		return blendBones;
	}
	#end
}

#if arm_skin
typedef WeightIndex = {
	var weight: FastFloat;
	var index: Int;
} 
#end