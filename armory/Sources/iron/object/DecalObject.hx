package iron.object;

import kha.graphics4.Graphics;
import iron.data.MaterialData;
import iron.data.ConstData;
import iron.object.Uniforms;

class DecalObject extends Object {

#if rp_decals

	public var material: MaterialData;

	public function new(material: MaterialData) {
		super();
		this.material = material;
		Scene.active.decals.push(this);
	}

	public override function remove() {
		if (Scene.active != null) Scene.active.decals.remove(this);
		super.remove();
	}

	// Called before rendering decal in render path
	public function render(g: Graphics, context: String, bindParams: Array<String>) {

		// Check context skip
		if (material.raw.skip_context != null &&
			material.raw.skip_context == context) {
			return;
		}

		transform.update();

		var materialContext: MaterialContext = null;
		for (i in 0...material.raw.contexts.length) {
			if (material.raw.contexts[i].name == context) {
				materialContext = material.contexts[i]; // Single material decals
				break;
			}
		}
		var shaderContext = material.shader.getContext(context);

		g.setPipeline(shaderContext.pipeState);

		Uniforms.setContextConstants(g, shaderContext, bindParams);
		Uniforms.setObjectConstants(g, shaderContext, this);
		Uniforms.setMaterialConstants(g, shaderContext, materialContext);

		g.setVertexBuffer(ConstData.boxVB);
		g.setIndexBuffer(ConstData.boxIB);
		g.drawIndexedVertices();
	}

#end
}
