package armory.trait;

import iron.Trait;

class SceneInstance extends Trait {

    public function new(sceneName:String) {
        super();

        notifyOnInit(function() {
			iron.Scene.active.addScene(sceneName, object);
		});
    }
}
