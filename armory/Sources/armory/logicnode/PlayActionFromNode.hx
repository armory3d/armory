package armory.logicnode;

import iron.object.Animation;
import iron.object.Object;
import iron.Scene;
import kha.arrays.Float32Array;
import iron.object.ObjectAnimation;

class PlayActionFromNode extends LogicNode {

	var animation: Animation;
	var startFrame: Int;
	var endFrame: Int = -1;
	var loop: Bool;
	var reverse: Bool;
	var action: String;
	var actionR: String;

	public function new(tree: LogicTree) {
		super(tree);
		tree.notifyOnUpdate(update);
	}
	
	function update() {
		if (animation != null && action == animation.action) {
			if (animation.currentFrame() == endFrame-1) {
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
		action = inputs[2].get();
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
						if(a.name == action){
							var bones = [];
							var cn = [];
							for(bone in a.bones){
								var v = bone.anim.tracks[0];
								var len: Int = v.values.length;
								var val = new Float32Array(len);
								var l = Std.int(len/16);
								for(i in 0...l)
									for(j in 0...16){
										val[i*16+j] = v.values[(l-i)*16+j-16];
									}

								if (bone.children != null){
									var cdn = [];
									for (child in bone.children)
										cdn.push(child.name);
									cn.push(cdn);
								} else cn.push(null);

								var a: iron.data.SceneFormat.TObj = {
									type : bone.type,
							        name : bone.name,
							        transform : {
							        		//target : null,
							                values : bone.transform.values
							        },
							        anim : {
							                tracks : [{
						                                target : v.target,
						                                frames : v.frames,
						                                values : val,
						                                ref_values : null
							                        }]//,
							                //begin : null,
							                //end : null,
							                //has_delta : null,
							                //marker_frames : null,
							                //marker_names : null
							        },
							        children : bone.children,
							        data_ref : null
							    	}

								if (bone.parent != null){
									a.parent = bone.parent;
								}

						    	bones.push(a);
							}

							for (i in 0...bones.length){
								var cd = [];
								if (cn[i] != null)
									for (name in cn[i])
										for (bone in bones)
											if (bone.name == name)
												cd.push(bone);
								bones[i].children = cd;
							}
							
							for (i in 0...bones.length){
								if (bones[i].parent != null)
									for (bone in bones)
										if (bone.name == bones[i].parent.name)
											bones[i].parent = bone;

							}

							animation.armature.actions.push({
								name: actionR,
								bones: bones,
								mats: null});

							var mats: Array<iron.math.Mat4> = [];
							for (bone in a.bones) mats.push(iron.math.Mat4.fromFloat32Array(bone.transform.values));

							var castBoneAnim = cast(animation, iron.object.BoneAnimation);
							castBoneAnim.data.geom.actions.set(actionR, bones);
							castBoneAnim.data.geom.mats.set(actionR, mats);

							for(o in iron.Scene.active.raw.objects)
								if (o.name == object.name) o.bone_actions.push('action_'+o.bone_actions[0].split('_')[1]+'_'+actionR);
						}
				}
			}
			else {
				
				var oaction = null;
				var tracks: Array<iron.data.SceneFormat.TTrack> = [];

				var oactions = cast(animation, ObjectAnimation).oactions;

				for (a in oactions)
					if (a != null && a.objects[0].name == actionR) isnew = false;

				if (isnew){
					for (a in oactions){
						if (a != null && a.objects[0].name == action){
							oaction = a.objects[0];
							for(b in a.objects[0].anim.tracks){
								var val: Array<Float> = [];
								for(c in b.values) val.unshift(c);
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
