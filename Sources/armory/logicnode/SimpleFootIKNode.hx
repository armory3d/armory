package armory.logicnode;

import iron.data.SceneFormat.TObj;
import armory.object.AnimationExtension;
import haxe.display.Protocol.InitializeParams;
import kha.FastFloat;
import iron.object.Object;
import iron.object.BoneAnimation;
import iron.math.Vec4;
import iron.math.Mat4;

class SimpleFootIKNode extends LogicNode {

	#if arm_skin
	var object: Object; //0
	var leftBoneName: String; //2
	var rightBoneName: String; //3
	var leftHitPoint: Null<Float>; //4
	var rightHitPoint: Null<Float>; //5
	var heightOffset: Float; //6
	var footOffset: Null<Float>; //7
	var offsetThreshold: Float; //8
	var interpSpeed: Float; //9
	var layerMask: Null<Int>; //10
	var influence: FastFloat;
	var leftPole: Vec4 = null; 
	var rightPole: Vec4 = null;
	var leftFootDir: Vec4;
	var rightFootDir: Vec4;
	var scanHeight: FastFloat;
	var scanDepth: FastFloat;
	var collisionMask: Int;
	var footIK: SimpleBiPedalIK;
	var leftBone: TObj;
	var rightBone: TObj;

	public var property0: String;
	public var property1: String;

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
		animation = object.getBoneAnimation(object.uid);
		assert(Error, animation != null, "The object does not have armatureanimation");
		leftBoneName = property0;
		rightBoneName = property1;
		leftBone = animation.getBone(leftBoneName);
		rightBone = animation.getBone(rightBoneName);
		footIK = new SimpleBiPedalIK(object, animation, leftBoneName, rightBoneName);
		ready = true;

	}
	#end

	override function get(from: Int): Dynamic {

		#if arm_skin
		return function (animMats: Array<Mat4>) {
			if(! ready) init();

			inputs[1].get()(animMats);
			scanHeight = inputs[2].get();
			scanDepth = inputs[3].get();
			collisionMask = inputs[4].get();
			heightOffset = inputs[5].get();
			footOffset = inputs[6].get();
			offsetThreshold = inputs[7].get();
			interpSpeed = inputs[8].get();
			layerMask = inputs[9].get();
			influence = inputs[10].get();
			var usePoles = inputs[11].get();
			var rotateFoot = inputs[12].get();
			var vecArray: Array<Vec4> = inputs[13].get();
			if(usePoles) {
				leftPole = new Vec4().setFrom(vecArray[0]);
				rightPole =  new Vec4().setFrom(vecArray[1]);
			}
			else {
				leftPole = null;
				rightPole = null;
			}
			if(rotateFoot){
				leftFootDir = vecArray[2];
				rightFootDir = vecArray[3];
			}
			/* leftPole = inputs[14].get();
			rightPole = inputs[15].get(); */
			
			

			var leftBoneLoc = animation.getAbsWorldMat(leftBone, animMats).getLoc();
			var rightBoneLoc = animation.getAbsWorldMat(rightBone, animMats).getLoc();

			var physics = armory.trait.physics.PhysicsWorld.active;
			var top = new Vec4().setFrom(leftBoneLoc).add(new Vec4(0, 0, scanHeight));
			var bottom = new Vec4().setFrom(leftBoneLoc).sub(new Vec4(0, 0, scanDepth));
			var rayLeft = physics.rayCast(top, bottom, collisionMask);
			if(rayLeft == null) return;
			var leftPos = new Vec4().setFrom(rayLeft.pos);
			var leftNorm = new Vec4().setFrom(rayLeft.normal);

			top = new Vec4().setFrom(rightBoneLoc).add(new Vec4(0, 0, scanHeight));
			bottom = new Vec4().setFrom(rightBoneLoc).sub(new Vec4(0, 0, scanDepth));
			var rayRight = physics.rayCast(top, bottom, collisionMask);
			if(rayRight == null) return;
			var rightPos =  new Vec4().setFrom(rayRight.pos);
			var rightNorm = new Vec4().setFrom(rayRight.normal);

			trace("Left Pole = " + leftPole.toString());
			trace("Right Pole = " + rightPole.toString());
			
			footIK.updatePosition(animMats, heightOffset, footOffset, leftPos, rightPos, offsetThreshold, interpSpeed, leftPole, rightPole, influence, layerMask);

			if(! rotateFoot) return;
			trace("left norm =" + leftNorm.toString());
			trace("Right norm =" + rightNorm.toString());
			footIK.updateRotation(animMats, leftFootDir, rightFootDir, leftNorm, rightNorm);
			
		}
		#end
	}
}
