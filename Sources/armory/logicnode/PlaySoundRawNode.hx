package armory.logicnode;

class PlaySoundRawNode extends LogicNode {

	/** The name of the sound */
	public var property0: String;
	/** Whether to loop the playback */
	public var property1: Bool;
	/** Override sample rate */
	public var property2: Bool;
	/** Playback sample rate */
	public var property3: Int;

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		iron.data.Data.getSound(property0, function(sound: kha.Sound) {
			if (property2) sound.sampleRate = property3;
			iron.system.Audio.play(sound, property1);
		});
		runOutput(0);
	}
}
