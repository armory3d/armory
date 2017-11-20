package armory.logicnode;

import iron.object.SpeakerObject;

class PlaySoundNode extends LogicNode {

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run() {
		var object:SpeakerObject = cast(inputs[1].get(), SpeakerObject);
		object.play();
		super.run();
	}
}
