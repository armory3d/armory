package armory.logicnode;

class PlaySoundRawNode extends LogicNode {

	public var property0:String;

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run(from:Int) {
		iron.data.Data.getSound(property0, function(sound:kha.Sound) {
			iron.system.Audio.play(sound, false);
		});
		runOutput(0);
	}
}
