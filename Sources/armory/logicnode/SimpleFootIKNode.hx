package armory.logicnode;

import haxe.display.Protocol.InitializeParams;
import kha.FastFloat;
import iron.object.Object;
import iron.object.BoneAnimation;
import iron.math.Vec4;
import iron.math.Mat4;

class SimpleFootIKNode extends LogicNode {

	#if arm_skin
	var object: Object; //0
	var animMats: Array<Mat4>; //1
	var leftBoneName: String; //2
	var rightBoneName: String; //3
	var leftHitPoint: Null<Float>; //4
	var rightHitPoint: Null<Float>; //5
	var hipHeight: Float; //6
	var footOffset: Float; //7
	var footOffsetThreshold: Float; //8
	var interpSpeed: Float; //9
	var layerMask: Null<Int>; //10
	var currentLeftZ: Null<Float> = null;
	var currentRightZ: Null<Float> = null;

	var animation: BoneAnimation;
	var ready = false;
	#end
	
	public function new(tree: LogicTree) {
		super(tree);
	}

	#if arm_skin
	public function init(){

		object = inputs[0].get();
		assert(Error, object != null, "The object input not be null");
		animation = object.getParentArmature(object.name);
		assert(Error, animation != null, "The object does not have armatureanimation");
		ready = true;

	}

	override function get(from: Int): Dynamic {

		return function (animMats: Array<Mat4>) {
			if(! ready) init();

			inputs[1].get()(animMats);
			leftBoneName = inputs[2].get();
			rightBoneName = inputs[3].get();
			leftHitPoint = inputs[4].get();
			rightHitPoint = inputs[5].get();
			hipHeight = inputs[6].get();
			footOffset = inputs[7].get();
			footOffsetThreshold = inputs[8].get();
			interpSpeed = inputs[9].get();
			layerMask = inputs[10].get();

			var leftBone = animation.getBone(leftBoneName);
			var rightBone = animation.getBone(rightBoneName);
  
			// get bone world location
			var leftLoc = animation.getAbsWorldMat(leftBone, animMats).getLoc();
			var rightLoc = animation.getAbsWorldMat(rightBone, animMats).getLoc();

			// get lowest hit point
			var hitPoint = 0.0;
			if(leftHitPoint == null || rightHitPoint == null) {
				currentLeftZ = null;
				currentRightZ = null;
				return;
			}
			hitPoint = Math.min(rightHitPoint, leftHitPoint);

			// get current armature height
			var currentPos = new Vec4().setFrom(object.transform.world.getLoc());
			var currentHeight = currentPos.z;

			// interpolate z movement
			currentPos.z = deltaInterpolate(currentHeight, hitPoint + hipHeight, interpSpeed);

			// set new armature height
			setWorldLocation(currentPos);
			
			var deltaFeetDistance = Math.abs(leftLoc.z - rightLoc.z);
			if(deltaFeetDistance > footOffsetThreshold) {
				currentLeftZ = null;
				currentRightZ = null;
				return;
			}

			//Perform IK on left leg
			if(currentLeftZ == null) currentLeftZ = leftLoc.z;
			currentLeftZ = deltaInterpolate(currentLeftZ, leftHitPoint, interpSpeed);
			leftLoc.z = currentLeftZ /* + footOffset */;
			animation.solveTwoBoneIKBlend(animMats, leftBone.parent, leftLoc, null, 
										  0.0, 1.0, layerMask, 0.1);

			//Perform IK on right leg
			if(currentRightZ == null) currentRightZ = rightLoc.z;
			currentRightZ = deltaInterpolate(currentRightZ, rightHitPoint, interpSpeed);
			rightLoc.z = currentRightZ /* + footOffset */;
			animation.solveTwoBoneIKBlend(animMats, rightBone.parent, rightLoc, null, 
										  0.0, 1.0, layerMask, 0.1);
		}
	}

	function deltaInterpolate(from: Float, to: Float, interpSpeed: Float): Float{

		var sign = to > from ? 1.0 : -1.0;
		var value = from + interpSpeed * sign;
		var min = Math.min(to, from);
		var max = Math.max(to, from);
		return value < min ? min : value > max ? max : value;
	}

	function setWorldLocation(currentPos: Vec4){
		var loc = new Vec4().setFrom(currentPos);
		loc.sub(object.parent.transform.world.getLoc()); // Remove parent location influence
		// Convert vec to parent local space
		var dotX = loc.dot(object.parent.transform.right());
		var dotY = loc.dot(object.parent.transform.look());
		var dotZ = loc.dot(object.parent.transform.up());
		var vec = new Vec4(dotX, dotY, dotZ);
		object.transform.loc.setFrom(vec);
		object.transform.buildMatrix();
	}
	#end
}
