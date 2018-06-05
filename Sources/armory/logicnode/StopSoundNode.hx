package armory.logicnode;

import iron.object.SpeakerObject;

class StopSoundNode extends LogicNode {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run() {
		var object:SpeakerObject = cast(inputs[1].get(), SpeakerObject);
		object.stop();
		super.run();
	}
}
