package arm2d;

// Zui
import zui.Zui;
import zui.Themes;
import zui.Id;
using zui.Ext;
import armory.ui.Popup;
import armory.ui.Canvas;

// Editor
import arm2d.Path;
import arm2d.Assets;
import arm2d.tools.Math;
import arm2d.ui.UIToolBar;
import arm2d.ui.UIProperties;
import arm2d.tools.CanvasTools;

@:access(zui.Zui)
class Editor {
	var ui:Zui;
	public var cui:Zui;
	public var canvas:TCanvas;

	public static var defaultWindowW = 240;
	public static var windowW = defaultWindowW;
	static var uiw(get, null):Int;
	static function get_uiw():Int {
		return Std.int(windowW * Main.prefs.scaleFactor);
	}
	var toolbarw(get, null):Int;
	function get_toolbarw():Int {
		return Std.int(140 * ui.SCALE());
	}

	// Canvas offset from the editor window
	// Should be a multiple of gridSize to ensure visual grid alignment
	public static var coffX = 160.0;
	public static var coffY = 40.0;

	var dropPath = "";
	public static var currentOperation = "";
	public static var assetNames:Array<String> = [""];
	public static var dragAsset:TAsset = null;
	var resizeCanvas = false;
	var zoom = 1.0;

	public static var showFiles = false;
	public static var foldersOnly = false;
	public static var filesDone:String->Void = null;
	var uimodal:Zui;

	public static var gridSnapBounds:Bool = false;
	public static var gridSnapPos:Bool = true;
	public static var gridUseRelative:Bool = true;
	public static var useRotationSteps:Bool = false;
	public static var rotationSteps:Float = Math.toRadians(15);
	public static var gridSize:Int = 20;
	public static var redrawGrid = false;
	static var grid:kha.Image = null;
	static var timeline:kha.Image = null;

	var selectedFrame = 0;
	public static var selectedTheme:zui.Themes.TTheme = null;
	public static var selectedElem:TElement = null;
	var lastW = 0;
	var lastH = 0;
	var lastCanvasW = 0;
	var lastCanvasH = 0;

	public function new(canvas:TCanvas) {
		this.canvas = canvas;

		// Reimport assets
		if (canvas.assets.length > 0) {
			var assets = canvas.assets;
			canvas.assets = [];
			for (a in assets) Assets.importAsset(canvas, a.file);
		}

		Assets.importThemes();

		kha.Assets.loadEverything(loaded);
	}

	function loaded() {
		var t = Reflect.copy(Themes.dark);
		t.FILL_WINDOW_BG = true;
		ui = new Zui({scaleFactor: Main.prefs.scaleFactor, font: kha.Assets.fonts.font_default, theme: t, color_wheel: kha.Assets.images.color_wheel, black_white_gradient: kha.Assets.images.black_white_gradient});
		cui = new Zui({scaleFactor: 1.0, font: kha.Assets.fonts.font_default, autoNotifyInput: true, theme: Reflect.copy(Canvas.getTheme(canvas.theme))});
		uimodal = new Zui( { font: kha.Assets.fonts.font_default, scaleFactor: Main.prefs.scaleFactor } );
		ElementController.initialize(ui, cui);

		if (Canvas.getTheme(canvas.theme) == null) {
			Popup.showMessage(new Zui(ui.ops), "Warning!",
				'Theme "${canvas.theme}" was not found!'
				+ '\nUsing first theme in list instead: "${Canvas.themes[0].NAME}"');
			canvas.theme = Canvas.themes[0].NAME;
		}

		kha.System.notifyOnDropFiles(function(path:String) {
			dropPath = StringTools.rtrim(path);
			dropPath = Path.toRelative(dropPath, Main.cwd);
		});

		kha.System.notifyOnFrames(onFrames);
		kha.Scheduler.addTimeTask(update, 0, 1 / 60);
	}

	function resize() {
		if (grid != null) {
			grid.unload();
			grid = null;
		}
		if (timeline != null) {
			timeline.unload();
			timeline = null;
		}
	}

	function drawGrid() {
		redrawGrid = false;

		var scaledGridSize = scaled(gridSize);
		var doubleGridSize = scaled(gridSize * 2);

		var ww = kha.System.windowWidth();
		var wh = kha.System.windowHeight();
		var w = ww + doubleGridSize * 2;
		var h = wh + doubleGridSize * 2;

		if (grid == null) {
			grid = kha.Image.createRenderTarget(w, h);
		}
		grid.g2.begin(true, 0xff242424);

		for (i in 0...Std.int(h / doubleGridSize) + 1) {
			grid.g2.color = 0xff282828;
			grid.g2.drawLine(0, i * doubleGridSize + scaledGridSize, w, i * doubleGridSize + scaledGridSize);
			grid.g2.color = 0xff323232;
			grid.g2.drawLine(0, i * doubleGridSize, w, i * doubleGridSize);
		}
		for (i in 0...Std.int(w / doubleGridSize) + 1) {
			grid.g2.color = 0xff282828;
			grid.g2.drawLine(i * doubleGridSize + scaledGridSize, 0, i * doubleGridSize + scaledGridSize, h);
			grid.g2.color = 0xff323232;
			grid.g2.drawLine(i * doubleGridSize, 0, i * doubleGridSize, h);
		}

		grid.g2.end();
	}

	function drawTimeline(timelineLabelsHeight:Int, timelineFramesHeight:Int) {
		var sc = ui.SCALE();

		var timelineHeight = timelineLabelsHeight + timelineFramesHeight;

		timeline = kha.Image.createRenderTarget(kha.System.windowWidth() - uiw - toolbarw, timelineHeight);

		var g = timeline.g2;
		g.begin(true, 0xff222222);
		g.font = kha.Assets.fonts.font_default;
		g.fontSize = Std.int(16 * sc);

		// Labels
		var frames = Std.int(timeline.width / (11 * sc));
		for (i in 0...Std.int(frames / 5) + 1) {
			var frame = i * 5;

			var frameTextWidth = kha.Assets.fonts.font_default.width(g.fontSize, frame + "");
			g.drawString(frame + "", i * 55 * sc + 5 * sc - frameTextWidth / 2, timelineLabelsHeight / 2 - g.fontSize / 2);
		}

		// Frames
		for (i in 0...frames) {
			g.color = i % 5 == 0 ? 0xff444444 : 0xff333333;
			g.fillRect(i * 11 * sc, timelineHeight - timelineFramesHeight, 10 * sc, timelineFramesHeight);
		}

		g.end();
	}

	public function onFrames(framebuffers: Array<kha.Framebuffer>): Void {
		// Prevent crash when minimizing window
		if (kha.System.windowWidth() == 0 || kha.System.windowHeight() == 0) return;

		var framebuffer = framebuffers[0];

		// Disable UI if a popup is displayed
		if (Popup.show && ui.inputRegistered) {
			ui.unregisterInput();
			cui.unregisterInput();
		} else if (!Popup.show && !ui.inputRegistered) {
			ui.registerInput();
			cui.registerInput();
		}

		// Update preview when choosing a color
		if (Popup.show) UIProperties.hwin.redraws = 1;

		if (dropPath != "") {
			Assets.importAsset(canvas, dropPath);
			dropPath = "";
		}

		var sc = ui.SCALE();
		var timelineLabelsHeight = Std.int(30 * sc);
		var timelineFramesHeight = Std.int(40 * sc);

		// Bake and redraw if the UI scale has changed
		if (grid == null || redrawGrid) drawGrid();
		if (timeline == null || timeline.height != timelineLabelsHeight + timelineFramesHeight) drawTimeline(timelineLabelsHeight, timelineFramesHeight);

		var g = framebuffer.g2;
		g.begin();

		g.color = 0xffffffff;
		var doubleGridSize = scaled(gridSize * 2);
		g.drawImage(grid, coffX % doubleGridSize - doubleGridSize, coffY % doubleGridSize - doubleGridSize);

		// Canvas outline
		canvas.x = coffX;
		canvas.y = coffY;
		g.drawRect(canvas.x, canvas.y, scaled(canvas.width), scaled(canvas.height), 1.0);

		// Canvas resize
		var handleSize = ElementController.handleSize;
		if (Math.hitbox(cui, canvas.x + scaled(canvas.width) - handleSize / 2, canvas.y + scaled(canvas.height) - handleSize / 2, handleSize, handleSize)) {
			g.color = 0xff205d9c;
			g.fillRect(canvas.x + scaled(canvas.width) - handleSize / 2, canvas.y + scaled(canvas.height) - handleSize / 2, handleSize, handleSize);
			g.color = 0xffffffff;
		}
		g.drawRect(canvas.x + scaled(canvas.width) - handleSize / 2, canvas.y + scaled(canvas.height) - handleSize / 2, handleSize, handleSize, 1);

		Canvas.screenW = canvas.width;
		Canvas.screenH = canvas.height;
		Canvas.draw(cui, canvas, g);

		ElementController.render(g, canvas);

		if (currentOperation != "") {
			g.fontSize = Std.int(14 * ui.SCALE());
			g.color = 0xffaaaaaa;
			g.drawString(currentOperation, toolbarw, kha.System.windowHeight() - timeline.height - g.fontSize);
		}

		// Timeline
		var showTimeline = true;
		if (showTimeline) {
			g.color = 0xffffffff;
			var ty = kha.System.windowHeight() - timeline.height;
			g.drawImage(timeline, toolbarw, ty);

			g.color = 0xff205d9c;
			g.fillRect(toolbarw + selectedFrame * 11 * sc, ty + timelineLabelsHeight, 10 * sc, timelineFramesHeight);

			// Show selected frame number
			g.font = kha.Assets.fonts.font_default;
			g.fontSize = Std.int(16 * sc);

			var frameIndicatorMargin = 4 * sc;
			var frameIndicatorPadding = 4 * sc;
			var frameIndicatorWidth = 30 * sc;
			var frameIndicatorHeight = timelineLabelsHeight - frameIndicatorMargin * 2;
			var frameTextWidth = kha.Assets.fonts.font_default.width(g.fontSize, "" + selectedFrame);

			// Scale the indicator if the contained text is too long
			if (frameTextWidth > frameIndicatorWidth + frameIndicatorPadding) {
				frameIndicatorWidth = frameTextWidth + frameIndicatorPadding;
			}

			g.fillRect(toolbarw + selectedFrame * 11 * sc + 5 * sc - frameIndicatorWidth / 2, ty + frameIndicatorMargin, frameIndicatorWidth, frameIndicatorHeight);
			g.color = 0xffffffff;
			g.drawString("" + selectedFrame, toolbarw + selectedFrame * 11 * sc + 5 * sc - frameTextWidth / 2, ty + timelineLabelsHeight / 2 - g.fontSize / 2);
		}

		g.end();

		ui.begin(g);

		UIToolBar.renderToolbar(ui, cui, canvas, toolbarw);

		if (ui.window(Id.handle(), toolbarw, 0, kha.System.windowWidth() - uiw - toolbarw, Std.int((ui.t.ELEMENT_H + 2) * ui.SCALE()))) {
			ui.tab(Id.handle(), canvas.name);
		}

		UIProperties.renderProperties(ui, uiw, canvas);

		ui.end();

		if (ui.changed && !ui.inputDown) drawGrid();

		g.begin(false);

		if (dragAsset != null) {
			var w = std.Math.min(128, Assets.getImage(dragAsset).width);
			var ratio = w / Assets.getImage(dragAsset).width;
			var h = Assets.getImage(dragAsset).height * ratio;
			g.drawScaledImage(Assets.getImage(dragAsset), ui.inputX, ui.inputY, w, h);
		}

		g.end();

		if (lastW > 0 && (lastW != kha.System.windowWidth() || lastH != kha.System.windowHeight())) {
			resize();
		}
		else if (lastCanvasW > 0 && (lastCanvasW != canvas.width || lastCanvasH != canvas.height)) {
			resize();
		}
		lastW = kha.System.windowWidth();
		lastH = kha.System.windowHeight();
		lastCanvasW = canvas.width;
		lastCanvasH = canvas.height;

		if (showFiles) renderFiles(g);
		if (Popup.show) Popup.render(g);
	}

	function acceptDrag(index:Int) {
		var elem = CanvasTools.makeElem(cui, canvas, ElementType.Image);
		elem.asset = assetNames[index + 1]; // assetNames[0] == ""
		elem.x = ui.inputX - canvas.x;
		elem.y = ui.inputY - canvas.y;
		elem.width = Assets.getImage(canvas.assets[index]).width;
		elem.height = Assets.getImage(canvas.assets[index]).height;
		selectedElem = elem;
	}

	public function update() {

		// Drag from assets panel
		if (ui.inputReleased && dragAsset != null) {
			if (ui.inputX < kha.System.windowWidth() - uiw) {
				var index = 0;
				for (i in 0...canvas.assets.length) if (canvas.assets[i] == dragAsset) { index = i; break; }
				acceptDrag(index);
			}
			dragAsset = null;
		}
		if (dragAsset != null) return;

		updateCanvas();

		// Select frame
		if (timeline != null) {
			var ty = kha.System.windowHeight() - timeline.height;
			if (ui.inputDown && ui.inputY > ty && ui.inputX < kha.System.windowWidth() - uiw && ui.inputX > toolbarw) {
				selectedFrame = Std.int((ui.inputX - toolbarw) / 11 / ui.SCALE());
			}
		}

		ElementController.update(ui, cui, canvas);

		if (Popup.show) Popup.update();

		updateFiles();
	}

	function updateCanvas() {
		if (showFiles || ui.inputX > kha.System.windowWidth() - uiw) return;

		ElementController.selectElement(canvas);

		if (!ElementController.isManipulating) {
			// Pan canvas
			if (ui.inputDownR) {
				coffX += Std.int(ui.inputDX);
				coffY += Std.int(ui.inputDY);
			}

			// Zoom canvas
			if (ui.inputWheelDelta != 0) {
				var prevZoom = zoom;
				zoom += -ui.inputWheelDelta / 10;
				if (zoom < 0.4) zoom = 0.4;
				else if (zoom > 1.0) zoom = 1.0;
				zoom = std.Math.round(zoom * 10) / 10;
				cui.setScale(zoom);

				// Update the grid only when necessary, this prevents lag from scrolling too fast
				if (prevZoom != zoom) {
					drawGrid();
				}
			}
		}

		// Canvas resize
		var handleSize = ElementController.handleSize;
		if (ui.inputStarted && Math.hitbox(cui, canvas.x + scaled(canvas.width) - handleSize / 2, canvas.y + scaled(canvas.height) - handleSize / 2, handleSize, handleSize)) {
			resizeCanvas = true;
		}
		if (ui.inputReleased && resizeCanvas) {
			resizeCanvas = false;
		}
		if (resizeCanvas) {
			canvas.width += Std.int(ui.inputDX);
			canvas.height += Std.int(ui.inputDY);
			if (canvas.width < 1) canvas.width = 1;
			if (canvas.height < 1) canvas.height = 1;
		}
	}

	function updateFiles() {
		if (!showFiles) return;

		if (ui.inputReleased) {
			var appw = kha.System.windowWidth();
			var apph = kha.System.windowHeight();
			var left = appw / 2 - modalRectW / 2;
			var right = appw / 2 + modalRectW / 2;
			var top = apph / 2 - modalRectH / 2;
			var bottom = apph / 2 + modalRectH / 2;
			if (ui.inputX < left || ui.inputX > right || ui.inputY < top + modalHeaderH || ui.inputY > bottom) {
				showFiles = false;
			}
		}
	}

	static var modalW = 625;
	static var modalH = 545;
	static var modalHeaderH = 66;
	static var modalRectW = 625; // No shadow
	static var modalRectH = 545;

	static var path = '/';
	function renderFiles(g:kha.graphics2.Graphics) {
		var appw = kha.System.windowWidth();
		var apph = kha.System.windowHeight();
		var left = appw / 2 - modalW / 2;
		var top = apph / 2 - modalH / 2;

		g.begin(false);
		g.color = 0xff202020;
		g.fillRect(left, top, modalW, modalH);
		g.end();

		var leftRect = Std.int(appw / 2 - modalRectW / 2);
		var rightRect = Std.int(appw / 2 + modalRectW / 2);
		var topRect = Std.int(apph / 2 - modalRectH / 2);
		var bottomRect = Std.int(apph / 2 + modalRectH / 2);
		topRect += modalHeaderH;

		uimodal.begin(g);
		if (uimodal.window(Id.handle(), leftRect, topRect, modalRectW, modalRectH - 100)) {
			var pathHandle = Id.handle();
			pathHandle.text = uimodal.textInput(pathHandle);
			path = uimodal.fileBrowser(pathHandle, foldersOnly);
		}
		uimodal.end(false);

		g.begin(false);

		uimodal.beginRegion(g, rightRect - 100, bottomRect - 30, 100);
		if (uimodal.button("OK")) {
			showFiles = false;
			filesDone(path);
		}
		uimodal.endRegion(false);

		uimodal.beginRegion(g, rightRect - 200, bottomRect - 30, 100);
		if (uimodal.button("Cancel")) {
			showFiles = false;
		}
		uimodal.endRegion();

		g.end();
	}

	inline function scaled(f: Float): Int { return Std.int(f * cui.SCALE()); }
}
