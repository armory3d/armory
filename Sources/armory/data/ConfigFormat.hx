package armory.data;

typedef TConfig = {
	var version:String;
	var debug_console:Bool;
	var window_mode:Int; // window, borderless, fullscreen
	var window_w:Int;
	var window_h:Int;
	var window_vsync:Bool;
	var window_msaa:Int;
	var rp_supersample:Int; // 1, 1.5, 2, 4
	var rp_shadowmap:Int;
	var rp_voxelgi:Int; // off, ao, ao_revox, gi, gi_revox
	var rp_ssgi:Bool;
	var rp_ssr:Bool;
	var rp_bloom:Bool;
	var rp_motionblur:Bool;
}
