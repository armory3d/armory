package iron;

import iron.object.Object;

#if arm_target_n64
@:autoBuild(armory.n64.N64TraitMacro.build())
#end
class Trait {

	public var name: String = "";

    /**
      Object this trait belongs to.
    **/
	public var object: Object;

	var _add: Array<Void->Void> = null;
	var _init: Array<Void->Void> = null;
	var _remove: Array<Void->Void> = null;
	var _update: Array<Void->Void> = null;
	var _lateUpdate: Array<Void->Void> = null;
	var _fixedUpdate: Array<Void->Void> = null;
	var _render: Array<kha.graphics4.Graphics->Void> = null;
	var _render2D: Array<kha.graphics2.Graphics->Void> = null;

	public function new() {}

    /**
      Remove the trait from the object.
    **/
	public function remove() {
		object.removeTrait(this);
	}

    /**
      Trait is added to an object.
    **/
	public function notifyOnAdd(f: Void->Void) {
		if (_add == null) _add = [];
		_add.push(f);
	}

    /**
      Object which this trait belongs to is added to scene.
    **/
	public function notifyOnInit(f: Void->Void) {
		if (_init == null) _init = [];
		_init.push(f);
		App.notifyOnInit(f);
	}

    /**
      Object which this trait belongs to is removed from scene.
    **/
	public function notifyOnRemove(f: Void->Void) {
		if (_remove == null) _remove = [];
		_remove.push(f);
	}

    /**
      Add game logic handler.
    **/
	public function notifyOnUpdate(f: Void->Void) {
		if (_update == null) _update = [];
		_update.push(f);
		App.notifyOnUpdate(f);
	}

    /**
      Remove game logic handler.
    **/
	public function removeUpdate(f: Void->Void) {
		_update.remove(f);
		App.removeUpdate(f);
	}

    /**
      Add late game logic handler.
    **/
	public function notifyOnLateUpdate(f: Void->Void) {
		if (_lateUpdate == null) _lateUpdate = [];
		_lateUpdate.push(f);
		App.notifyOnLateUpdate(f);
	}

    /**
      Remove late game logic handler.
    **/
	public function removeLateUpdate(f: Void->Void) {
		_lateUpdate.remove(f);
		App.removeLateUpdate(f);
	}

    /**
      Add fixed game logic handler.
    **/
	public function notifyOnFixedUpdate(f: Void->Void) {
		if (_fixedUpdate == null) _fixedUpdate = [];
		_fixedUpdate.push(f);
		App.notifyOnFixedUpdate(f);
	}

    /**
      Remove fixed game logic handler.
    **/
	public function removeFixedUpdate(f: Void->Void) {
		_fixedUpdate.remove(f);
		App.removeFixedUpdate(f);
	}

    /**
      Add render handler.
    **/
	public function notifyOnRender(f: kha.graphics4.Graphics->Void) {
		if (_render == null) _render = [];
		_render.push(f);
		App.notifyOnRender(f);
	}

    /**
      Remove render handler.
    **/
	public function removeRender(f: kha.graphics4.Graphics->Void) {
		_render.remove(f);
		App.removeRender(f);
	}

    /**
      Add 2D render handler.
    **/
	public function notifyOnRender2D(f: kha.graphics2.Graphics->Void) {
		if (_render2D == null) _render2D = [];
		_render2D.push(f);
		App.notifyOnRender2D(f);
	}

    /**
      Remove 2D render handler.
    **/
	public function removeRender2D(f: kha.graphics2.Graphics->Void) {
		_render2D.remove(f);
		App.removeRender2D(f);
	}
}
