// Auto-generated
package ;
class Main {
    public static inline var projectName = 'untitled';
    public static inline var projectPackage = 'arm';
    public static inline var projectAssets = 9;
    static inline var projectWidth = 960;
    static inline var projectHeight = 540;
    static inline var projectSamplesPerPixel = 1;
    static inline var projectScene = 'Scene';
    static var state:Int;
    #if js
    static function loadLib(name:String) {
        kha.LoaderImpl.loadBlobFromDescription({ files: [name] }, function(b:kha.Blob) {
            untyped __js__("(1, eval)({0})", b.toString());
            state--;
            start();
        });
    }
    #end
    public static function main() {
        iron.system.CompileTime.importPackage('armory.trait');
        iron.system.CompileTime.importPackage('armory.renderpath');
        iron.system.CompileTime.importPackage('arm');
        state = 1;
        #if (js && arm_physics) state++; loadLib("ammo.js"); #end
        #if (js && arm_navigation) state++; loadLib("recast.js"); #end
        state--; start();
    }
    static function start() {
        if (state > 0) return;
        armory.object.Uniforms.register();
        kha.System.init({title: projectName, width: projectWidth, height: projectHeight, samplesPerPixel: projectSamplesPerPixel}, function() {
            iron.App.init(function() {

                iron.Scene.setActive(projectScene, function(object:iron.object.Object) {
                    object.addTrait(new armory.trait.internal.SpaceArmory());
                });
            });
        });
    }
}
