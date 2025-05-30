package iron.object;

import iron.Scene;
import iron.data.Data;
import iron.data.SceneFormat;
import iron.system.Time;

@:allow(iron.Scene)
class Tilesheet {

	public var tileX = 0.0; // Tile offset on tilesheet texture 0-1
	public var tileY = 0.0;

	public var raw: TTilesheetData;
	public var action: TTilesheetAction = null;
	var ready: Bool;

	public var paused = false;
	public var frame = 0;
	var time = 0.0;
	var onActionComplete: Void->Void = null;

	public function new(sceneName: String, tilesheet_ref: String, tilesheet_action_ref: String) {
		ready = false;
		Data.getSceneRaw(sceneName, function(format: TSceneFormat) {
			for (ts in format.tilesheet_datas) {
				if (ts.name == tilesheet_ref) {
					raw = ts;
					Scene.active.tilesheets.push(this);
					play(tilesheet_action_ref);
					ready = true;
					break;
				}
			}
		});
	}

	public function play(action_ref: String, onActionComplete: Void->Void = null) {
		this.onActionComplete = onActionComplete;
		for (a in raw.actions) {
			if (a.name == action_ref) {
				action = a;
				break;
			}
		}
		setFrame(action.start);
		paused = false;
		time = 0.0;
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
		if (!ready || paused || action.start >= action.end) return;

		time += Time.delta;

		var frameTime = 1 / raw.framerate;
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

		var tx = frame % raw.tilesx;
		var ty = Std.int(frame / raw.tilesx);
		tileX = tx * (1 / raw.tilesx);
		tileY = ty * (1 / raw.tilesy);
	}
}
