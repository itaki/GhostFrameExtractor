import nuke

testing = False

# Helper function to get a node
def get_node(name):
    node = nuke.toNode(name)
    if node is None and testing:
        print(f"Node '{name}' not found.")
    return node

# At the beginning of the file, add this function:
def node_exists(node_name):
    return nuke.exists(node_name)

# Helper function to set knob values
def set_knob_value(node_name, knob_values):
    if not node_exists(node_name):
        if testing:
            print(f"Node '{node_name}' not found. Skipping knob value setting.")
        return
    node = nuke.toNode(node_name)
    if node:
        for knob_name, knob_value in knob_values.items():
            knob = node.knob(knob_name)
            if knob:
                if isinstance(knob_value, list):
                    if knob.isAnimated():
                        knob.clearAnimated()
                        knob.setAnimated()
                        for value, frame in knob_value:
                            knob.setValueAt(value, frame)
                    else:
                        knob.setValue(knob_value[0][1])
                else:
                    knob.setValue(knob_value)

def get_frame_range():
    input_node = gizmo.input(0)
    if input_node is not None:
        first_frame = input_node.firstFrame()
        last_frame = input_node.lastFrame()
        set_knob_value('InputFrameRange', {'first_frame': first_frame, 'last_frame': last_frame})
        set_knob_value('MatteFrameHold', {'firstFrame': first_frame + 1})

        matte_frame = 1 if add_matte_frame() else 0
        last_frame += matte_frame
        set_knob_value('AppendMatteFrame', {'firstFrame': first_frame, 'lastFrame': last_frame})
        set_knob_value('EndFrameHold', {'firstFrame': last_frame - 1})
        last_frame += add_end_frame(first_frame, last_frame)
        set_knob_value('AppendEndFrame', {'firstFrame': first_frame, 'lastFrame': last_frame})
        set_knob_value('OutputFrameRange', {'first_frame': first_frame, 'last_frame': last_frame})
        
        return [first_frame, last_frame]
    return [1, 100]

def add_matte_frame():
    add_frame_switch = get_node('add_frame_switch')
    if gizmo['add_frame'].value():
        add_frame_switch['which'].setValue(1)
        return True
    else:
        add_frame_switch['which'].setValue(0)
        return False

def add_end_frame(first_frame, last_frame):
    total_frames = last_frame - first_frame
    add_end_frame_switch = get_node('add_end_frame_switch')
    if total_frames % 2 != 0:
        add_end_frame_switch['which'].setValue(1)
        return 1
    else:
        add_end_frame_switch['which'].setValue(0)
        return 0

def propogate_frame_range(frame_range):
    f, l = frame_range
    new_last_frame = ((l - f) * 2) + f
    hero_last_frame = (l - f - 1) // 2 + f
    if testing:
        print(f'Refreshing frame range, first frame {f}, last frame {l}')

    nodes = {
        'PlateRetime': {'input.first': f, 'input.last': l, 'output.first': f, 'output.last': new_last_frame},
        'OFlowPlateBlend': {'input.first': f, 'input.last': l, 'timingFrame2': [(f, f), (l, new_last_frame)]},
        'KronosPlate': {'input.first': f, 'input.last': l, 'timingFrame2': [(f, f), (l, new_last_frame)]},
        'OFlowPlate': {'input.first': f, 'input.last': l, 'timingFrame2': [(f, f), (l, new_last_frame)]},
        'TwixtorPlate': {'StartFrame': f, 'LastFrame': l, 'Frame': [(f, f), (l, new_last_frame)]},
        'BCC3Optical_Flow1': {'start_offset_frame': f},
        'S_Retime1': {'start_frame': f},
        'RetimeInterpolated': {'input.first': f + 1, 'input.last': new_last_frame, 'output.first': f, 'output.last': l},
        'HeroRetime': {'input.first': f + 1, 'input.last': l, 'output.first': f, 'output.last': hero_last_frame},
        'DoublePlateFrames': {'input.first': f, 'input.last': new_last_frame, 'timingFrame2': [(f, f), ((new_last_frame * 2) - 1, new_last_frame)]},
        'OFlowBlend': {'input.first': f, 'input.last': l - 1, 'timingFrame2': [(f, f), (l, new_last_frame)]},
        'KronosHero': {'input.first': f, 'input.last': l - 1, 'timingFrame2': [(f, f), (l, new_last_frame)]},
        'OFlowHero': {'input.first': f, 'input.last': l - 1, 'timingFrame2': [(f, f), (l, new_last_frame)]},
        'TwixtorHero': {'StartFrame': f, 'LastFrame': l, 'Frame': [(f, f), (l, new_last_frame)]},
        'OutputFrameRange2': {'first_frame': f, 'last_frame': hero_last_frame},
        'RetimeExtracted': {'input.first': f, 'input.last': new_last_frame, 'output.first': f, 'output.last': l}
    }

    for node_name, knob_values in nodes.items():
        set_knob_value(node_name, knob_values)

def output_type(output):
    if output == 'hero plate':
        set_knob_value('output_switch', {'which': 1})
        gizmo['tile_color'].setValue(131583)
        gizmo['matte_extraction_group'].setVisible(False)

    else:
        set_knob_value('output_switch', {'which': 0})
        gizmo['tile_color'].setValue(131071)
        gizmo['matte_extraction_group'].setVisible(True)

def select_parent_method(parent_method):
    method_index = {'interpolate': 0, 'vector extract': 1, 'average': 2}.get(parent_method, 0)
    set_knob_value('parent_method_switch', {'which': method_index})
    gizmo['interpolation_group'].setVisible(parent_method == 'interpolate')
    gizmo['extract_group'].setVisible(parent_method in ['vector extract', 'average'])

def select_matte_interpolation_method(interpolation_method):
    method_index = {'Blend': 0, 'Kronos': 1, 'OFlow': 2, 'ABME': 3, 'Twixtor': 4, 'BCC3Optical_Flow': 5, 'S_Retime': 6}.get(interpolation_method, 0)
    set_knob_value('interpolated_switch', {'which': method_index})
    gizmo['giblend'].setVisible(interpolation_method == 'Blend')
    gizmo['gikronos'].setVisible(interpolation_method == 'Kronos')
    gizmo['gioflow'].setVisible(interpolation_method == 'OFlow')
    gizmo['giabme'].setVisible(interpolation_method == 'ABME')
    gizmo['gitwixtor'].setVisible(interpolation_method == 'Twixtor')
    gizmo['giboris'].setVisible(interpolation_method == 'BCC3Optical_Flow')
    gizmo['gisapphire'].setVisible(interpolation_method == 'S_Retime')
    set_knob_value('ABME_Retime_interpolate', {'disable': interpolation_method != 'ABME'})
    
    if node_exists('TwixtorPlate'):
        set_knob_value('TwixtorPlate', {'disable': interpolation_method != 'Twixtor'})
    if node_exists('BCC3Optical_Flow1'):
        set_knob_value('BCC3Optical_Flow1', {'disable': interpolation_method != 'BCC3Optical_Flow'})
    if node_exists('S_Retime1'):
        set_knob_value('S_Retime1', {'disable': interpolation_method != 'S_Retime'})

    interpolated_switch = nuke.toNode('interpolated_switch')
    time_offset = get_node('TimeOffset2')

    if interpolated_switch and time_offset:
        # Disconnect TimeOffset2 from interpolated_switch
        for i in range(interpolated_switch.inputs()):
            if interpolated_switch.input(i) == time_offset:
                interpolated_switch.setInput(i, None)
                break

    # Reconnect TimeOffset2 to input 5 of interpolated_switch if selected
    if method_index == 5 and interpolated_switch and time_offset:
        interpolated_switch.setInput(5, time_offset)
    
        

def select_hero_interpolation_method(interpolation_method):
    method_index = {'Blend': 0, 'Kronos': 1, 'OFlow': 2, 'ABME': 3, 'Twixtor': 4, 'BCC3Optical_Flow': 5, 'S_Retime': 6}.get(interpolation_method, 0)
    set_knob_value('hero_interpolation_swtich', {'which': method_index})
    gizmo['vgblend'].setVisible(interpolation_method == 'Blend')
    gizmo['vgkronos'].setVisible(interpolation_method == 'Kronos')
    gizmo['vgoflow'].setVisible(interpolation_method == 'OFlow')
    gizmo['vgabme'].setVisible(interpolation_method == 'ABME')
    gizmo['vgtwixtor'].setVisible(interpolation_method == 'Twixtor')
    gizmo['vgboris'].setVisible(interpolation_method == 'BCC3Optical_Flow')
    gizmo['vgsapphire'].setVisible(interpolation_method == 'S_Retime')
    
    if node_exists('ABME_Retime3'):
        set_knob_value('ABME_Retime3', {'disable': interpolation_method != 'ABME'})
    if node_exists('TwixtorHero'):
        set_knob_value('TwixtorHero', {'disable': interpolation_method != 'Twixtor'})
    if node_exists('BCC3Optical_Flow2'):
        set_knob_value('BCC3Optical_Flow2', {'disable': interpolation_method != 'BCC3Optical_Flow'})
    if node_exists('S_Retime2'):
        set_knob_value('S_Retime2', {'disable': interpolation_method != 'S_Retime'})
    
    interpolated_switch = nuke.toNode('hero_interpolation_swtich')
    time_offset = get_node('TimeOffset4')
    
    if interpolated_switch and time_offset:
        # Disconnect TimeOffset4 from interpolated_switch
        for i in range(interpolated_switch.inputs()):
            if interpolated_switch.input(i) == time_offset:
                interpolated_switch.setInput(i, None)
                break

    # Reconnect TimeOffset4 to input 5 of interpolated_switch if selected
    if method_index == 5 and interpolated_switch and time_offset:
        interpolated_switch.setInput(5, time_offset)

def select_hero_vector_generator(vector_generator):
    method_index = {'VectorGenerator': 0, 'SmartVectors': 1, 'ABME': 2, 'RAFT': 3, 'NNFlowVector': 4}.get(vector_generator, 0)
    set_knob_value('vector_switch', {'which': method_index})
    gizmo['vectorgenerator'].setVisible(vector_generator == 'VectorGenerator')
    gizmo['smartvector'].setVisible(vector_generator == 'SmartVectors')
    gizmo['abme'].setVisible(vector_generator == 'ABME')
    gizmo['raft'].setVisible(vector_generator == 'RAFT')
    gizmo['nnflowvector'].setVisible(vector_generator == 'NNFlowVector')
    
    if node_exists('ABME_SV1'):
        set_knob_value('ABME_SV1', {'disable': vector_generator != 'ABME'})
    if node_exists('RAFT1'):
        set_knob_value('RAFT1', {'disable': vector_generator != 'RAFT'})
    if node_exists('NNFlowVector1'):
        set_knob_value('NNFlowVector1', {'disable': vector_generator != 'NNFlowVector'})

def set_uv_channels(vector_post_processor):
    method_index = {'forward': 0, 'backward': 1, 'average_motion': 2, 'OFlow': 3, 'Kronos': 4, 'Twixtor': 5}.get(vector_post_processor, 0)
    set_knob_value('SwitchMotionType', {'which': method_index})
    gizmo['vpost_oflow'].setVisible(vector_post_processor == 'OFlow')
    gizmo['vpost_kronos'].setVisible(vector_post_processor == 'Kronos')
    
    # Check if the Twixtor node exists before trying to set its visibility
    if node_exists('vpost_twixtor'):
        gizmo['vpost_twixtor'].setVisible(vector_post_processor == 'Twixtor')
    elif vector_post_processor == 'Twixtor':
        print("Warning: Twixtor node 'vpost_twixtor' not found. Skipping visibility setting.")

    # If Twixtor is selected but not available, you might want to fall back to a default option
    if vector_post_processor == 'Twixtor' and not node_exists('vpost_twixtor'):
        print("Twixtor not available. Falling back to forward motion.")
        set_knob_value('SwitchMotionType', {'which': 0})  # Set to forward motion

def set_distortion_method(distortion_method):
    method_index = 1 if distortion_method == 'IDistort' else 0
    set_knob_value('SwitchBackward', {'which': method_index})
    set_knob_value('SwitchForward', {'which': method_index})

def label_setter():
    output_type = gizmo['output_type'].value()
    if output_type == 'hero plate':
        label = 'HERO'
    else:
        parent_method = gizmo['parent_method'].value()
        if parent_method == 'interpolate':
            label = gizmo['matte_interpolation'].value()
        else:
            label = f"{gizmo['hero_interpolation'].value()}\n{gizmo['vector_generator'].value()}\n{gizmo['distortion_method'].value()}\n{gizmo['vector_post'].value()}"
    gizmo['label'].setValue(label)
    
def create_shuffle():
    # Get the root node
    root = nuke.root()
    
    # Deselect all nodes to ensure the new node is correctly connected to the gizmo
    for node in nuke.allNodes():
        node['selected'].setValue(False)
    
    # Create a new Shuffle2 node in the root context
    with root:
        shuffle_node = nuke.createNode('Shuffle2')
    
    # Set the properties to shuffle the 'matte' layer into the RGB channels
    shuffle_node['in1'].setValue('matte')
    shuffle_node['in2'].setValue('none')


    # Set the mappings
    mappings = [
        (0, 'matte.red', 'rgba.red'),
        (0, 'matte.green', 'rgba.green'),
        (0, 'matte.blue', 'rgba.blue'),
        (-1, 'white', 'rgba.alpha')  # Use 'white' to map matte.alpha to 1
    ]
    shuffle_node['mappings'].setValue(mappings)
    
    # Enable the postage stamp for easier identification
    shuffle_node['postage_stamp'].setValue(True)
    
    # Set the label for easier identification in the node graph
    shuffle_node['label'].setValue('Matte to RGB')
    
    # Position the node below the gizmo for better visibility
    shuffle_node.setXYpos(gizmo.xpos(), gizmo.ypos() + 100)
    
    # Connect the shuffle node to the gizmo's output
    shuffle_node.setInput(0, gizmo)

def twixfix(value):
    for node in (n for n in gizmo.nodes() if n.Class() == 'Switch' and 'MSwitch' in n['name'].value()):
        nuke.toNode(node['name'].value())['which'].setValue(value)

                

def toggle_text_overlays(overlay):
    gizmo['font'].setVisible(overlay)
    gizmo['font_scale'].setVisible(overlay)
    text_nodes = [node for node in nuke.allNodes() if node.Class() == 'Text2']
    for node in text_nodes:
        node['disable'].setValue(not overlay)

def font_selector():
    font_family, font_style = gizmo.knob('font').getValue()
    text_nodes = [node for node in nuke.allNodes() if node.Class() == 'Text2']
    for node in text_nodes:
        try:
            node['font'].setValue(font_family, font_style)
        except:
            pass


def set_font_scale(scale):
    text_nodes = [node for node in nuke.allNodes() if node.Class() == 'Text2']
    for node in text_nodes:
        node['global_font_scale'].setValue(scale)

# Use a variable to store the current node
gizmo = nuke.thisNode()
k = nuke.thisKnob()  # the knob that activated knobChanged
frame_range_changing_knobs = ['inputChange', 'add_frame', 'output_type', 'refresh']

# Turns on knobs when testing
gizmo['print_all_knobs'].setVisible(testing)

# Define a mapping of knob names to functions
knob_function_map = {
    'text_overlays': lambda: toggle_text_overlays(k.value()),
    'font': lambda: font_selector(),
    'font_scale': lambda: set_font_scale(k.value()),
    'twixfix': lambda: twixfix(k.value()),
    'output_type': lambda: (output_type(k.value()), label_setter()),
    'parent_method': lambda: (select_parent_method(k.value()), label_setter()),
    'create_shuffle': lambda: (create_shuffle()),
    'matte_interpolation': lambda: (select_matte_interpolation_method(k.value()), label_setter()),
    'hero_interpolation': lambda: (select_hero_interpolation_method(k.value()), label_setter()),
    'vector_generator': lambda: (select_hero_vector_generator(k.value()), label_setter()),
    'distortion_method': lambda: (set_distortion_method(k.value()), label_setter()),
    'vector_post': lambda: (set_uv_channels(k.value()), label_setter()),
    'difference_viewer': lambda: set_knob_value('diff_switch', {'which': int(k.value())})
}

# Only take action if the particular knob was changed
if k.name() in frame_range_changing_knobs:
    frame_range = get_frame_range()
    propogate_frame_range(frame_range)
if k.name() in knob_function_map:
    knob_function_map[k.name()]()
