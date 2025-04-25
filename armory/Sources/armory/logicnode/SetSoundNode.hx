package armory.logicnode;

import iron.object.SpeakerObject;

class SetSoundNode extends LogicNode {

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		var object: SpeakerObject = cast(inputs[1].get(), SpeakerObject);
		var sound: String = inputs[2].get(); 
		if (object == null || sound == null) return;
		object.setSound(sound);
		runOutput(0);
	}
}
