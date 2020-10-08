package armory.logicnode;

import iron.object.SpeakerObject;

class SetSpeakerEnabledNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		var speaker: SpeakerObject = cast(inputs[1].get(), SpeakerObject);
		var enabled: Bool = inputs[2].get();

		if (object == null) return;

		enabled ? speaker.play() : speaker.pause();

		runOutput(0);
	}
}
