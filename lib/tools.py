import os, sys
sys.path.append(os.getcwd())
import matplotlib.pyplot as plt
plt.rcParams['toolbar'] = 'toolmanager'
from matplotlib.backend_tools import ToolBase, ToolToggleBase

class PaintLine(ToolToggleBase):
    '''Show lines with a given gid'''
    default_keymap = 'G'
    description = 'paint a line'
    default_toggled = False
    image = os.path.abspath('./lib/line_tool.png')
    
    def __init__(self, *args, lineDraw, **kwargs):
        self.drawer = lineDraw
        super().__init__(*args, **kwargs)

    def enable(self, *args):
        self.drawer.connect()
        
    def disable(self, *args):
        self.drawer.disconnect()

class Start(ToolBase):
    default_keymap = 'P'
    description = 'start animation'
    image = os.path.abspath('./lib/start.png')
    
    def __init__(self, *args, full_animation, **kwargs):
        self.animation = full_animation
        self.timer = None
        super().__init__(*args, **kwargs)
        
    def trigger(self, *args, **kwargs):
        self.animation.start()

class Stop(ToolBase):
    default_keymap = 'S'
    description = 'stop animation'
    image = os.path.abspath('./lib/stop.png')
    
    def __init__(self, *args, full_animation, **kwargs):
        self.animation = full_animation
        super().__init__(*args, **kwargs)
        
    def trigger(self, *args, **kwargs):
        self.animation.stop()

class Right(ToolBase):
    default_keymap = 'R'
    description = 'next frame'
    image = os.path.abspath('./lib/right.png')
    
    def __init__(self, *args, full_animation, **kwargs):
        self.animation = full_animation
        super().__init__(*args, **kwargs)
        
    def trigger(self, *args, **kwargs):
        if self.animation.image_animation:
            self.animation.step()

class Left(ToolBase):
    default_keymap = 'L'
    description = 'previous frame'
    image = os.path.abspath('./lib/left.png')
    
    def __init__(self, *args, full_animation, **kwargs):
        self.animation = full_animation
        super().__init__(*args, **kwargs)
        
    def trigger(self, *args, **kwargs):
        if self.animation.image_animation:
            self.animation.unstep()

class ZoomOption(ToolToggleBase):
    description = 'zoom to fit curve in view box'
    image = os.path.abspath('./lib/zoom_option.png')
    def __init__(self, *args, full_animation, **kwargs):
        self.animation = full_animation
        super().__init__(*args, **kwargs)

    def enable(self, *args, **kwargs):
        self.animation.zoom = True
            
    def disable(self, *args, **kwargs):
        self.animation.zoom = False
        
class SaveAnimation(ToolBase):
    description = 'save the animation'
    image = os.path.abspath('./lib/save.png')
    
    def __init__(self, *args, full_animation, **kwargs):
        self.animation = full_animation
        super().__init__(*args, **kwargs)

    def trigger(self, *args, **kwargs):
        self.animation.start(save=True)
            

