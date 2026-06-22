import arm.utils
from arm import assets

def parse_context(
    c: dict,
    sres: dict,
    asset,
    defs: list[str],
    vert: list[str] = None,
    frag: list[str] = None,
):
    con = {
        "name": c["name"],
        "constants": [],
        "texture_units": [],
        "vertex_elements": [],
    }
    sres["contexts"].append(con)

    # Names
    con["vertex_shader"] = c["vertex_shader"].rsplit(".", 1)[0].split("/")[-1]
    if con["vertex_shader"] not in asset:
        asset.append(con["vertex_shader"])

    con["fragment_shader"] = c["fragment_shader"].rsplit(".", 1)[0].split("/")[-1]
    if con["fragment_shader"] not in asset:
        asset.append(con["fragment_shader"])

    if "geometry_shader" in c:
        con["geometry_shader"] = c["geometry_shader"].rsplit(".", 1)[0].split("/")[-1]
        if con["geometry_shader"] not in asset:
            asset.append(con["geometry_shader"])

    if "tesscontrol_shader" in c:
        con["tesscontrol_shader"] = (
            c["tesscontrol_shader"].rsplit(".", 1)[0].split("/")[-1]
        )
        if con["tesscontrol_shader"] not in asset:
            asset.append(con["tesscontrol_shader"])

    if "tesseval_shader" in c:
        con["tesseval_shader"] = c["tesseval_shader"].rsplit(".", 1)[0].split("/")[-1]
        if con["tesseval_shader"] not in asset:
            asset.append(con["tesseval_shader"])

    if "color_attachments" in c:
        con["color_attachments"] = c["color_attachments"]
        for i in range(len(con["color_attachments"])):
            if con["color_attachments"][i] == "_HDR":
                con["color_attachments"][i] = "RGBA32" if "_LDR" in defs else "RGBA64"

    # Params
    params = [
        "depth_write",
        "compare_mode",
        "cull_mode",
        "blend_source",
        "blend_destination",
        "blend_operation",
        "alpha_blend_source",
        "alpha_blend_destination",
        "alpha_blend_operation",
        "color_writes_red",
        "color_writes_green",
        "color_writes_blue",
        "color_writes_alpha",
        "conservative_raster",
    ]

    for p in params:
        if p in c:
            con[p] = c[p]

    # Parse shaders
    if vert is None:
        with open(c["vertex_shader"], encoding="utf-8") as f:
            vert = f.read().splitlines()
    parse_shader(sres, c, con, defs, vert, True)  # Parse attribs for vertex shader

    if frag is None:
        with open(c["fragment_shader"], encoding="utf-8") as f:
            frag = f.read().splitlines()
    parse_shader(sres, c, con, defs, frag, False)

    if "geometry_shader" in c:
        with open(c["geometry_shader"], encoding="utf-8") as f:
            geom = f.read().splitlines()
        parse_shader(sres, c, con, defs, geom, False)

    if "tesscontrol_shader" in c:
        with open(c["tesscontrol_shader"], encoding="utf-8") as f:
            tesc = f.read().splitlines()
        parse_shader(sres, c, con, defs, tesc, False)

    if "tesseval_shader" in c:
        with open(c["tesseval_shader"], encoding="utf-8") as f:
            tese = f.read().splitlines()
        parse_shader(sres, c, con, defs, tese, False)


def parse_shader(
    sres, c: dict, con: dict, defs: list[str], lines: list[str], parse_attributes: bool
):
    """Parses the given shader to get information about the used vertex
    elements, uniforms and constants. This information is later used in
    Iron to check what data each shader requires.

    @param defs A list of set defines for the preprocessor
    @param lines The list of lines of the shader file
    @param parse_attributes Whether to parse vertex elements
    """
    vertex_elements_parsed = False
    vertex_elements_parsing = False

    # Stack of the state of all preprocessor conditions for the current
    # line. If there is a `False` in the stack, at least one surrounding
    # condition is false and the line must not be parsed
    stack: list[bool] = []

    if not parse_attributes:
        vertex_elements_parsed = True

    for line in lines:
        line = line.lstrip()

        # Preprocessor
        if line.startswith("#if"):  # if, ifdef, ifndef
            s = line.split(" ")[1]
            found = s in defs
            if line.startswith("#ifndef"):
                found = not found
            stack.append(found)
            continue

        if line.startswith("#else"):
            stack[-1] = not stack[-1]
            continue

        if line.startswith("#endif"):
            stack.pop()
            continue

        # Skip lines if the stack contains at least one preprocessor
        # condition that is not fulfilled
        skip = False
        for condition in stack:
            if not condition:
                skip = True
                break
        if skip:
            continue

        if not vertex_elements_parsed and line.startswith("in "):
            vertex_elements_parsing = True
            s = line.split(" ")
            con["vertex_elements"].append(
                {
                    "data": "float" + s[1][-1:],
                    "name": s[2][:-1],  # [:1] to get rid of the semicolon
                }
            )

        # Stop the vertex element parsing if no other vertex elements
        # follow directly (assuming all vertex elements are positioned
        # directly after each other apart from empty lines and comments)
        if (
            vertex_elements_parsing
            and len(line) > 0
            and not line.startswith("//")
            and not line.startswith("in ")
        ):
            vertex_elements_parsed = True

        if line.startswith("uniform ") or line.startswith(
            "//!uniform"
        ):  # Uniforms included from header files
            s = line.split(" ")
            # Examples:
            #   uniform sampler2D myname;
            #   uniform layout(RGBA8) image3D myname;
            if s[1].startswith("layout"):
                ctype = s[2]
                cid = s[3]
                if cid[-1] == ";":
                    cid = cid[:-1]
            else:
                ctype = s[1]
                cid = s[2]
                if cid[-1] == ";":
                    cid = cid[:-1]

            found = False  # Uniqueness check
            if (
                ctype.startswith("sampler")
                or ctype.startswith("image")
                or ctype.startswith("uimage")
            ):  # Texture unit
                for tu in con["texture_units"]:
                    if tu["name"] == cid:
                        # Texture already present
                        found = True
                        break
                if not found:
                    if cid[-1] == "]":  # Array of samplers - sampler2D mySamplers[2]
                        # Add individual units - mySamplers[0], mySamplers[1]
                        for i in range(int(cid[-2])):
                            tu = {"name": cid[:-2] + str(i) + "]"}
                            con["texture_units"].append(tu)
                    else:
                        tu = {"name": cid}
                        con["texture_units"].append(tu)
                        if ctype.startswith("image") or ctype.startswith("uimage"):
                            tu["is_image"] = True

                        check_link(c, defs, cid, tu)

            else:  # Constant
                if cid.find("[") != -1:  # Float arrays
                    cid = cid.split("[")[0]
                    ctype = "floats"
                for const in con["constants"]:
                    if const["name"] == cid:
                        found = True
                        break
                if not found:
                    const = {"type": ctype, "name": cid}
                    con["constants"].append(const)

                    check_link(c, defs, cid, const)


def check_link(source_context: dict, defs: list[str], cid: str, out: dict):
    """Checks whether the uniform/constant with the given name (`cid`)
    has a link stated in the json (`source_context`) that can be safely
    included based on the given defines (`defs`). If that is the case,
    the found link is written to the `out` dictionary.
    """
    for link in source_context["links"]:
        if link["name"] == cid:
            valid_link = True

            # Optionally only use link if at least
            # one of the given defines is set
            if "ifdef" in link:
                def_found = False
                for d in defs:
                    for link_def in link["ifdef"]:
                        if d == link_def:
                            def_found = True
                            break
                    if def_found:
                        break
                if not def_found:
                    valid_link = False

            # Optionally only use link if none of
            # the given defines are set
            if "ifndef" in link:
                def_found = False
                for d in defs:
                    for link_def in link["ifndef"]:
                        if d == link_def:
                            def_found = True
                            break
                    if def_found:
                        break
                if def_found:
                    valid_link = False

            if valid_link:
                out["link"] = link["link"]
            break


def make(
    res: dict, base_name: str, json_data: dict, fp, defs: list[str], make_variants: bool
):
    sres = {"name": base_name, "contexts": []}
    res["shader_datas"].append(sres)
    asset = assets.shader_passes_assets[base_name]

    vert = None
    frag = None
    has_variants = "variants" in json_data and len(json_data["variants"]) > 0
    if make_variants and has_variants:
        d = json_data["variants"][0]
        if d in defs:
            # Write shader variant with define
            c = json_data["contexts"][0]
            with open(c["vertex_shader"], encoding="utf-8") as f:
                vert = f.read().split("\n", 1)[1]
                vert = "#version 450\n#define " + d + "\n" + vert

            with open(c["fragment_shader"], encoding="utf-8") as f:
                frag = f.read().split("\n", 1)[1]
                frag = "#version 450\n#define " + d + "\n" + frag

            with open(
                arm.utils.get_fp_build()
                + "/compiled/Shaders/"
                + base_name
                + d
                + ".vert.glsl",
                "w",
                encoding="utf-8",
            ) as f:
                f.write(vert)

            with open(
                arm.utils.get_fp_build()
                + "/compiled/Shaders/"
                + base_name
                + d
                + ".frag.glsl",
                "w",
                encoding="utf-8",
            ) as f:
                f.write(frag)

            # Add context variant
            c2 = c.copy()
            c2["vertex_shader"] = base_name + d + ".vert.glsl"
            c2["fragment_shader"] = base_name + d + ".frag.glsl"
            c2["name"] = c["name"] + d
            parse_context(c2, sres, asset, defs, vert.splitlines(), frag.splitlines())

    for c in json_data["contexts"]:
        parse_context(c, sres, asset, defs)
