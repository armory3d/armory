package armory.logicnode;

import iron.object.SpeakerObject;

class PauseSoundNode extends LogicNode {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run() {
		var object:SpeakerObject = cast(inputs[1].get(), SpeakerObject);
		if (object == null) return;
		object.pause();
		super.run();
	}
}
