import os, sys
sys.path.append(os.getcwd())
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
optimX = lambda x: optim.SGD(x ,lr=0.1, momentum=0.999)
plot_function = lambda x,y : ((x)**2*4+y**2*4+(x*2-3)**3/10\
                              +(y-1)**3/10*8+x*y*4+(x**4+y**4)/10+97)/100

class BaseAnimation():
    def __init__(self, number_of_frames):
        self.current_frame = -1
        self.number_of_frames = number_of_frames
        self.storage = []

    def is_last(self):
        return self.current_frame+1 >= self.number_of_frames

    def is_first(self):
        return self.current_frame == -1

    def get_next_frame(self):
        if self.is_last():
            return self.storage[-1]
        self.current_frame+= 1
        if self.current_frame == len(self.storage):
            self.storage.append(self.generate_frame())
        return self.storage[self.current_frame]

    def get_prev_frame(self):
        if self.current_frame>0:
            self.current_frame -= 1
        return self.storage[self.current_frame]

    def rewind(self):
        self.current_frame = -1

    def generate_frame(self):
        return None

class ImageAnimation(BaseAnimation):
    """
        Calculates the data for the next frame.
        The class deals with optimization and generation of data.
    """
    def __init__(self, bounds, resolution, number_of_frames,
                 function=plot_function, optimizer=optimX):
        """
        Args:
        bounds - determinats rectangle bounding the generated area
        resolution - number of points along one axis
        number_of_frames - leght of animation in frames
        """
        super().__init__(number_of_frames)
        #initial points and dimensions definition
        self.x_scale = np.linspace(bounds[0][0], bounds[0][1], resolution)
        self.y_scale = np.linspace(bounds[1][1], bounds[1][0], resolution)
        print([np.min(self.x_scale),np.max(self.x_scale),
               np.min(self.y_scale),np.max(self.y_scale)])
        #self.xy_scale = np.stack(np.meshgrid(self.x_scale, self.y_scale))
        #optimization initial points
        self.par = nn.Parameter(torch.Tensor(np.stack(np.meshgrid(self.x_scale,self.y_scale))))
        self.optimX = optimizer({self.par:1})
        self.plot_function = function
        
    def generate_frame(self):
        """
        generates next frame of animation
        return size N x M
        """
        result = self.plot_function(self.par[0], self.par[1])
        number = result.sum()
        number.backward()
        self.optimX.step()
        self.optimX.zero_grad()
        return result.detach().numpy()

class LineAnimation(BaseAnimation):
    def __init__(self, bounds, resolution, number_of_frames,
                 function=plot_function, optimizer=optimX):
        super().__init__(number_of_frames)
        self.xy_scale = np.stack([np.linspace(bounds[i][0], bounds[i][1],
                                            num = resolution)
                                for i in [0,1]])
        self.par = nn.Parameter(torch.Tensor(self.xy_scale))
        self.optimX = optimizer({self.par:1})
        
        self.plot_function = function
        self.initial_bounds = bounds
    def generate_frame(self):
        """
        generates next animation frame
        returned size: 2 X M
        """
        if self.current_frame == 0:
            print('zer', end='')
            return self.xy_scale
        print('gen', end='')
        result = self.plot_function(self.par[0], self.par[1])
        result = result.sum()
        result.backward()
        self.optimX.step()
        self.optimX.zero_grad()
        return self.par.detach().numpy().copy()
    
    def is_changed(self, bounds):
        return self.initial_bounds != bounds
