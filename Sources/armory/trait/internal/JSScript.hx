package armory.trait.internal;

import iron.Trait;

class JSScript extends Trait {

    public function new(scriptBlob:String) {
        super();

        var src =  Reflect.field(kha.Assets.blobs, scriptBlob + '_js').toString();
        untyped __js__("eval(src);");
    }
}
