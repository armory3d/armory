package armory.logicnode;

import iron.object.Animation;
import iron.object.Object;
import iron.Scene;
import kha.arrays.Float32Array;

class PlayActionFromNode extends LogicNode {

	var animation: Animation;
	var startFrame: Int;
	var endFrame: Int = -1;
	var loop: Bool;
	var reverse: Bool;
	var actionR: String;

	public function new(tree: LogicTree) {
		super(tree);
		tree.notifyOnUpdate(update);
	}
	
	function update() {
		if (animation != null) {
			if (animation.currentFrame() == endFrame) {
				if (loop) animation.setFrame(startFrame);
				else {
					if (!animation.paused) {
						animation.pause();
						runOutput(1);
					}
				}
			}
		}
	}

	override function run(from: Int) {
		var object: Object = inputs[1].get();
		var action: String = inputs[2].get();
		startFrame = inputs[3].get();
		endFrame = inputs[4].get();
		var blendTime: Float = inputs[5].get();
		var speed: Float = inputs[6].get();
		loop = inputs[7].get();
		reverse = inputs[8].get();

		if (object == null) return;
		animation = object.animation;
		if (animation == null) animation = object.getParentArmature(object.name);

		if (reverse){
			var isnew = true;
			actionR = action+'Reverse';

			if (animation.isSkinned){
				for(a in animation.armature.actions)
					if (a.name == actionR) isnew = false;

				if (isnew){
					for(a in animation.armature.actions)
						if(a.name == action)
							animation.armature.actions.push({
								name: actionR,
								bones: a.bones,
								mats: null});

					for(a in animation.armature.actions)
						if(a.name == actionR){
							for(bone in a.bones){
								var val: Array<Float> = [];
								var v = bone.anim.tracks[0];
								var len: Int = v.values.length;
								var l = Std.int(len/16);
								for(i in 0...l)
									for(j in 0...16)
										val.push(v.values[(l-i)*16+j-16]);
								for(i in 0...v.values.length)
									v.values[i] = val[i];
							}

						var castBoneAnim = cast(animation, iron.object.BoneAnimation);
						castBoneAnim.data.geom.actions.set(actionR, a.bones);
						castBoneAnim.data.geom.mats.set(actionR, castBoneAnim.data.geom.mats.get(action));

						for(o in iron.Scene.active.raw.objects)
							if (o.name == object.name) o.bone_actions.push('action_'+o.bone_actions[0].split('_')[1]+'_'+actionR);
						}
				}
			}
			else {
				
				var oaction = null;
				var tracks = [];

				var oactions = animation.getOactions();

				for (a in oactions)
					if (a.objects[0].name == actionR) isnew = false;

				if (isnew){
					for (a in oactions){
						if (a.objects[0].name == action){
							oaction = a.objects[0];
							for(b in a.objects[0].anim.tracks){
								var val: Array<Float> = [];
								for(c in b.values) val.push(c);
								val.reverse();
								var vali = new Float32Array(val.length);
								for(i in 0...val.length) vali[i] = val[i];
								tracks.push({target: b.target, frames: b.frames, values: vali});
							}

						oactions.push({
			                objects: [{name: actionR,
			                anim: {begin: oaction.anim.begin, end: oaction.anim.end, tracks: tracks},
			                type: 'object',
			                data_ref: '',
			                transform: null}]});

						for(o in iron.Scene.active.raw.objects)
							if (o.name == object.name) o.object_actions.push('action_'+actionR);
						}
					}
				}
			}
		}

		animation.play(reverse ? actionR : action, function() {
			runOutput(1);
		}, blendTime, speed, loop);
		animation.update(startFrame * Scene.active.raw.frame_time);

		runOutput(0);

	}
}
