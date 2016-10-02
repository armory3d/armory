package armory.trait;

import iron.Trait;

class SceneInstance extends Trait {

	function safeFilename(s:String) {
		s = StringTools.replace(s, '.', '_');
		s = StringTools.replace(s, '-', '_');
		s = StringTools.replace(s, ' ', '_');
		if (Std.parseInt(s.charAt(0)) != null) s = '_' + s; // Prefix _ if first char is digit
		return s;
	}

	public function new(sceneName:String) {
		super();

		notifyOnInit(function() {
			iron.Scene.active.addScene(safeFilename(sceneName), object, function(o:iron.object.Object) {});
		});
	}
}
