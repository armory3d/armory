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
	var currentMesh: MeshObject = null; // Currently active mesh (from children)
	var meshCache: Map<String, MeshObject> = new Map(); // Cache of child meshes by name

	/**
	 * Create a tilesheet from embedded object tilesheet data.
	 * @param tilesheetData The tilesheet data embedded in the object
	 * @param ownerObject The MeshObject that owns this tilesheet
	 */
	public function new(tilesheetData: TTilesheetData, ownerObject: MeshObject = null) {
		owner = ownerObject;
		actions = tilesheetData.actions;

		// Cache child mesh objects for quick lookup during mesh swaps
		if (owner != null) {
			cacheChildMeshes();
		}

		// Play the start action or default to first action
		var startAction = tilesheetData.start_action;
		if (startAction != null && startAction != "") {
			play(startAction);
		} else if (actions.length > 0) {
			play(actions[0].name);
		}
		ready = true;
	}

	/**
	 * Cache all MeshObject children for quick lookup by mesh name.
	 * Children used for tilesheet mesh swapping should be hidden (not rendered directly).
	 */
	function cacheChildMeshes() {
		if (owner.children == null) return;

		for (child in owner.children) {
			if (Std.isOfType(child, MeshObject)) {
				var meshChild = cast(child, MeshObject);
				// Cache by the mesh data name (what's referenced in action.mesh)
				if (meshChild.data != null) {
					meshCache.set(meshChild.data.name, meshChild);
					// Hide children - they're just data sources, not rendered directly
					meshChild.visible = false;
				}
			}
		}
	}

	public function play(action_ref: String, onActionComplete: Void->Void = null) {
		if (actions == null) return;

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
			// Lazy cache children - they may not be available at construction time
			var cacheSize = 0;
			for (_ in meshCache) cacheSize++;
			if (cacheSize == 0 && owner != null) {
				cacheChildMeshes();
			}
			// Handle optional mesh swap - find child MeshObject and copy its data/materials
			if (action.mesh != null && action.mesh != "") {
				var targetMesh = meshCache.get(action.mesh);
				if (targetMesh != null && targetMesh != currentMesh) {
					swapMesh(targetMesh);
				}
			}
			setFrame(action.start);
			paused = false;
			time = 0.0;
		}
	}

	/**
	 * Swap to a different mesh by copying its geometry and materials to the owner.
	 * @param meshObj The child MeshObject to swap to
	 */
	function swapMesh(meshObj: MeshObject) {
		if (owner == null || meshObj == null) return;

		currentMesh = meshObj;

		// Copy geometry data
		if (meshObj.data != null) {
			owner.setData(meshObj.data);
		}

		// Copy materials
		if (meshObj.materials != null) {
			owner.materials = meshObj.materials;
		}
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
		currentMesh = null;
		meshCache.clear();
	}

	/**
	 * Set the frame of the current active tilesheet action. Automatically un-pauses action.
	 * @param frame Frame offset with 0 as the first frame of the active action.
	 **/
	public function setFrameOffset(frame: Int) {
		if (action == null) return;
		setFrame(action.start + frame);
		paused = false;
	}

	/**
	 * Returns the current frame.
	 * @return Frame offset with 0 as the first frame of the active action.
	 */
	public function getFrameOffset(): Int {
		if (action == null) return 0;
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
