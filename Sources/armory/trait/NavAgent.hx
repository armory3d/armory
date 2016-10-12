package armory.trait;

import iron.Trait;

@:keep
class NavAgent extends Trait {

    // nav mesh
    // target object
    // behaviour

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
