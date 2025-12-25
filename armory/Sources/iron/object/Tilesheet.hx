package iron.object;

import iron.data.Data;
import iron.data.SceneFormat;
import iron.system.Time;
import iron.Scene;

class Tilesheet {

	public var tileX = 0.0; // Tile offset on tilesheet texture 0-1
	public var tileY = 0.0;
	public var flipX = false;
	public var flipY = false;

	public var actions: Array<TTilesheetAction>;
	public var action: TTilesheetAction = null;
	var ready: Bool;

	public var paused = false;
	public var frame = 0;
	var time = 0.0;
	var onActionComplete: Void->Void = null;
	var owner: MeshObject = null;
	var currentMesh: String = null; // Track current mesh name to avoid redundant swaps

	/**
	 * Create a tilesheet from embedded object tilesheet data.
	 * @param tilesheetData The tilesheet data embedded in the object
	 * @param ownerObject The MeshObject that owns this tilesheet
	 */
	public function new(tilesheetData: TTilesheetData, ownerObject: MeshObject = null) {
		owner = ownerObject;
		actions = tilesheetData.actions;

		// Play the start action or default to first action
		var startAction = tilesheetData.start_action;
		if (startAction != null && startAction != "") {
			play(startAction);
		} else if (actions.length > 0) {
			play(actions[0].name);
		}
		ready = true;
	}

	public function play(action_ref: String, onActionComplete: Void->Void = null) {
		if (action != null && action.name == action_ref) {
			paused = false;
			return;
		}

		this.onActionComplete = onActionComplete;
		for (a in actions) {
			if (a.name == action_ref) {
				action = a;
				break;
			}
		}
		if (action != null) {
			// Handle optional mesh swap
			if (action.mesh != null && action.mesh != "" && owner != null && action.mesh != currentMesh) {
				swapMesh(action.mesh);
			}
			setFrame(action.start);
			paused = false;
			time = 0.0;
		}
	}

	function swapMesh(meshName: String) {
		currentMesh = meshName;
		// Mesh files are exported as "mesh_[meshname].arm" with the mesh data named "[meshname]" inside
		var meshFile = "mesh_" + meshName;
		Data.getMesh(meshFile, meshName, function(meshData) {
			if (owner != null && meshData != null) {
				owner.setData(meshData);
			}
		});
	}

	public function pause() {
		paused = true;
	}

	public function resume() {
		paused = false;
	}

	public function remove() {
		ready = false;
		action = null;
		actions = null;
		owner = null;
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

	public function update() {
		if (!ready || paused || action == null || action.start >= action.end) return;

		time += Time.renderDelta;

		var frameTime = 1 / action.framerate;
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

		var tx = frame % action.tilesx;
		var ty = Std.int(frame / action.tilesx);
		tileX = tx * (1 / action.tilesx);
		tileY = ty * (1 / action.tilesy);
	}

	// Getters for current action's tile dimensions (for uniforms)
	public function getTilesx(): Int {
		return action != null ? action.tilesx : 1;
	}

	public function getTilesy(): Int {
		return action != null ? action.tilesy : 1;
	}
}
