# GhostFrameExtractor for Nuke

This repository contains 2 gizmos, GhostFrameExtractor and GhostFrameFootageCreator. 

*GhostFrameExtractor :* This is the core tool and what you would use to seperate ghost frame footage that was shot on a production volume. It splits the footage in HERO frames (those which will be seen in the edit) and MATTE frames. The tool has many different methods for creating new MATTE frames that match perfectly to the HERO frames. 

*GhostFrameFootageCreator :* is a simple tool for creating ghost frame footage to play and test with. Since undoubtably clients and production companies may want to see tests before commiting to shooting this way. 

Also contained in this repository are some Nuke scripts showing simple examples as well as a bunch footage that was shot ghost frame as well as generated test footage. 

The gizmos can be installed using the script in the gizmo directly, just put the GhostFrameGizmos folder in your .nuke directory and add 
'''
nuke.pluginAddPath( 'GhostFrameGizmos' )
'''
to your menu.py file. 


But the better way to install them would be through a gizmo manager like [NukeShared](https://maxvanleeuwen.com/project/nukeshared/) and just putting them and the icons in the ./Repository/Nodes/Image directory.

For more detailed information, visit our [GhostFrameExtractor webpage](https://www.itaki.com/ghostframeextractor-for-nuke/).
