package armory.logicnode;

class ColorgradingSetGlobalNode extends LogicNode {

    public var property0:Dynamic;
    public var property1:Dynamic;
    public var property2:Dynamic;
    public var property3:Dynamic;

    var value:Dynamic;
    var whitebalance:Dynamic;
    var tint:Dynamic;
    var saturation:Dynamic;
    var contrast:Dynamic;
    var gamma:Dynamic;
    var gain:Dynamic;
    var offset:Dynamic;

	public function new(tree:LogicTree) {
		super(tree);
	}

	override function run(from:Int) {

        if(property0 == "Uniform"){

            armory.renderpath.Postprocess.colorgrading_global_uniforms[0][0] = inputs[1].get();
            armory.renderpath.Postprocess.colorgrading_global_uniforms[1][0] = inputs[2].get().x;
            armory.renderpath.Postprocess.colorgrading_global_uniforms[1][1] = inputs[2].get().y;
            armory.renderpath.Postprocess.colorgrading_global_uniforms[1][2] = inputs[2].get().z;

            for (i in 2...7){
                armory.renderpath.Postprocess.colorgrading_global_uniforms[i][0] = inputs[i+1].get();
                armory.renderpath.Postprocess.colorgrading_global_uniforms[i][1] = inputs[i+1].get();
                armory.renderpath.Postprocess.colorgrading_global_uniforms[i][2] = inputs[i+1].get();
            }

        } else if (property0 == "RGB") {

            armory.renderpath.Postprocess.colorgrading_global_uniforms[0][0] = inputs[1].get();

            for (i in 1...7){
                armory.renderpath.Postprocess.colorgrading_global_uniforms[i][0] = inputs[i+1].get().x;
                armory.renderpath.Postprocess.colorgrading_global_uniforms[i][1] = inputs[i+1].get().y;
                armory.renderpath.Postprocess.colorgrading_global_uniforms[i][2] = inputs[i+1].get().z;
            }

            var value:Dynamic = inputs[0].get();
            var whitebalance:Float = inputs[1].get();
            var tint:iron.math.Vec4 = inputs[2].get();
            var saturation:Float = inputs[3].get();
            var contrast:Float = inputs[4].get();
            var gamma:Float = inputs[5].get();
            var gain:Float = inputs[6].get();
            var offset:Float = inputs[7].get();

        } else if (property0 == "Preset File") {
            return;
        } else {
            return;
        }

		runOutput(0);
	}
}
