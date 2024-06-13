import nuke
import os


nuke.menu('Nodes').addCommand('Image/GhostFrameExtractor', 'nuke.createNode("GhostFrameExtractor")', icon='GhostFrameExtractor.png')
nuke.menu('Nodes').addCommand('Image/GhostFrameFootageCreator', 'nuke.createNode("GhostFrameFootageCreator")', icon='GhostFrameFootageCreator.png')
