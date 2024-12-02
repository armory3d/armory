package iron.object;

import kha.FastFloat;
import kha.arrays.Uint32Array;
import iron.math.Vec4;
import iron.math.Mat4;
import iron.math.Quat;
import iron.data.SceneFormat;

class ObjectAnimation extends Animation {

	public var object: Object;
	public var oactions: Array<TSceneFormat>;
	var oaction: TObj;
	var s0: FastFloat = 0.0;
	var bezierFrameIndex = -1;

	public function new(object: Object, oactions: Array<TSceneFormat>) {
		this.object = object;
		this.oactions = oactions;
		isSkinned = false;
		super();
	}

	function getAction(action: String): TObj {
		for (a in oactions) if (a != null && a.objects[0].name == action) return a.objects[0];
		return null;
	}

	override public function play(action = "", onComplete: Void->Void = null, blendTime = 0.0, speed = 1.0, loop = true) {
		super.play(action, onComplete, blendTime, speed, loop);
		if (this.action == "" && oactions[0] != null) this.action = oactions[0].objects[0].name;
		oaction = getAction(this.action);
		if (oaction != null) {
			isSampled = oaction.sampled != null && oaction.sampled;
		}
	}

	override public function update(delta: FastFloat) {
		if (!object.visible || object.culled || oaction == null) return;

		#if arm_debug
		Animation.beginProfile();
		#end

		super.update(delta);
		if (paused) return;
		if (!isSkinned) updateObjectAnim();

		#if arm_debug
		Animation.endProfile();
		#end
	}

	function updateObjectAnim() {
		updateTransformAnim(oaction.anim, object.transform);
		object.transform.buildMatrix();
	}

	inline function interpolateLinear(t: FastFloat, t1: FastFloat, t2: FastFloat, v1: FastFloat, v2: FastFloat): FastFloat {
		var s = (t - t1) / (t2 - t1);
		return (1.0 - s) * v1 + s * v2;
	}

	// inline function interpolateTcb(): FastFloat { return 0.0; }

	override function isTrackEnd(track: TTrack): Bool {
		return speed > 0 ?
			frameIndex >= track.frames.length - 2 :
			frameIndex <= 0;
	}

	inline function checkFrameIndexT(frameValues: Uint32Array, t: FastFloat): Bool {
		return speed > 0 ?
			frameIndex < frameValues.length - 2 && t > frameValues[frameIndex + 1] * frameTime :
			frameIndex > 1 && t > frameValues[frameIndex - 1] * frameTime;
	}

	@:access(iron.object.Transform)
	function updateTransformAnim(anim: TAnimation, transform: Transform) {
		if (anim == null) return;

		var total = anim.end * frameTime - anim.begin * frameTime;

		if (anim.has_delta) {
			var t = transform;
			if (t.dloc == null) {
				t.dloc = new Vec4();
				t.drot = new Quat();
				t.dscale = new Vec4();
			}
			t.dloc.set(0, 0, 0);
			t.dscale.set(0, 0, 0);
			t._deulerX = t._deulerY = t._deulerZ = 0.0;
		}

		for (track in anim.tracks) {

			if (frameIndex == -1) rewind(track);
			var sign = speed > 0 ? 1 : -1;

			// End of current time range
			var t = time + anim.begin * frameTime;
			while (checkFrameIndexT(track.frames, t)) frameIndex += sign;

			// No data for this track at current time
			if (frameIndex >= track.frames.length) continue;

			// End of track
			if (time > total) {
				if (onComplete != null) onComplete();
				if (loop) rewind(track);
				else {
					frameIndex -= sign;
					paused = true;
				}
				return;
			}

			var ti = frameIndex;
			var t1 = track.frames[ti] * frameTime;
			var t2 = track.frames[ti + sign] * frameTime;
			var v1 = track.values[ti];
			var v2 = track.values[ti + sign];

			var value = interpolateLinear(t, t1, t2, v1, v2);

			switch (track.target) {
				case "xloc": transform.loc.x = value;
				case "yloc": transform.loc.y = value;
				case "zloc": transform.loc.z = value;
				case "xrot": transform.setRotation(value, transform._eulerY, transform._eulerZ);
				case "yrot": transform.setRotation(transform._eulerX, value, transform._eulerZ);
				case "zrot": transform.setRotation(transform._eulerX, transform._eulerY, value);
				case "qwrot": transform.rot.w = value;
				case "qxrot": transform.rot.x = value;
				case "qyrot": transform.rot.y = value;
				case "qzrot": transform.rot.z = value;
				case "xscl": transform.scale.x = value;
				case "yscl": transform.scale.y = value;
				case "zscl": transform.scale.z = value;
				// Delta
				case "dxloc": transform.dloc.x = value;
				case "dyloc": transform.dloc.y = value;
				case "dzloc": transform.dloc.z = value;
				case "dxrot": transform._deulerX = value;
				case "dyrot": transform._deulerY = value;
				case "dzrot": transform._deulerZ = value;
				case "dqwrot": transform.drot.w = value;
				case "dqxrot": transform.drot.x = value;
				case "dqyrot": transform.drot.y = value;
				case "dqzrot": transform.drot.z = value;
				case "dxscl": transform.dscale.x = value;
				case "dyscl": transform.dscale.y = value;
				case "dzscl": transform.dscale.z = value;
			}
		}
	}

	override public function totalFrames(): Int {
		if (oaction == null || oaction.anim == null) return 0;
		return oaction.anim.end - oaction.anim.begin;
	}
}
