package armory.logicnode;

class PlaySoundRawNode extends LogicNode {

	public var property0: String;
	/**
	 * Override sample rate
	 */
	public var property1: Bool;
	/**
	 * Playback sample rate
	 */
	public var property2: Int;

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		iron.data.Data.getSound(property0, function(sound: kha.Sound) {
			if (property1) sound.sampleRate = property2;
			iron.system.Audio.play(sound, false);
		});
		runOutput(0);
	}
}
