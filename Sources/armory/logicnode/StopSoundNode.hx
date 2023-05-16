package armory.logicnode;

import iron.object.SpeakerObject;

class StopSoundNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		var object: SpeakerObject = cast(inputs[1].get(), SpeakerObject);
		if (object == null) return;
		object.stop();
		runOutput(0);
	}
}
