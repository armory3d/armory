package armory.logicnode;

import kha.Color;
import kha.Image;
import kha.Scheduler;

class DrawImageSequenceNode extends LogicNode {

	var images: Array<Image> = [];
	var currentImgIdx = 0;
	var timetaskID = -1;

	public function new(tree: LogicTree) {
		super(tree);
	}

	override function run(from: Int) {
		switch (from) {
			case 0: // Start
				if (timetaskID != -1) {
					// Do nothing if already running
					return;
				} else {
					// We could still be rendering the last image, reset in this case
					tree.removeRender2D(render2D);
					currentImgIdx = 0;
				}

				final startIndex = inputs[9].get();
				final endIndex = inputs[10].get();
				assert(Error, startIndex >= 0, "Start Index must not be negative!");
				assert(Error, endIndex >= 0, "End Index must not be negative!");
				assert(Error, startIndex <= endIndex, "Start Index must not be larger than End Index!");

				final numImages = endIndex + 1 - startIndex;
				images.resize(numImages);

				final imagePrefix = inputs[2].get();
				final imageExtension = inputs[3].get();

				final waitForLoad = inputs[13].get();
				var numLoaded = 0;
				for (i in startIndex...endIndex + 1) {
					iron.data.Data.getImage(imagePrefix + i + '.' + imageExtension, (image: Image) -> {
						images[i - startIndex] = image;
						numLoaded++;

						if (waitForLoad && numLoaded == numImages) {
							startTimetask();
							runOutput(0);
						}
					});
				}

				if (!waitForLoad) {
					startTimetask();
					runOutput(0);
				}

				tree.notifyOnRender2D(render2D);

			case 1: // Stop
				tree.removeRender2D(render2D);
				currentImgIdx = 0;
				stopTimetask();
				runOutput(1);
		}
	}

	inline function startTimetask() {
		final rate = inputs[11].get();
		timetaskID = Scheduler.addTimeTask(() -> {
			currentImgIdx++;
			if (currentImgIdx == images.length) {
				final loop = inputs[12].get();
				if (loop) {
					currentImgIdx = 0;
				} else {
					currentImgIdx--;
					stopTimetask();
					runOutput(1);
				}
			}
		}, rate, rate); // Rate is also first offset so that we start at array index 0
	}

	inline function stopTimetask() {
		if (timetaskID != -1) {
			Scheduler.removeTimeTask(timetaskID);
			timetaskID = -1;
		}
	}

	function render2D(g:kha.graphics2.Graphics) {
		if (images[currentImgIdx] == null) {
			return;
		}

		final colorVec = inputs[4].get();
		g.color = Color.fromFloats(colorVec.x, colorVec.y, colorVec.z, colorVec.w);

		g.drawScaledImage(images[currentImgIdx], inputs[5].get(), inputs[6].get(), inputs[7].get(), inputs[8].get());
	}
}
