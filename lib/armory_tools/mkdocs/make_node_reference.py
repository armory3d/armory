"""
Generates the logic nodes reference page for Armory3D's wiki:
https://github.com/armory3d/armory/wiki/reference

USAGE:
    First, generate the node screenshots (1). After that, open a
    terminal in the folder of this script and execute the following
    command (Blender must have the Armory add-on activated of course):

    path/to/blender.exe -b -P make_node_reference.py"

    This will create markdown files containing the reference in the
    `/output` folder relative to this script. You can copy the content
    from those files into the logic node reference articles. DO NOT
    commit the generated files to the armory_tools repo!

    Todo: Create a GitHub action to automatically update the reference
    for each release.

    (1) https://github.com/armory3d/armory_wiki_images/blob/master/logic_nodes/make_screenshots.py
        Please also read the usage notes in that file!
"""
import ensurepip
import itertools
import os
import subprocess
import sys
from typing import List

import bpy
from nodeitems_utils import NodeItem

from arm.logicnode import arm_nodes
import arm.props

ensurepip.bootstrap()
os.environ.pop("PIP_REQ_TRACKER", None)
subprocess.check_output([sys.executable, '-m', 'pip', 'install', '--upgrade', 'markdownmaker'])

# If pip wants an update, toggle this flag before execution
UPDATE_PIP = False
if UPDATE_PIP:
    subprocess.check_output([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'])

from markdownmaker.document import Document
from markdownmaker.markdownmaker import *

PY_NODE_DIR = "https://github.com/armory3d/armory/blob/main/armory/blender/arm/logicnode/"
HX_NODE_DIR = "https://github.com/armory3d/armory/blob/main/armory/Sources/armory/logicnode/"
IMG_DIR = "https://github.com/armory3d/armory_wiki_images/raw/master/logic_nodes/"

OUTPUT_DIR = os.path.abspath(__file__)
OUTPUT_DIR = os.path.join(os.path.dirname(OUTPUT_DIR), "output")


def get_anchor(text: str) -> str:
    """Gets the GitHub anchor id for a link."""
    return "#" + text.lower().replace(" ", "-")


def make_node_link(nodename: str) -> str:
    """Create a link to a node given by the name of the node"""
    return Link(label=InlineCode(nodename), url=get_anchor(nodename))


def get_nodetype(typename: str):
    """Convert the type name to the actual type."""
    return bpy.types.bpy_struct.bl_rna_get_subclass_py(typename)


def format_desc(description_text: str, *, indented=False) -> str:
    """Format the raw description string."""
    out = ""

    # Indentation for list items is 2 spaces per markdown standard in
    # this case. For now, sub-lists are indented one level only, more
    # is not required currently
    line_start = "  " if indented else ""

    # Whether the last line was empty (ignore multiple empty lines)
    last_empty = False

    for line in description_text.splitlines():
        line = line.strip()

        # List item. Explicitly check for space after "-", might be a negative number else
        if line.startswith("- "):
            out += "\n" + line_start + line
            last_empty = False

        elif line == "":
            if last_empty:
                continue
            out += "\n"
            last_empty = True

        else:
            if last_empty:
                out += "\n" + line_start + line  # Create a full empty line above the start of a paragraph
            else:
                out += " " + line  # Combine one paragraph to a single line
            last_empty = False

    # Remove any left-over whitespace at the beginning/end
    return out.strip()


def generate_node_documentation(doc: Document, nodeitem: NodeItem, category: arm_nodes.ArmNodeCategory):
    nodetype = get_nodetype(nodeitem.nodetype)
    docstring: str = nodetype.__doc__
    if docstring is not None:
        doc_parts = docstring.split("@")

        # Show docstring until the first "@"
        node_description = doc_parts[0].rstrip("\n")
        node_description = format_desc(node_description)

        deprecation_note = Optional()
        doc.add(deprecation_note)
        doc.add(Paragraph(node_description))

        has_see = False
        has_inputs = False
        has_outputs = False
        has_options = False
        see_list = []
        input_list = []
        output_list = []
        option_list = []
        for part in doc_parts:
            # Reference to other logic nodes
            if part.startswith("seeNode "):
                if not has_see:
                    has_see = True
                    doc.add(Paragraph(Bold("See also:")))
                    doc.add(UnorderedList(see_list))

                see_list.append(Italic(make_node_link(part[8:].rstrip())))

            # General references
            elif part.startswith("see "):
                if not has_see:
                    has_see = True
                    doc.add(Paragraph(Bold("See also:")))
                    doc.add(UnorderedList(see_list))

                see_list.append(Italic(part[4:].rstrip()))

        # Add node screenshot
        image_file = IMG_DIR + category.name.lower() + "/" + nodeitem.nodetype + ".jpg"
        doc.add(Image(url=image_file, alt_text=nodeitem.label + " node"))

        for part in doc_parts:
            # Input sockets
            if part.startswith("input "):
                if not has_inputs:
                    has_inputs = True
                    doc.add(Paragraph(Bold("Inputs:")))
                    doc.add(UnorderedList(input_list))

                socket_name, description = part[6:].split(":", 1)
                description = format_desc(description, indented=True)
                input_list.append(f"{InlineCode(socket_name)}: {description}")

            # Output sockets
            elif part.startswith("output "):
                if not has_outputs:
                    has_outputs = True
                    doc.add(Paragraph(Bold("Outputs:")))
                    doc.add(UnorderedList(output_list))

                socket_name, description = part[7:].split(":", 1)
                description = format_desc(description, indented=True)
                output_list.append(f"{InlineCode(socket_name)}: {description}")

            # Other UI options
            elif part.startswith("option "):
                if not has_options:
                    has_options = True
                    doc.add(Paragraph(Bold("Options:")))
                    doc.add(UnorderedList(option_list))

                option_name, description = part[7:].split(":", 1)
                description = format_desc(description, indented=True)
                option_list.append(f"{InlineCode(option_name)}: {description}")

            elif part.startswith("deprecated "):
                alternatives, message = part[11:].split(":", 1)

                message = " ".join(message.split()).replace("\n", "")
                if not message.endswith(".") and not message == "":
                    message += "."

                links = []
                for alternative in alternatives.split(","):
                    if alternative == "":
                        continue
                    links.append(str(make_node_link(alternative)))

                if len(links) > 0:
                    alternatives = f"Please use the following node(s) instead: {', '.join(links)}."
                    message = alternatives + " " + message

                deprecation_note.content = Quote(f"{Bold('DEPRECATED.')} This node is deprecated and will be removed in future versions of Armory. {message}")

        # Link to sources
        node_file_py = "/".join(nodetype.__module__.split(".")[2:]) + ".py"
        node_file_hx = nodetype.bl_idname[2:] + ".hx"  # Discard LN prefix

        pylink = Link(label="Python", url=PY_NODE_DIR + node_file_py)
        hxlink = Link(label="Haxe", url=HX_NODE_DIR + node_file_hx)

        doc.add(Paragraph(f"{Bold('Sources:')} {pylink} | {hxlink}"))


def build_page(section_name: str = ""):
    is_mainpage = section_name == ""

    doc = Document()

    doc.add(Header("Logic Nodes Reference" + ("" if is_mainpage else f": {Italic(section_name.capitalize())} nodes")))

    doc.add(Paragraph(Italic(
        "This reference was generated automatically. Please do not edit the"
        " page directly, instead change the docstrings of the nodes in their"
        f" {Link(label='Python files', url='https://github.com/armory3d/armory/tree/main/blender/arm/logicnode')}"
        f" or the {Link(label='generator script', url='https://github.com/armory3d/armory_tools/blob/main/mkdocs/make_node_reference.py')}"
        f" and {Link(label='open a pull request', url='https://github.com/armory3d/armory/wiki/contribute#creating-a-pull-request')}."
        " Thank you for contributing!")))
    doc.add(Paragraph(Italic(f"This reference was built for {Bold(f'Armory {arm.props.arm_version}')}.")))

    doc.add(HorizontalRule())

    with HeaderSubLevel(doc):

        # Table of contents
        doc.add(Header("Node Categories"))

        category_items: List[Node] = []
        for section, section_categories in arm_nodes.category_items.items():
            # Ignore empty sections ("default" e.g)
            if len(section_categories) > 0:
                section_title = Bold(section.capitalize())
                if section_name == section:
                    # Highlight current page
                    section_title = Italic(section_title)
                category_items.append(section_title)
                url = f"https://github.com/armory3d/armory/wiki/reference_{section}"
                category_items.append(UnorderedList([Link(c.name, url + get_anchor(c.name)) for c in section_categories]))

        doc.add(UnorderedList(category_items))

        # Page content
        if not is_mainpage:
            for category in arm_nodes.category_items[section_name]:
                doc.add(Header(category.name))

                if category.description != "":
                    doc.add(Paragraph(category.description))

                with HeaderSubLevel(doc):
                    # Sort nodes alphabetically and discard section order
                    iterator = itertools.chain(category.get_all_nodes(), category.deprecated_nodes)
                    for nodeitem in sorted(iterator, key=lambda n: n.label):
                        doc.add(Header(nodeitem.label))

                        generate_node_documentation(doc, nodeitem, category)

    filename = "reference.md" if is_mainpage else f"reference_{section_name}.md"
    with open(os.path.join(OUTPUT_DIR, filename), "w") as out_file:
        out_file.write(doc.write())


def run():
    print("Generating documentation...")

    if not os.path.exists(OUTPUT_DIR):
        os.mkdir(OUTPUT_DIR)

    # Main page
    build_page()

    # Section sub-pages
    for section_name in arm_nodes.category_items.keys():
        if section_name == 'default':
            continue
        build_page(section_name)


if __name__ == "__main__":
    run()
