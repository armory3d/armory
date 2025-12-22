package iron.object;

import iron.Scene;
import iron.data.Data;
import iron.data.SceneFormat;
import iron.system.Time;

@:allow(iron.Scene)
class Tilesheet {

	public var tileX = 0.0; // Tile offset on tilesheet texture 0-1
	public var tileY = 0.0;

	public var tilesx: Int;
	public var tilesy: Int;
	public var framerate: Int;
	public var actions: Array<TTilesheetAction>;
	public var action: TTilesheetAction = null;
	public var materialName: String;
	var ready: Bool;

	public var paused = false;
	public var frame = 0;
	var time = 0.0;
	var onActionComplete: Void->Void = null;

	/**
	 * Create a tilesheet from material data.
	 * @param sceneName The scene containing the material
	 * @param materialRef The material name with tilesheet data
	 * @param actionRef The initial action to play (optional)
	 */
	public function new(sceneName: String, materialRef: String, actionRef: String) {
		ready = false;
		materialName = materialRef;
		Data.getSceneRaw(sceneName, function(format: TSceneFormat) {
			// Find material with tilesheet data
			for (mat in format.material_datas) {
				if (mat.name == materialRef && mat.tilesheet != null) {
					var ts = mat.tilesheet;
					tilesx = ts.tilesx;
					tilesy = ts.tilesy;
					framerate = Std.int(ts.framerate);
					actions = ts.actions;
					Scene.active.tilesheets.push(this);
					if (actionRef != null && actionRef != "") {
						play(actionRef);
					} else if (actions.length > 0) {
						play(actions[0].name);
					}
					ready = true;
					break;
				}
			}
		});
	}

	public function play(action_ref: String, onActionComplete: Void->Void = null) {
		this.onActionComplete = onActionComplete;
		for (a in actions) {
			if (a.name == action_ref) {
				action = a;
				break;
			}
		}
		if (action != null) {
			setFrame(action.start);
			paused = false;
			time = 0.0;
		}
	}

	public function pause() {
		paused = true;
	}

	public function resume() {
		paused = false;
	}

	public function remove() {
		Scene.active.tilesheets.remove(this);
	}

	/**
	 * Set the frame of the current active tilesheet action. Automatically un-pauses action.
	 * @param frame Frame offset with 0 as the first frame of the active action.
	 **/
	public function setFrameOffset(frame: Int) {
		setFrame(action.start + frame);
		paused = false;
	}

	/**
	 * Returns the current frame.
	 * @return Frame offset with 0 as the first frame of the active action.
	 */
	public function getFrameOffset(): Int {
		return frame - action.start;
	}

	function update() {
		if (!ready || paused || action == null || action.start >= action.end) return;

		time += Time.renderDelta;

		var frameTime = 1 / framerate;
		var framesToAdvance = 0;

		// Check how many animation frames passed during the last render frame
		// and catch up if required. The remaining `time` that couldn't fit in
		// another animation frame will be used in the next `update()`.
		while (time >= frameTime) {
			time -= frameTime;
			framesToAdvance++;
		}

		if (framesToAdvance != 0) {
			setFrame(frame + framesToAdvance);
		}
	}

	function setFrame(f: Int) {
		frame = f;

		// Action end
		if (frame > action.end && action.start < action.end) {
			if (onActionComplete != null) onActionComplete();
			if (action.loop) setFrame(action.start);
			else paused = true;
			return;
		}

		var tx = frame % tilesx;
		var ty = Std.int(frame / tilesx);
		tileX = tx * (1 / tilesx);
		tileY = ty * (1 / tilesy);
	}
}
