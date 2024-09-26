import os
import nuke

def find_logo(logo):
    nukepaths = nuke.pluginPath()
    for path in nukepaths:
        candidate_path = os.path.join(path, logo)
        if os.path.exists(candidate_path):
            return candidate_path
    return False

def set_logo(logo_path):
    n = nuke.thisNode()
    version = n.knob('version').value()
    if logo_path:
        html_path = f"<img src='{logo_path}' width='50'>   "
    else:
        html_path = "<span style='font-size:45px;'>&#x1F47B;</span>"

    html_header = (
        f"<a href='https://www.itaki.com/ghostframeextractor-for-nuke/' style='text-decoration: none;'>"
        
        f"<div><span style='color:#F5F9F1;'>{html_path}</span>"
        f"<font size='6'><span style='color:#F5F9F1;'>GhostFrame</span>"
        f"<span style='color:#FFA100;'>Extractor</span>"
        f"<font size='3'><span style='color:#CFE6B2;'></span>"
        f"<span style='color:#DFD3E7;'>{version}</span></font></font></div></a>"
    )
    n['header'].setValue(html_header)


def check_plugs(plugins):
    all_plugins = nuke.plugins()

    for plugin in all_plugins:
        for key in plugins:
            if key in plugin:
                plugins[key] = True

    nodes_to_delete = ['Twixtor', 'S_Retime', 'BCC3Optical_Flow', 'NNFlowVector']

    for plugin in plugins:
        if plugins[plugin] == True:
            print(f'FOUND {plugin}')
            gizmo.knob(plugin).setValue(True)
        else:
            print(f'not found {plugin}')
            gizmo.knob(plugin).setValue(False)
            
            # Delete nodes for unavailable plugins
            if plugin in nodes_to_delete:
                delete_plugin_nodes(gizmo, plugin)

    return plugins

def delete_plugin_nodes(parent_node, plugin_name):
    for node in parent_node.nodes():
        if plugin_name in node.name():
            nuke.delete(node)
    print(f"Deleted nodes containing '{plugin_name}'")

plugins = {'forward': True, 'backward': True, 'average_motion': True, 'Blend': True, 'Kronos' : True, 'OFlow' : True, 'VectorGenerator' : True, 'SmartVectors': True, 'ABME' : False, 'RAFT' : False, 'NNFlowVector' : False, 'Twixtor' : False, 'BCC3Optical_Flow' : False, 'S_Retime' : False }
# Use a variable to store the current node
gizmo = nuke.thisNode()
installed_plugins = check_plugs(plugins)
            
# List all the options
parent_methods = ['interpolate', 'vector extract']
all_interpolation_methods = ['Blend', 'Kronos', 'OFlow', 'ABME', 'Twixtor','BCC3OpticalFlow', 'S_Retime']
all_vector_generators = ['VectorGenerator', 'SmartVectors', 'ABME', 'RAFT', 'NNFlowVector' ]
all_vector_post_processors = ['forward', 'backward', 'average_motion', 'OFlow', 'Kronos',  'Twixtor']

available_interpolation_methods = [method for method in all_interpolation_methods if method in installed_plugins and installed_plugins[method]]
available_vector_generators = [generator for generator in all_vector_generators if generator in installed_plugins and installed_plugins[generator]]
available_post_processors = [process for process in all_vector_post_processors if process in installed_plugins and installed_plugins[process]]
# Set all the options
gizmo.knob('parent_method').setValues(parent_methods)
gizmo.knob('matte_interpolation').setValues(available_interpolation_methods)
gizmo.knob('hero_interpolation').setValues(available_interpolation_methods)
gizmo.knob('vector_generator').setValues(available_vector_generators)
gizmo.knob('vector_post').setValues(available_post_processors)

logo = 'GhostFrameExtractor.png'
logo_path = find_logo(logo)
set_logo(logo_path)