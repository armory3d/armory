package armory.logicnode;

class PlaySoundRawNode extends LogicNode {

	/** The name of the sound */
	public var property0: String;
	/** Whether to loop the playback */
	public var property1: Bool;
	/** Retrigger */
	public var property2: Bool;
	/** Override sample rate */
	public var property3: Bool;
	/** Playback sample rate */
	public var property4: Int;
	/** Whether to stream the sound from disk **/
	public var property5: Bool;

	var sound: kha.Sound = null;
	var channel: kha.audio1.AudioChannel = null;

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		switch (from) {
			case Play:
				if (sound == null) {
					iron.data.Data.getSound(property0, function(s: kha.Sound) {
						this.sound = s;
					});
				}

				// Resume
				if (channel != null) {
					if (property2) channel.stop();
					channel.play();
					channel.volume = inputs[4].get();
				}
				// Start
				else if (sound != null) {
					if (property3) sound.sampleRate = property4;
					channel = iron.system.Audio.play(sound, property1, property5);
					channel.volume = inputs[4].get();
				}

				tree.notifyOnUpdate(this.onUpdate);
				runOutput(0);

			case Pause:
				if (channel != null) channel.pause();
				tree.removeUpdate(this.onUpdate);

			case Stop:
				if (channel != null) channel.stop();
				tree.removeUpdate(this.onUpdate);
				runOutput(2);
			
			case UpdateVolume:
				if (channel != null) channel.volume = inputs[4].get();
		}
	}

	function onUpdate() {
		if (channel != null) {
			// Done
			if (channel.finished) {
				channel = null;
				runOutput(2);
			}
			// Running
			else runOutput(1);
		}
	}
}

private enum abstract PlayState(Int) from Int to Int {
	var Play = 0;
	var Pause = 1;
	var Stop = 2;
	var UpdateVolume = 3;
}
