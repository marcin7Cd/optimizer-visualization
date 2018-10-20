import os, sys
sys.path.append(os.getcwd())
import torch
import torch.optim as optim
import numpy as np
from matplotlib.colors import LogNorm
import matplotlib.pyplot as plt
plt.rcParams['toolbar'] = 'toolmanager'
from matplotlib.backend_tools import ToolBase, ToolToggleBase
import imageio
import lib.animation_generation as anim_gen
RESOLUTION=100
x_scale = np.linspace(-15, 10, RESOLUTION)
y_scale = np.linspace(-15, 10, RESOLUTION)
xy_scale = np.stack(np.meshgrid(x_scale, y_scale))
optimX = lambda x: optim.SGD(x ,lr=0.1, momentum=0.999)
plot_function = lambda x,y : ((x)**2*4+y**2*4+(x*2-3)**3/10\
                              +(y-1)**3/10*8+x*y*4+(x**4+y**4)/10+97)/100
##############################

class DrawableLine:
    def __init__(self, ax):
        self.axes = ax
        self.current_line = None
        self.start_point = None
        self.line_was_drawn = False
        
    def connect(self):
        'connect to all the events we need'
        self.cidpress = self.axes.figure.canvas.mpl_connect(
            'button_press_event', self.on_press)
        self.cidrelease = self.axes.figure.canvas.mpl_connect(
            'button_release_event', self.on_release)
        self.cidmotion = self.axes.figure.canvas.mpl_connect(
            'motion_notify_event', self.on_motion)

    def on_press(self, event):
        'on button press we will see if the mouse is over us and store some data'
        if event.inaxes != self.axes: return
        print('press')
        self.start_point = event.xdata, event.ydata
        if not self.line_was_drawn:
                self.current_line = self.axes.plot([event.xdata, event.xdata],
                                                   [event.ydata, event.ydata],
                                                   'k-',c=(0,0,0,0.3),lw=2)[0]
                self.line_was_drawn = True
        else:
                self.current_line.set_data([event.xdata, event.xdata],
                                              [event.ydata, event.ydata])
        
        print(self.current_line)

    def on_motion(self, event):
        'on motion we will move the rect if the mouse is over us'
        if not self.start_point: return
        xpress, ypress = self.start_point
        print(self.start_point, event.xdata, event.ydata)
        self.current_line.set_data([xpress, event.xdata],
                                   [ypress, event.ydata])
        self.axes.figure.canvas.draw()


    def on_release(self, event):
        'on release we reset the press data'
        print('release')
        
        self.press = None
        self.start_point = None
        
        self.axes.figure.canvas.draw()

    def disconnect(self):
        'disconnect all the stored connection ids'
        self.axes.figure.canvas.mpl_disconnect(self.cidpress)
        self.axes.figure.canvas.mpl_disconnect(self.cidrelease)
        self.axes.figure.canvas.mpl_disconnect(self.cidmotion)

class SelectablePoint:
    def __init__(self, ax):
        self.axes = ax
        self.current_point = None
        self.point = None
        self.awake = False
        self.point_was_drawn = False
        self.connect()
        
    def connect(self):
        'connect to all the events we need'
        self.cidpress = self.axes.figure.canvas.mpl_connect(
            'button_press_event', self.on_press)

    def on_press(self, event):
        'on button press we will see if the mouse is over us and store some data'
        if self.awake:
            self.awake = False
            if event.inaxes != self.axes:
                self.current_point = None
                if self.point_was_drawn:
                    self.point.set_data([None],
                                        [None])
                    self.axes.figure.canvas.draw()
            
                return
            
            self.current_point = event.xdata, event.ydata

            if not self.point_was_drawn:
                self.point = self.axes.plot([self.current_point[0]],
                                            [self.current_point[1]],
                                            'ro',c=(0,0,0,0.3),lw=2)[0]
                self.point_was_drawn = True
            else:
                self.point.set_data([self.current_point[0]],
                                    [self.current_point[1]])
            print('Printed', self.current_point)
            self.axes.figure.canvas.draw()
            

    def disconnect(self):
        'disconnect all the stored connection ids'
        self.axes.figure.canvas.mpl_disconnect(self.cidpress)

    def activate(self):
        self.awake = True


class AnimationSave():
    def __init__(self):
        self.saving = False
        self.storage = []

    def add_frame(self, image):
        self.storage.append(image)
        self.saving = True
        print('+', end='')


    def save(self):
        print("saving")
        if self.saving:
            imageio.mimsave('movie.gif',self.storage)

    def clear(self):
        self.storage = []
        self.saving = False

class FullAnimation():
    def __init__(self, line_draw, ax0, ax1, img,
                 duration=20,
                 image_bounds=((10,-15),(10,-15)),
                 image_resolution=500,
                 line_resolution=500,
                 function=plot_function,
                 optimizer=optimX,
                 speed=100
                 ):
        self.right_ax = ax0
        self.left_ax = ax1

        self.point = None
        self.sheet = img

        self.center = (0.0, 0.0)
        self.running_average= 0

        #timer base variables
        self.timer = None
        self.callback_id = None
        
        self.zoom = False
        
        self.image_animation = None
        self.line_animation = None
        self.line_draw = line_draw
        self.fixed_point = SelectablePoint(self.right_ax)
        self.saver = AnimationSave()

        self.image_bounds = image_bounds
        self.image_resolution = image_resolution
        self.line_resolution = line_resolution
        self.function = function
        self.optimizer = optimizer
        self.speed = speed
        self.duration = duration
        
        
        
    def draw_right(self, image, first_time=False):
        print(']', end='')
        if not self.point:
            self.point = self.right_ax.scatter(image[:, 0], image[:, 1], s=0.5,
                                               c = np.linspace(0, 1, num=len(image[:,0])),
                                               cmap='gist_rainbow')
        else:
            self.point.set_offsets(image)

        if self.zoom :
            if not self.fixed_point.current_point:
                wh = [0, 0]
                for i in range(2):
                    wh[i] = image[:,i].max() - image[:,i].min() 
                max_wh = np.max(wh)

                self.right_ax.set_xlim(image[:,0].min()+(wh[0]-max_wh)/2,
                                       image[:,0].max()-(wh[0]-max_wh)/2)
                self.right_ax.set_ylim(image[:,1].min()+(wh[1]-max_wh)/2,
                                       image[:,1].max()-(wh[1]-max_wh)/2)
            else:
                center = self.fixed_point.current_point
                k = 1.1*np.max([-(image[:,1].min()-center[1]),
                            (image[:,1].max()-center[1]),
                            -(image[:,0].min()-center[0]),
                            (image[:,0].max()-center[0]),
                            ])
                self.running_average = 0.5*self.running_average + 0.5*k 

                self.right_ax.set_ylim( center[1]-self.running_average,
                             center[1]+self.running_average)
                self.right_ax.set_xlim( center[0]-self.running_average,
                                center[0]+self.running_average)
        
        self.right_ax.figure.canvas.draw()

    def draw_left(self, image):
        print('[', end='')
        self.sheet.set_data(image)
        self.left_ax.figure.canvas.draw()

    def populate_left(self, bounds, frame_num, resolution=500):
        self.image_animation = anim_gen.ImageAnimation( bounds=bounds,
                                               resolution=resolution,
                                               number_of_frames=frame_num,
                                               function=self.function,
                                               optimizer=self.optimizer)

    def populate_right(self, bounds, frame_num, resolution=500):
        self.line_animation = anim_gen.LineAnimation( bounds=bounds,
                                             resolution=resolution,
                                             number_of_frames=frame_num,
                                             function=self.function,
                                             optimizer=self.optimizer)
        
       
        
    def start(self,save=False):
        #right part
        if self.line_draw.line_was_drawn:
            points = self.line_draw.current_line.get_data()
            if not self.line_animation\
               or self.line_animation.is_changed(points):
                self.populate_right(points, self.duration,
                                    self.line_resolution)
            else:
                if self.image_animation.is_last():
                    self.line_animation.rewind()
        #left part
        if not self.image_animation:
            self.populate_left(self.image_bounds, self.duration,
                               self.image_resolution)
        else:
            if self.image_animation.is_last():
                self.image_animation.rewind()
        
        self.step(first_time=True)
        ##seting up timer to draw frames
        if self.timer:
            self.stop()
            self.timer.remove_callback(self.step)
            self.timer.add_callback(self.step, save)
            self.timer.start(interval=self.speed)
        else:
            self.timer = self.right_ax.figure.canvas.new_timer(interval=self.speed)
            self.callback_id = self.timer.add_callback(self.step, save)
            self.timer.start()

    def stop(self, save=False):
        if self.timer:
            self.timer.stop()
            self.saver.save()
            self.saver.clear()
  
    
    def step(self, save=False, first_time=False, ignore_end=False):
        """
        changes displayed data to data from next frame.
        both sides are animated until they reach the last frame, then timer is stopped
        if step of animation form left and right are different the
        left side is animated only when number of frames on both graphs is equal
        right side is animated only if the line on the left graph was (re)drawn
        """
        print('*', end='')
        ##right side animation
        if self.line_draw.current_line:
            if self.line_animation.is_last():
                if ignore_end:
                    self.line_animation.number_of_frames+=1
                    self.duration+=1
                    print('1')
                else:
                    self.stop(save)
                    return
            right_image = self.line_animation.get_next_frame().transpose(1, 0)
            self.draw_right(right_image,first_time)
            
        ##left_side_animatiob
        if not self.line_animation\
        or self.line_animation.current_frame-1 >= \
        self.image_animation.current_frame:#-1 because we've already taken one frame
            if self.image_animation.is_last():
                if ignore_end:
                    self.image_animation.number_of_frames+=1
                    self.duration+=1
                    print('2')
                else:
                    self.stop(save)
                    return
            left_image = self.image_animation.get_next_frame()
            self.draw_left(left_image)
        if save:
            print('S')
            width, height = self.left_ax.figure.get_size_inches()\
                            *self.left_ax.figure.get_dpi()
            self.saver.add_frame(np.fromstring(self.right_ax.figure.canvas.tostring_rgb(),
                                               dtype='uint8').reshape(int(height),int(width), 3))
        
        
    def unstep(self):
        'used to move to previous frame'
        print('*', end='')
        ##right side animation
        if self.line_draw.current_line:
            if self.line_animation.is_first():
                self.stop()
                return
            right_image = self.line_animation.get_prev_frame().transpose(1, 0)
            self.draw_right(right_image)
            print('r', end='')
            
        ##left_side_animatiob
        if not self.line_animation\
        or self.line_animation.current_frame+1 == \
        self.image_animation.current_frame:#+1 because we've already taken one frame
            if self.image_animation.is_first():
                self.stop()
                return
            print('l', end='')
            left_image = self.image_animation.get_prev_frame()
            self.draw_left(left_image)
        
        
