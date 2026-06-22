package arm2d.ui;

// Kha
import kha.input.KeyCode;

// Zui
import zui.Id;
import zui.Zui;
import armory.ui.Popup;
import armory.ui.Canvas;
using zui.Ext;
using armory.ui.Ext;

// Editor
import arm2d.tools.Math;
import arm2d.tools.CanvasTools;

@:access(zui.Zui)
class UIProperties {

	public static var hwin = Id.handle();

	public static function renderProperties(ui:Zui, width:Int, canvas:TCanvas) {

		if (ui.window(hwin, kha.System.windowWidth() - width, 0, width, kha.System.windowHeight())) {

			var htab = Id.handle();
			if (ui.tab(htab, "Project")) {

				var hpath = Id.handle({text:""});
				ui.textInput(hpath,"Current file");
				if(hpath.changed){
					Main.prefs.path = hpath.text;
				}

				if (ui.button("Save")) {
					Assets.save(canvas);
				}

				if(ui.button("Load")){
					Assets.load(function(c:TCanvas){
						Main.inst.canvas = c;
						hwin.redraws = 2;
					});
				}

				if (ui.panel(Id.handle({selected: false}), "Canvas")) {
					ui.indent();

					if (ui.button("New")) {
						canvas.elements = [];
						Editor.selectedElem = null;
					}
					if (ui.isHovered) ui.tooltip("Create new canvas");

					var handleName = Id.handle({text: canvas.name});
					handleName.text = canvas.name;
					ui.textInput(handleName, "Name", Right);
					if (handleName.changed) {
						// Themes file is called _themes.json, so canvases should not be named like that
						if (handleName.text == "_themes") {
							Popup.showMessage(new Zui(ui.ops), "Sorry!", "\"_themes\" is not a valid canvas name as it is reserved!");
							handleName.text = canvas.name;
						} else {
							canvas.name = handleName.text;
						}
					}

					ui.row([1/2, 1/2]);
					var handlecw = Id.handle({text: canvas.width + ""});
					var handlech = Id.handle({text: canvas.height + ""});
					handlecw.text = canvas.width + "";
					handlech.text = canvas.height + "";
					var strw = ui.textInput(handlecw, "Width", Right);
					var strh = ui.textInput(handlech, "Height", Right);
					canvas.width = Std.parseInt(strw);
					canvas.height = Std.parseInt(strh);

					ui.unindent();
				}

				if (ui.panel(Id.handle({selected: true}), "Outliner")) {
					ui.indent();

					function drawList(h:zui.Zui.Handle, elem:TElement) {
						var b = false;
						// Highlight
						if (Editor.selectedElem == elem) {
							ui.g.color = 0xff205d9c;
							ui.g.fillRect(ui._x, ui._y, ui._w, ui.t.ELEMENT_H * ui.SCALE());
							ui.g.color = 0xffffffff;
						}
						var started = ui.getStarted();
						// Select
						if (started && !ui.inputDownR) Editor.selectedElem = elem;
						// Parenting
						if (started && ui.inputDownR) {
							if (elem == Editor.selectedElem) CanvasTools.unparent(canvas, elem);
							else CanvasTools.setParent(canvas, Editor.selectedElem, elem);
						}
						// Draw
						if (elem.children != null && elem.children.length > 0) {
							ui.row([1/13, 12/13]);
							b = ui.panel(h.nest(elem.id, {selected: true}), "", true, false, false);
							ui.text(elem.name);
						}
						else {
							ui._x += 18; // Sign offset
							ui.text(elem.name);
							ui._x -= 18;
						}
						// Draw children
						if (b) {
							var i = elem.children.length;
							while(i > 0) {
								i--; //Iterate backwards to avoid reparenting issues.
								var id = elem.children[elem.children.length - 1 - i];
								ui.indent();
								drawList(h, CanvasTools.elemById(canvas, id));
								ui.unindent();
							}
						}
					}

					if (canvas.elements.length > 0) {
						for (i in 0...canvas.elements.length) {
							var elem = canvas.elements[canvas.elements.length - 1 - i];
							if (elem.parent == null) drawList(Id.handle(), elem);
						}

						ui.row([1/4, 1/4, 1/4, 1/4]);
						if (ui.button("Up") && Editor.selectedElem != null) {
							CanvasTools.moveElem(canvas, Editor.selectedElem, 1);
						}
						if (ui.isHovered) ui.tooltip("Move element up");

						if (ui.button("Down") && Editor.selectedElem != null) {
							CanvasTools.moveElem(canvas, Editor.selectedElem,-1);
						}
						if (ui.isHovered) ui.tooltip("Move element down");

						if (ui.button("Remove") && Editor.selectedElem != null) {
							CanvasTools.removeElem(canvas, Editor.selectedElem);
							Editor.selectedElem = null;
						}
						if (ui.isHovered) ui.tooltip("Delete element");

						if (ui.button("Duplicate") && Editor.selectedElem != null) {
							Editor.selectedElem = CanvasTools.duplicateElem(canvas, Editor.selectedElem);
						}
						if (ui.isHovered) ui.tooltip("Create duplicate of element");
					}

					ui.unindent();
				}

				if (Editor.selectedElem != null) {
					var elem = Editor.selectedElem;
					var id = elem.id;

					if (ui.panel(Id.handle({selected: true}), "Properties")) {
						ui.indent();
						elem.visible = ui.check(Id.handle().nest(id, {selected: elem.visible == null ? true : elem.visible}), "Visible");
						elem.name = ui.textInput(Id.handle().nest(id, {text: elem.name}), "Name", Right);
						elem.text = ui.textInput(Id.handle().nest(id, {text: elem.text}), "Text", Right);
						ui.row([1/4, 1/4, 1/4, 1/4]);
						var handlex = Id.handle().nest(id, {text: elem.x + ""});
						var handley = Id.handle().nest(id, {text: elem.y + ""});
						// if (drag) {
							handlex.text = elem.x + "";
							handley.text = elem.y + "";
						// }
						var strx = ui.textInput(handlex, "X", Right);
						var stry = ui.textInput(handley, "Y", Right);
						elem.x = Std.parseFloat(strx);
						elem.y = Std.parseFloat(stry);
						// ui.row([1/2, 1/2]);
						var handlew = Id.handle().nest(id, {text: elem.width + ""});
						var handleh = Id.handle().nest(id, {text: elem.height + ""});
						// if (drag) {
							handlew.text = elem.width + "";
							handleh.text = elem.height + "";
						// }
						var strw = ui.textInput(handlew, "W", Right);
						var strh = ui.textInput(handleh, "H", Right);
						elem.width = Std.int(Std.parseFloat(strw));
						elem.height = Std.int(Std.parseFloat(strh));
						if (elem.type == ElementType.Rectangle || elem.type == ElementType.Circle || elem.type == ElementType.Triangle || elem.type == ElementType.ProgressBar || elem.type == ElementType.CProgressBar){
							var handles = Id.handle().nest(id, {text: elem.strength+""});
							var strs = ui.textInput(handles, "Line Strength", Right);
							elem.strength = Std.int(Std.parseFloat(strs));
						}
						if (elem.type == ElementType.ProgressBar || elem.type == ElementType.CProgressBar){
							var handlep = Id.handle().nest(id, {value: elem.progress_at});
							var slp = ui.slider(handlep, "Progress", 0.0, elem.progress_total, true, 1);
							var handlespt = Id.handle().nest(id, {text: elem.progress_total+""});
							var strpt = ui.textInput(handlespt, "Total Progress", Right);
							elem.progress_total = Std.int(Std.parseFloat(strpt));
							elem.progress_at = Std.int(slp);
						}
						var handlerot = Id.handle().nest(id, {value: Math.roundPrecision(Math.toDegrees(elem.rotation == null ? 0 : elem.rotation), 2)});
						handlerot.value = Math.roundPrecision(Math.toDegrees(elem.rotation), 2);
						// Small fix for radian/degree precision errors
						if (handlerot.value >= 360) handlerot.value = 0;
						elem.rotation = Math.toRadians(ui.slider(handlerot, "Rotation", 0.0, 360.0, true));
						var assetPos = ui.combo(Id.handle().nest(id, {position: Assets.getAssetIndex(canvas, elem.asset)}), Assets.getEnumTexts(), "Asset", true, Right);
						elem.asset = Assets.getEnumTexts()[assetPos];
						ui.unindent();
					}
					if (ui.panel(Id.handle({selected: false}), "Color")){
						ui.indent();

						function drawColorSelection(idMult: Int, color:Null<Int>, defaultColor:Int) {
							ui.row([1/2, 1/2]);

							var handleCol = Id.handle().nest(id).nest(idMult, {color: Canvas.getColor(color, defaultColor)});
							ui.colorField(handleCol, true);

							if (handleCol.changed) {
								color = handleCol.color;
							}

							// Follow theme color
							if (ui.button("Reset") || color == null) {
								color = null;
								handleCol.color = defaultColor;
								handleCol.changed = false;
							}

							return color;
						}

						var canvasTheme = Canvas.getTheme(canvas.theme);

						switch(elem.type) {
							case Text:
								ui.text("Text:");
								elem.color_text = drawColorSelection(1, elem.color_text, canvasTheme.TEXT_COL);

							case Button:
								ui.text("Text:");
								elem.color_text = drawColorSelection(1, elem.color_text, canvasTheme.BUTTON_TEXT_COL);
								ui.text("Background:");
								elem.color = drawColorSelection(2, elem.color, canvasTheme.BUTTON_COL);
								ui.text("On Hover:");
								elem.color_hover = drawColorSelection(3, elem.color_hover, canvasTheme.BUTTON_HOVER_COL);
								ui.text("On Pressed:");
								elem.color_press = drawColorSelection(4, elem.color_press, canvasTheme.BUTTON_PRESSED_COL);

							case Rectangle, FRectangle, Circle, FCircle, Triangle, FTriangle:
								ui.text("Color:");
								elem.color = drawColorSelection(1, elem.color, canvasTheme.BUTTON_COL);

							case ProgressBar, CProgressBar:
								ui.text("Progress:");
								elem.color_progress = drawColorSelection(1, elem.color_progress, canvasTheme.TEXT_COL);
								ui.text("Background:");
								elem.color = drawColorSelection(2, elem.color, canvasTheme.BUTTON_COL);

							case Check, TextInput, KeyInput, Combo, Slider:
								ui.text("Text:");
								elem.color_text = drawColorSelection(1, elem.color_text, canvasTheme.TEXT_COL);
								ui.text("Background:");
								elem.color = drawColorSelection(2, elem.color, canvasTheme.BUTTON_COL);
								ui.text("On Hover:");
								elem.color_hover = drawColorSelection(3, elem.color_hover, canvasTheme.BUTTON_HOVER_COL);

							default:
								ui.text("This element type has no color settings!");

						}
						ui.unindent();
					}

					if (ui.panel(Id.handle({selected: false}), "Align")) {
						ui.indent();

						var alignmentHandle = Id.handle().nest(id, {position: elem.alignment});
						ui.row([1/3, 1/3, 1/3]);
						ui.radio(alignmentHandle, 0, "Left");
						ui.radio(alignmentHandle, 1, "Center");
						ui.radio(alignmentHandle, 2, "Right");
						Editor.selectedElem.alignment = alignmentHandle.position;

						ui.unindent();
					}

					if (ui.panel(Id.handle({selected: false}), "Anchor")) {
						ui.indent();
						var hanch = Id.handle().nest(id, {position: elem.anchor});
						ui.row([4/11,3/11,4/11]);
						ui.radio(hanch, 0, "Top-Left");
						ui.radio(hanch, 1, "Top");
						ui.radio(hanch, 2, "Top-Right");
						ui.row([4/11,3/11,4/11]);
						ui.radio(hanch, 3, "Left");
						ui.radio(hanch, 4, "Center");
						ui.radio(hanch, 5, "Right");
						ui.row([4/11,3/11,4/11]);
						ui.radio(hanch, 6, "Bot-Left");
						ui.radio(hanch, 7, "Bottom");
						ui.radio(hanch, 8, "Bot-Right");
						elem.anchor = hanch.position;
						ui.unindent();
					}

					if (ui.panel(Id.handle({selected: false}), "Script")) {
						ui.indent();
						elem.event = ui.textInput(Id.handle().nest(id, {text: elem.event}), "Event", Right);
						ui.unindent();
					}

					if (ui.panel(Id.handle({selected: false}), "Timeline")) {
						// ui.indent();
						// ui.row([1/2,1/2]);
						// ui.button("Insert");
						// ui.button("Remove");
						// ui.unindent();
					}
				}
			}

			if (ui.tab(htab, "Themes")) {
				// Must be accesible all over this place because when deleting themes,
				// the color handle's child handle at that theme index must be reset.
				var handleThemeColor = Id.handle();
				var handleThemeName = Id.handle();
				var iconSize = 16;

				function drawList(h:zui.Zui.Handle, theme:zui.Themes.TTheme) {
					// Highlight
					if (Editor.selectedTheme == theme) {
						ui.g.color = 0xff205d9c;
						ui.g.fillRect(0, ui._y, ui._windowW, ui.t.ELEMENT_H * ui.SCALE());
						ui.g.color = 0xffffffff;
					}
					// Highlight default theme
					if (theme == Canvas.getTheme(canvas.theme)) {
						var iconMargin = (ui.t.BUTTON_H - iconSize) / 2;
						ui.g.drawSubImage(kha.Assets.images.icons, ui._x + iconMargin, ui._y + iconMargin, 0, 0, 16, 16);
					}

					var started = ui.getStarted();
					// Select
					if (started && !ui.inputDownR) Editor.selectedTheme = theme;

					// Draw
					ui._x += iconSize; // Icon offset
					ui.text(theme.NAME);
					ui._x -= iconSize;
				}

				for (theme in Canvas.themes) drawList(Id.handle(), theme);

				ui.row([1/4, 1/4, 1/4, 1/4]);
				if (ui.button("Add")) {
					var newTheme = Reflect.copy(armory.ui.Themes.light);
					newTheme.NAME = CanvasTools.unique("New Theme", Canvas.themes, "NAME");

					Canvas.themes.push(newTheme);
					Editor.selectedTheme = newTheme;
				}

				if (Editor.selectedTheme == null) ui.enabled = false;
				if (ui.button("Copy")) {
					var newTheme = Reflect.copy(Editor.selectedTheme);
					newTheme.NAME = CanvasTools.unique(newTheme.NAME, Canvas.themes, "NAME");

					Canvas.themes.push(newTheme);
					Editor.selectedTheme = newTheme;
				}
				ui.enabled = true;

				if (Editor.selectedTheme == null) ui.enabled = false;
				var hName = handleThemeName.nest(Canvas.themes.indexOf(Editor.selectedTheme));
				if (ui.button("Rename")) {
					hName.text = Editor.selectedTheme.NAME;
					Popup.showCustom(
						new Zui(ui.ops),
						function(ui:Zui) {
							ui.textInput(hName);
							if (ui.button("OK")) {
								Popup.show = false;
								hwin.redraws = 2;
							}
						},
						Std.int(ui.inputX), Std.int(ui.inputY), 200, 60);
				}
				if (Editor.selectedTheme != null) {
					var name = Editor.selectedTheme.NAME;
					if (hName.changed && Editor.selectedTheme.NAME != hName.text) {
						name = CanvasTools.unique(hName.text, Canvas.themes, "NAME");
						if (canvas.theme == Editor.selectedTheme.NAME) {
							canvas.theme = name;
						}
						Editor.selectedTheme.NAME = name;
					}
				}
				ui.enabled = true;

				if (Canvas.themes.length == 1 || Editor.selectedTheme == null) ui.enabled = false;
				if (ui.button("Delete")) {
					handleThemeColor.unnest(Canvas.themes.indexOf(Editor.selectedTheme));
					handleThemeName.unnest(Canvas.themes.indexOf(Editor.selectedTheme));

					Canvas.themes.remove(Editor.selectedTheme);

					// Canvas default theme was deleted
					if (Canvas.getTheme(canvas.theme) == null) {
						canvas.theme = Canvas.themes[0].NAME;
					}
					Editor.selectedTheme = null;
				}
				ui.enabled = true;

				if (Editor.selectedTheme == null) ui.enabled = false;
				if (ui.button("Apply to Canvas")) canvas.theme = Editor.selectedTheme.NAME;

				ui.enabled = true;

				if (Editor.selectedTheme == null) {
					ui.text("Please select a Theme!");
				} else {
					// A Map would be way better, but its order is not guaranteed.
					var themeColorOptions:Array<Array<String>> = [
						["Text", "TEXT_COL"],
						["Elements", "BUTTON_COL", "BUTTON_TEXT_COL", "BUTTON_HOVER_COL", "BUTTON_PRESSED_COL", "ACCENT_COL", "ACCENT_HOVER_COL", "ACCENT_SELECT_COL"],
						["Other", "PANEL_BG_COL"],
					];

					for (idxCategory in 0...themeColorOptions.length) {
						if (ui.panel(Id.handle().nest(idxCategory, {selected: true}), themeColorOptions[idxCategory][0])) {
							ui.indent();

							var attributes = themeColorOptions[idxCategory].slice(1);

							for (idxElemAttribs in 0...attributes.length) {
								var themeColorOption = attributes[idxElemAttribs];
								// is getField() better?
								ui.row([2/3, 1/3]);
								ui.text(themeColorOption);

								var themeColor = Reflect.getProperty(Editor.selectedTheme, themeColorOption);

								var handleCol = handleThemeColor.nest(Canvas.themes.indexOf(Editor.selectedTheme)).nest(idxCategory).nest(idxElemAttribs, {color: themeColor});
								var col = ui.colorField(handleCol, true);
								Reflect.setProperty(Editor.selectedTheme, themeColorOption, col);
							}

							ui.unindent();
						}
					}
				}
			}

			if (ui.tab(htab, "Assets")) {
				if (ui.button("Import Asset")) {
					Editor.showFiles = true;
					Editor.foldersOnly = false;
					Editor.filesDone = function(path:String) {
						path = StringTools.rtrim(path);
						path = Path.toRelative(path, Main.cwd);
						Assets.importAsset(canvas, path);
					}
				}

				if (canvas.assets.length > 0) {
					ui.text("(Drag and drop assets to canvas)", zui.Zui.Align.Center);

					if (ui.panel(Id.handle({selected: true}), "Imported Assets")) {
						ui.indent();

						var i = canvas.assets.length - 1;
						while (i >= 0) {
							var asset = canvas.assets[i];
							if (!Assets.isPathFont(asset.name) && ui.image(Assets.getImage(asset)) == State.Started) {
								Editor.dragAsset = asset;
							} else if (Assets.isPathFont(asset.name)) {
								var oldFont = ui.ops.font;
								var oldFontSize = ui.fontSize;
								ui.ops.font = Assets.getFont(asset);
								ui.fontSize = Std.int(32 * ui.SCALE());
								ui.text(asset.name);
								ui.ops.font = oldFont;
								ui.fontSize = oldFontSize;
							}
							ui.row([7/8, 1/8]);
							asset.name = ui.textInput(Id.handle().nest(asset.id, {text: asset.name}), "", Right);
							Editor.assetNames[i + 1] = asset.name; // assetNames[0] == ""
							if (ui.button("X")) {
								Assets.getImage(asset).unload();
								canvas.assets.splice(i, 1);
								Editor.assetNames.splice(i + 1, 1);
							}
							i--;
						}

						ui.unindent();
					}
				}
				else ui.text("(Drag and drop images and fonts here)", zui.Zui.Align.Center);
			}

			if (ui.tab(htab, "Preferences")) {
				if (ui.panel(Id.handle({selected: true}), "Application")) {
					ui.indent();

					var hscale = Id.handle({value: 1.0});
					ui.slider(hscale, "UI Scale", 0.5, 4.0, true);
					if (hscale.changed && !ui.inputDown) {
						ui.setScale(hscale.value);
						Editor.windowW = Std.int(Editor.defaultWindowW * hscale.value);
					}

					Main.prefs.window_vsync = ui.check(Id.handle({selected: true}), "VSync");

					ui.unindent();
				}

				if (ui.panel(Id.handle({selected: true}), "Grid")) {
					ui.indent();
					var gsize = Id.handle({value: 20});
					ui.slider(gsize, "Grid Size", 1, 128, true, 1);
					if (gsize.changed) {
						Editor.gridSize = Std.int(gsize.value);
						Editor.redrawGrid = true;
					}

					Editor.gridSnapPos = ui.check(Id.handle({selected: true}), "Grid Snap Position");
					if (ui.isHovered) ui.tooltip("Snap the element's position to the grid");
					Editor.gridSnapBounds = ui.check(Id.handle({selected: false}), "Grid Snap Bounds");
					if (ui.isHovered) ui.tooltip("Snap the element's bounds to the grid");
					Editor.gridUseRelative = ui.check(Id.handle({selected: true}), "Use Relative Grid");
					if (ui.isHovered) ui.tooltip("Use a grid that's relative to the selected element");

					Editor.useRotationSteps = ui.check(Id.handle({selected: false}), "Use Fixed Rotation Steps");
					if (ui.isHovered) ui.tooltip("Rotate elements by a fixed step size");
					var rotStepHandle = Id.handle({value: 15});
					if (Editor.useRotationSteps) {
						ui.slider(rotStepHandle, "Rotation Step Size", 1, 180, true, 1);
						if (rotStepHandle.changed) {
							Editor.rotationSteps = Math.toRadians(rotStepHandle.value);
						}
					}

					ui.unindent();
				}

				// if (ui.button("Save")) {
				// 	#if kha_krom
				// 	Krom.fileSaveBytes("config.arm", haxe.io.Bytes.ofString(haxe.Json.stringify(armory.data.Config.raw)).getData());
				// 	#end
				// }
				// ui.text("armory2d");

				if (ui.panel(Id.handle({selected: true}), "Shortcuts")){
					ui.indent();

					ui.row([1/2, 1/2]);
					ui.text("Select");
					var selectMouseHandle = Id.handle({position: 0});
					ui.combo(selectMouseHandle, ["Left Click", "Right Click"], "");
					if (ui.isHovered) ui.tooltip("Mouse button used for element selection.");
					if (selectMouseHandle.changed) {
						Main.prefs.keyMap.selectMouseButton = ["Left", "Right"][selectMouseHandle.position];
					}

					ui.separator(8, false);
					ui.row([1/2, 1/2]);
					ui.text("Grab");
					Main.prefs.keyMap.grabKey = ui.keyInput(Id.handle({value: KeyCode.G}), "Key");
					if (ui.isHovered) ui.tooltip("Key used for grabbing elements");

					ui.row([1/2, 1/2]);
					ui.text("Rotate");
					Main.prefs.keyMap.rotateKey = ui.keyInput(Id.handle({value: KeyCode.R}), "Key");
					if (ui.isHovered) ui.tooltip("Key used for rotating elements");

					ui.row([1/2, 1/2]);
					ui.text("Size");
					Main.prefs.keyMap.sizeKey = ui.keyInput(Id.handle({value: KeyCode.S}), "Key");
					if (ui.isHovered) ui.tooltip("Key used for resizing elements");

					ui.separator(8, false);
					ui.row([1/2, 1/2]);
					ui.text("Precision Transform");
					Main.prefs.keyMap.slowMovement = ui.keyInput(Id.handle({value: KeyCode.Shift}), "Key");
					if (ui.isHovered) ui.tooltip("More precise transformations");

					ui.row([1/2, 1/2]);
					ui.text("Invert Grid");
					Main.prefs.keyMap.gridInvert = ui.keyInput(Id.handle({value: KeyCode.Control}), "Key");
					if (ui.isHovered) ui.tooltip("Invert the grid setting");

					ui.row([1/2, 1/2]);
					ui.text("Invert Rel. Grid");
					Main.prefs.keyMap.gridInvertRelative = ui.keyInput(Id.handle({value: KeyCode.Alt}), "Key");
					if (ui.isHovered) ui.tooltip("Invert the relative grid setting");

					ui.unindent();
				}

				if (ui.panel(Id.handle({selected: false}), "Console")) {
					ui.indent();

					//ui.text(lastTrace);
					ui.text("Mouse X: "+ ui.inputX);
					ui.text("Mouse Y: "+ ui.inputY);

					ui.unindent();
				}
			}
		}
	}
}
