package iron.object;

import kha.FastFloat;
import kha.arrays.Uint32Array;
import iron.math.Vec4;
import iron.math.Mat4;
import iron.math.Quat;
import iron.data.SceneFormat;

class Animation {

	public var isSkinned: Bool;
	public var isSampled: Bool;
	public var action = "";
	#if arm_skin
	public var armature: iron.data.Armature; // Bone
	#end

	// Lerp
	static var m1 = Mat4.identity();
	static var m2 = Mat4.identity();
	static var vpos = new Vec4();
	static var vpos2 = new Vec4();
	static var vscl = new Vec4();
	static var vscl2 = new Vec4();
	static var q1 = new Quat();
	static var q2 = new Quat();
	static var q3 = new Quat();
	static var vp = new Vec4();
	static var vs = new Vec4();

	public var time: FastFloat = 0.0;
	public var speed: FastFloat = 1.0;
	public var loop = true;
	public var frameIndex = 0;
	public var onComplete: Void->Void = null;
	public var paused = false;
	var frameTime: FastFloat = 1 / 60;

	var blendTime: FastFloat = 0.0;
	var blendCurrent: FastFloat = 0.0;
	var blendAction = "";
	var blendFactor: FastFloat = 0.0;

	var lastFrameIndex = -1;
	var markerEvents: Map<String, Array<Void->Void>> = null;

	function new() {
		Scene.active.animations.push(this);
		if (Scene.active.raw.frame_time != null) {
			frameTime = Scene.active.raw.frame_time;
		}
		play();
	}

	public function play(action = "", onComplete: Void->Void = null, blendTime = 0.0, speed = 1.0, loop = true) {
		if (blendTime > 0) {
			this.blendTime = blendTime;
			this.blendCurrent = 0.0;
			this.blendAction = this.action;
			frameIndex = 0;
			time = 0.0;
		}
		else frameIndex = -1;
		this.action = action;
		this.onComplete = onComplete;
		this.speed = speed;
		this.loop = loop;
		paused = false;
	}

	public function blend(action1: String, action2: String, factor: FastFloat) {
		blendTime = 1.0; // Enable blending
		blendFactor = factor;
	}

	public function pause() {
		paused = true;
	}

	public function resume() {
		paused = false;
	}

	public function remove() {
		Scene.active.animations.remove(this);
	}

	public function update(delta: FastFloat) {
		if (paused || speed == 0.0) return;
		time += delta * speed;

		if (blendTime > 0 && blendFactor == 0) {
			blendCurrent += delta;
			if (blendCurrent >= blendTime) blendTime = 0.0;
		}
	}

	function isTrackEnd(track: TTrack): Bool {
		return speed > 0 ?
			frameIndex >= track.frames.length - 1 :
			frameIndex <= 0;
	}

	inline function checkFrameIndex(frameValues: Uint32Array): Bool {
		return speed > 0 ?
			((frameIndex + 1) < frameValues.length && time > frameValues[frameIndex + 1] * frameTime) :
			((frameIndex - 1) > -1 && time < frameValues[frameIndex - 1] * frameTime);
	}

	function rewind(track: TTrack) {
		frameIndex = speed > 0 ? 0 : track.frames.length - 1;
		time = track.frames[frameIndex] * frameTime;
	}

	function updateTrack(anim: TAnimation) {
		if (anim == null) return;

		var track = anim.tracks[0];

		if (frameIndex == -1) rewind(track);

		// Move keyframe
		var sign = speed > 0 ? 1 : -1;
		while (checkFrameIndex(track.frames)) frameIndex += sign;

		// Marker events
		if (markerEvents != null && anim.marker_names != null && frameIndex != lastFrameIndex) {
			for (i in 0...anim.marker_frames.length) {
				if (frameIndex == anim.marker_frames[i]) {
					var ar = markerEvents.get(anim.marker_names[i]);
					if (ar != null) for (f in ar) f();
				} else {
					for (j in 0...(frameIndex - lastFrameIndex)) {
						if (lastFrameIndex + j + 1 == anim.marker_frames[i]) {
							var ar = markerEvents.get(anim.marker_names[i]);
							if (ar != null) for (f in ar) f();
						}
					}
				}
			}
			lastFrameIndex = frameIndex;
		}

		// End of track
		if (isTrackEnd(track)) {
			if (loop || blendTime > 0) {
				rewind(track);
			}
			else {
				frameIndex -= sign;
				paused = true;
			}
			if (onComplete != null && blendTime == 0) onComplete();
		}
	}

	function updateAnimSampled(anim: TAnimation, m: Mat4) {
		if (anim == null) return;
		var track = anim.tracks[0];
		var sign = speed > 0 ? 1 : -1;

		var t = time;
		var ti = frameIndex;
		var t1 = track.frames[ti] * frameTime;
		var t2 = track.frames[ti + sign] * frameTime;
		var s: FastFloat = (t - t1) / (t2 - t1); // Linear

		m1.setF32(track.values, ti * 16); // Offset to 4x4 matrix array
		m2.setF32(track.values, (ti + sign) * 16);

		// Decompose
		m1.decompose(vpos, q1, vscl);
		m2.decompose(vpos2, q2, vscl2);

		// Lerp
		vp.lerp(vpos, vpos2, s);
		vs.lerp(vscl, vscl2, s);
		q3.lerp(q1, q2, s);

		// Compose
		m.fromQuat(q3);
		m.scale(vs);
		m._30 = vp.x;
		m._31 = vp.y;
		m._32 = vp.z;
	}

	public function setFrame(frame: Int) {
		time = 0;
		frameIndex = frame;
		update(frame * Scene.active.raw.frame_time);
	}

	public function notifyOnMarker(name: String, onMarker: Void->Void) {
		if (markerEvents == null) markerEvents = new Map();
		var ar = markerEvents.get(name);
		if (ar == null) {
			ar = [];
			markerEvents.set(name, ar);
		}
		ar.push(onMarker);
	}

	public function removeMarker(name: String, onMarker: Void->Void) {
		markerEvents.get(name).remove(onMarker);
	}

	public function currentFrame(): Int {
		return Std.int(time / frameTime);
	}

	public function totalFrames(): Int {
		return 0;
	}

	#if arm_debug
	public static var animationTime = 0.0;
	static var startTime = 0.0;

	static function beginProfile() {
		startTime = kha.Scheduler.realTime();
	}
	static function endProfile() {
		animationTime += kha.Scheduler.realTime() - startTime;
	}
	public static function endFrame() {
		animationTime = 0;
	}
	#end
}
