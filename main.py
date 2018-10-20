import os, sys
sys.path.append(os.getcwd())
import argparse
import numpy as np
import torch
import torch.optim as optim
from matplotlib.colors import LogNorm
import matplotlib.pyplot as plt
plt.rcParams['toolbar'] = 'toolmanager'
import imageio
import lib.tools as tools
import lib.main_logic as logic

##ADJUSTABLE VARIABLES


optimX = lambda x: optim.Adam(x ,lr=0.1, betas=(0.9,0.99))
#optimX = lambda x: optim.Adadelta(x ,lr=10.0, rho=0.9)
#optimX = lambda x: optim.Adagrad(x ,lr=0.4)
#optimX = lambda x: optim.Adamax(x ,lr=0.1,betas=(0.9, 0.99))
#optimX = lambda x: optim.RMSprop(x ,lr=0.02, momentum=0.5)
#optimX = lambda x: optim.SGD(x ,lr=0.1, momentum=0.9)
plot_function = lambda x,y : ((x)**2*4+y**2*4+(x*2-3)**3/10\
                              +(y-1)**3/10*8+x*y*4+(x**4+y**4)/10+97)/100
#plot_function = lambda x,y : (2*y**2)/400
bounds = ((-15,10),(-15,10))

######################33

parser = argparse.ArgumentParser(description='PyTorch MNIST Example')
parser.add_argument('--duration', type=int, default=50, metavar='N',
                    help='maximal number of frames in animation (default: 50)')
parser.add_argument('--image-resolution', type=int, default=500, metavar='N',
                    help='number of points per line (default: 500)')
parser.add_argument('--line-resolution', type=int, default=2000, metavar='N',
                    help='number of points per line (default: 2000)')
parser.add_argument('--speed', type=int, default=100, metavar='N',
                    help='minimal interval between frames (default: 100)')

args = parser.parse_args()
image_resolution = args.image_resolution
line_resolution = args.line_resolution
duration = args.duration*2
speed=args.speed

x_scale = np.linspace(bounds[0][0], bounds[0][1], image_resolution)
y_scale = np.linspace(bounds[1][0], bounds[1][1], image_resolution)
xy_scale = np.stack(np.meshgrid(x_scale, y_scale))
print(xy_scale[:,0,:])
print([np.min(x_scale),np.max(x_scale),
                                         np.min(y_scale),np.max(y_scale)])
fig = plt.figure(figsize=(10,5))
ax1 = fig.add_subplot(121)
ln = ax1.imshow(plot_function(xy_scale[0],np.flip(xy_scale[1],0)),
                                 extent=[np.min(x_scale),np.max(x_scale),
                                         np.min(y_scale),np.max(y_scale)],
                                  norm = LogNorm(vmin=0.001,vmax=1, clip=False),
                                  animated = True)

#plt.autoscale(False)
line_drawer = logic.DrawableLine(ax1)
ax2 = fig.add_subplot(122)
plt.grid(True)
plt.autoscale(False)

anim = logic.FullAnimation(line_drawer, ax2, ax1, ln,
                           duration=duration,
                           image_bounds=bounds,
                           image_resolution=image_resolution,
                           line_resolution=line_resolution*4,
                           function=plot_function,
                           optimizer=optimX,
                           speed=speed
                           )
fig.canvas.manager.toolmanager.add_tool('draw_line', tools.PaintLine,
                                        lineDraw = line_drawer)
fig.canvas.manager.toolmanager.add_tool('start', tools.Start,
                                        full_animation=anim)
fig.canvas.manager.toolmanager.add_tool('stop', tools.Stop,
                                        full_animation=anim)
fig.canvas.manager.toolmanager.add_tool('right', tools.Right,
                                        full_animation=anim)
fig.canvas.manager.toolmanager.add_tool('left', tools.Left,
                                        full_animation=anim)
fig.canvas.manager.toolmanager.add_tool('zoom_option', tools.ZoomOption,
                                        full_animation=anim)
fig.canvas.manager.toolmanager.add_tool('save_anim', tools.SaveAnimation,
                                        full_animation=anim)
fig.canvas.manager.toolmanager.add_tool('fix_point', tools.FixedPoint,
                                        full_animation=anim)

#ax2 = line_drawer.current_line.get_data()

fig.canvas.manager.toolbar.add_tool('left', 'navigation')
fig.canvas.manager.toolbar.add_tool('right', 'navigation')
fig.canvas.manager.toolbar.add_tool('stop', 'navigation')
fig.canvas.manager.toolbar.add_tool('start', 'navigation')
fig.canvas.manager.toolbar.add_tool('draw_line', 'navigation')
fig.canvas.manager.toolbar.add_tool('zoom_option', 'framing')
fig.canvas.manager.toolbar.add_tool('save_anim', 'io')
fig.canvas.manager.toolbar.add_tool('fix_point', 'framing')
plt.show()


