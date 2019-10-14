package armory.object;

class GreasePencilObject {

	static var gpFrame = 0;

	public function drawGreasePencil(params:Array<String>, root:Object) {
		var gp = Scene.active.greasePencil;
		if (gp == null) return;

		var g = currentRenderTarget;
		var lamp = getLamp(currentLampIndex);
		var context = GreasePencilData.getContext(params[0]);
		g.setPipeline(context.pipeState);
		Uniforms.setConstants(g, context, null, camera, lamp, null);

		// Draw layers
		for (layer in gp.layers) {
			// Next frame
			if (layer.frames.length - 1 > layer.currentFrame && gpFrame >= layer.frames[layer.currentFrame + 1].raw.frame_number) {
				layer.currentFrame++;
			}
			var frame = layer.frames[layer.currentFrame];
			if (frame.numVertices > 0) {

				// Stroke
				#if (js && kha_webgl)
				// TODO: Construct triangulated lines from points instead
				g.setVertexBuffer(frame.vertexStrokeBuffer);
				kha.SystemImpl.gl.lineWidth(3);
				var start = 0;
				for (i in frame.raw.num_stroke_points) {
					kha.SystemImpl.gl.drawArrays(js.html.webgl.GL.LINE_STRIP, start, i);
					start += i;
				}
				#end

				// Fill
				g.setVertexBuffer(frame.vertexBuffer);
				g.setIndexBuffer(frame.indexBuffer);
				g.drawIndexedVertices();
			}
		}

		gpFrame++;

		// Reset timeline
		if (gpFrame > GreasePencilData.frameEnd) {
			gpFrame = 0;
			for (layer in gp.layers) layer.currentFrame = 0;
		}

		end(g);
	}
}
