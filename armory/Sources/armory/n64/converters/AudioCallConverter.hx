package armory.n64.converters;

#if macro
import haxe.macro.Expr;
import haxe.macro.Context;
import armory.n64.IRTypes;
import armory.n64.converters.ICallConverter;

using StringTools;

/**
 * Converts Aura audio API calls to libdragon N64 audio functions.
 *
 * Handles patterns like:
 *   Aura.mixChannels["music"].setVolume(v) -> arm_audio_set_mix_volume(AUDIO_MIX_MUSIC, v)
 *   Aura.createCompBufferChannel(sound, loop, mixCh) -> arm_audio_play(path, mix_ch, loop)
 *   handle.stop() -> arm_audio_stop(&handle)
 *   handle.finished -> handle.finished (bool field access)
 *   handle.setVolume(v) -> arm_audio_set_volume(&handle, v)
 *
 * Mix channel names are extracted from Aura.mixChannels["name"] accesses and converted
 * to C constants: AUDIO_MIX_NAME (e.g., "music" -> AUDIO_MIX_MUSIC)
 *
 * Also handles:
 *   Assets.sounds.sound_name -> "rom:/sound_name.wav64" (sound path string)
 */
class AudioCallConverter implements ICallConverter {
    public function new() {}

    public function tryConvert(obj:Expr, method:String, args:Array<IRNode>, rawParams:Array<Expr>, ctx:IExtractorContext):IRNode {
        // Handle Aura.* calls
        switch (obj.expr) {
            case EConst(CIdent("Aura")):
                return convertAuraCall(method, args, rawParams, ctx);

            // Handle Aura.mixChannels["name"].setVolume(v)
            // This comes as: obj = EArray(EField(Aura, mixChannels), "music"), method = setVolume
            case EArray(arrayObj, indexExpr):
                switch (arrayObj.expr) {
                    case EField(auraObj, "mixChannels"):
                        switch (auraObj.expr) {
                            case EConst(CIdent("Aura")):
                                return convertMixChannelCall(indexExpr, method, args, ctx);
                            default:
                        }
                    default:
                }
            default:
        }

        // Handle sound handle method calls (handle.play(), handle.stop(), handle.setVolume())
        // These are on variables typed as BaseChannelHandle or similar
        var objType = getExprTypeSafe(obj, ctx);
        if (objType != null && (objType.indexOf("ChannelHandle") >= 0 || objType.indexOf("Handle") >= 0)) {
            return convertHandleCall(obj, method, args, ctx);
        }

        return null;
    }

    function convertAuraCall(method:String, args:Array<IRNode>, rawParams:Array<Expr>, ctx:IExtractorContext):IRNode {
        var meta = ctx.getMeta();

        switch (method) {
            case "createCompBufferChannel":
                // Aura.createCompBufferChannel(sound, loop, mixChannel)
                // -> arm_audio_play(path, mix_channel, loop)
                if (args.length >= 3) {
                    var soundArg = args[0];
                    var loopArg = args[1];
                    var mixChArg = args[2];

                    // Loop boolean
                    var loopVal = loopArg.value != null ? (loopArg.value == true ? "true" : "false") : "false";

                    // Mix channel - extract from Aura.mixChannels["name"]
                    var mixCh = extractMixChannelFromArg(rawParams[2]);

                    // Return node with args - let emitter handle sound path
                    return {
                        type: "audio_play",
                        args: [soundArg],  // Sound path/variable
                        props: {
                            mix_channel: mixCh,
                            loop: loopVal
                        }
                    };
                }
                // Fallback with fewer args
                return { type: "skip" };

            case "init":
                // Aura.init() is handled by engine init, skip
                return { type: "skip" };

            default:
                // Unknown Aura method
                return null;
        }
    }

    function convertMixChannelCall(indexExpr:Expr, method:String, args:Array<IRNode>, ctx:IExtractorContext):IRNode {
        // Extract the channel name from the index expression (e.g., "music")
        var channelName = extractStringFromExpr(indexExpr);
        var cChannel = getMixChannelConstant(channelName);

        switch (method) {
            case "setVolume":
                if (args.length >= 1) {
                    var volArg = args[0];
                    var volCode = volArg.c_code != null ? volArg.c_code : (volArg.value != null ? Std.string(volArg.value) : "1.0f");
                    return {
                        type: "audio_mix_volume",
                        c_code: 'arm_audio_set_mix_volume(' + cChannel + ', ' + volCode + ')',
                        props: {
                            channel: cChannel,
                            volume: volCode
                        }
                    };
                }

            case "getVolume":
                return {
                    type: "audio_mix_volume_get",
                    c_code: 'arm_audio_get_mix_volume(' + cChannel + ')',
                    props: { channel: cChannel }
                };

            default:
        }

        return null;
    }

    function convertHandleCall(obj:Expr, method:String, args:Array<IRNode>, ctx:IExtractorContext):IRNode {
        // Convert the handle expression to an IR node so the emitter can properly prefix it
        var handleNode = ctx.exprToIR(obj);

        switch (method) {
            case "play":
                // Restart playback from beginning
                return {
                    type: "audio_handle_play",
                    props: {method: "play"},
                    children: [handleNode]
                };

            case "stop":
                return {
                    type: "audio_handle_stop",
                    props: {method: "stop"},
                    children: [handleNode]
                };

            case "pause":
                // libdragon doesn't have pause, use stop
                return {
                    type: "audio_handle_pause",
                    props: {method: "pause"},
                    children: [handleNode]
                };

            case "setVolume":
                if (args.length >= 1) {
                    return {
                        type: "audio_handle_volume",
                        props: {method: "setVolume"},
                        children: [handleNode],
                        args: [args[0]]
                    };
                }

            default:
        }

        return null;
    }

    function extractMixChannelFromArg(expr:Expr):String {
        // Handle Aura.mixChannels["name"] pattern
        switch (expr.expr) {
            case EArray(arrayObj, indexExpr):
                switch (arrayObj.expr) {
                    case EField(_, "mixChannels"):
                        var channelName = extractStringFromExpr(indexExpr);
                        return getMixChannelConstant(channelName);
                    default:
                }
            default:
        }
        return "AUDIO_MIX_MASTER";
    }

    /**
     * Convert a mix channel name to a C constant.
     * Follows Aura.mixChannels naming: "music" -> AUDIO_MIX_MUSIC
     */
    function getMixChannelConstant(name:String):String {
        if (name == null || name == "") return "AUDIO_MIX_MASTER";
        // Convert channel name to uppercase C constant: "music" -> "AUDIO_MIX_MUSIC"
        return 'AUDIO_MIX_' + name.toUpperCase();
    }

    function extractStringFromExpr(expr:Expr):String {
        switch (expr.expr) {
            case EConst(CString(s, _)):
                return s;
            default:
                return null;
        }
    }

    static function extractVarName(expr:Expr):String {
        switch (expr.expr) {
            case EConst(CIdent(name)):
                return name;
            case EField(_, name):
                return name;
            default:
                return null;
        }
    }

    function getExprTypeSafe(expr:Expr, ctx:IExtractorContext):String {
        try {
            return ctx.getExprType(expr);
        } catch (e:Dynamic) {
            return null;
        }
    }

    static function getExprTypeSafeStatic(expr:Expr):String {
        try {
            var typed = Context.typeExpr(expr);
            if (typed != null && typed.t != null) {
                return haxe.macro.TypeTools.toString(typed.t);
            }
        } catch (e:Dynamic) {}
        return null;
    }
}

#end
