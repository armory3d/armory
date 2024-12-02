package iron.object;

#if arm_morph_target

import kha.arrays.Float32Array;
import kha.Image;
import kha.FastFloat;
import iron.data.Data;
import iron.data.SceneFormat;

class MorphTarget {

    public var data: TMorphTarget;
    public var numMorphTargets: Int = 0;
    public var morphImageSize: Int = 0;
    public var morphBlockSize: Int = 0;
    public var scaling: FastFloat;
    public var offset: FastFloat;
    public var morphWeights: Float32Array;
    public var morphDataPos: Image;
    public var morphDataNor: Image;
    public var morphMap: Map<String, Int> = null;

    public function new(data: TMorphTarget) {
        initWeights(data.morph_target_defaults);
        scaling = data.morph_scale;
        offset = data.morph_offset;
        numMorphTargets = data.num_morph_targets;
        morphImageSize = data.morph_img_size;
        morphBlockSize = data.morph_block_size;

        Data.getImage(data.morph_target_data_file + "_morph_pos.png", function(img: Image) {
            if (img != null) morphDataPos = img;
        });
        Data.getImage(data.morph_target_data_file + "_morph_nor.png", function(img: Image) {
            if (img != null) morphDataNor = img;
        });
        morphMap = new Map();

        var i = 0;
        for (name in data.morph_target_ref) {
            morphMap.set(name, i);
            i++;
        }
    }

    inline function initWeights(defaults: Float32Array) {
        morphWeights = new Float32Array(defaults.length);
        for (i in 0...morphWeights.length) {
            morphWeights.set(i, defaults.get(i));
        }
    }

    public function setMorphValue(name: String, value: Float) {
        var i = morphMap.get(name);
        if (i != null) {
            morphWeights.set(i, value);
        }
    }
}

#end
