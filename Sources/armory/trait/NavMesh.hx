package armory.trait;

import iron.Trait;

@:keep
class NavMesh extends Trait {

    public function new() {
        super();

        notifyOnInit(init);
        notifyOnUpdate(update);
		notifyOnRemove(removed);
    }
	
	function removed() {

	}

    function init() {

    }

    function update() {
		
    }
}
