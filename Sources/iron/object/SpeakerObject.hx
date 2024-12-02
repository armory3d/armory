package iron.object;

import kha.FastFloat;
import kha.audio1.AudioChannel;
import iron.data.Data;
import iron.data.SceneFormat;
import iron.math.Vec4;
import iron.system.Audio;

class SpeakerObject extends Object {

#if arm_audio

	public var data: TSpeakerData;
	public var paused(default, null) = false;
	public var sound(default, null): kha.Sound = null;
	public var channels(default, null): Array<AudioChannel> = [];
	public var volume(default, null) : FastFloat;

	public function new(data: TSpeakerData) {
		super();

		this.data = data;

		Scene.active.speakers.push(this);

		if (data.sound == "") return;

		Data.getSound(data.sound, function(sound: kha.Sound) {
			this.sound = sound;
			App.notifyOnInit(init);
		});
	}

	function init() {
		if (visible && data.play_on_start) play();
	}

	public function play() {
		if (sound == null || data.muted) return;
		if (paused) {
			for (c in channels) c.play();
			paused = false;
			return;
		}
		var channel = Audio.play(sound, data.loop, data.stream);
		if (channel != null) {
			channels.push(channel);
			if (data.attenuation > 0 && channels.length == 1) App.notifyOnUpdate(update);
		}
	}

	public function pause() {
		for (c in channels) c.pause();
		paused = true;
	}

	public function stop() {
		for (c in channels) c.stop();
		channels.splice(0, channels.length);
	}

	function update() {
		if (paused) return;
		for (c in channels) if (c.finished) channels.remove(c);
		if (channels.length == 0) {
			App.removeUpdate(update);
			return;
		}

		if (data.attenuation > 0) {
			var distance = Vec4.distance(Scene.active.camera.transform.world.getLoc(), transform.world.getLoc());
			distance = Math.max(Math.min(data.distance_max, distance), data.distance_reference);
			volume = data.distance_reference / (data.distance_reference + data.attenuation * (distance - data.distance_reference));
			volume *= data.volume;
		}
		else {
			volume = data.volume;
		}

		if (volume > data.volume_max) volume = data.volume_max;
		else if (volume < data.volume_min) volume = data.volume_min;

		for (c in channels) c.volume = volume;
	}

	public override function remove() {
		stop();
		if (Scene.active != null) Scene.active.speakers.remove(this);
		super.remove();
	}

#end

}
