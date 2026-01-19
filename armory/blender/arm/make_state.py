import arm

if not arm.is_reload(__name__):
    arm.enable_reload(__name__)

    redraw_ui = False
    target = 'krom'
    last_target = 'krom'
    export_gapi = ''
    last_resx = 0
    last_resy = 0
    last_scene = ''
    last_world_defs = ''
    proc_play = None
    proc_build = None
    proc_publish_build = None
    mod_scripts = []
    is_export = False
    is_play = False
    is_publish = False
    is_n64 = False
