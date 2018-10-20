# optimizer-visualization
## overview
This project was created to better understand optimizers used in machine learning. It uses pytorch, matplotlib, numpy and imageio(for saving gifs). The application uses two plots. Left plot shows how value of two parameter function changes during optimiziation dependent on initial values of said parameters. Right plot shows how selected points from left plot move during optimization. This information complements the view from left plot, where movements of a point was not shown, the only thing shown in that case was the value of a function at that point.  
![alt text](https://raw.githubusercontent.com/marcin7Cd/optimizer-visualization/master/overview1.jpg)
## detailed description
### left plot
Left side shows how value of a function f(x,y) changes during minimization process dependent on initial parameter values x_0, y_0. Each pixel(point) represents the initial parameters x_0,y_0 of the function. Changes to the color of a pixel represents changes to the value of the function produced by changing the values of a parameters from their initial conditions(position of a pixel). The information about movement of points is lost. We only can tell if a point moves in a low value area or a hight value area, but the information which low value area it is is lost.
### right plot
The right side is reserved for showing the changes to parameters values directly. You select initial points and then the animation shows how these point travel during optimization. In this view the information about the value of a function is lost.
### points selection
In current version we can select initial points for analysis by selecting a line on the left view.
### animation
For better analysis you can move to next or previous frame. Moving to the next frame at the last frame extends the animation by one frame. So when restarted the animation will stop later. The play button restarts the animation(if you are on last frame). if you change selected initial point, the right view is started first to catch up to the left view. 
### saving
The only supported format is gif. When save button is clicked the animation is started and all subsequent frames will be recorded. Stopping animation causes the recording to stop and saves the results.
### view
There is an option to follow the right curve. IF selected it will constantly change view so as to fill the whole curve. Additionaly If you select the focus point the view will be centered on that point.  
### adjusting
In the main.py you can change manualy parameters: duration - number of frames to show; speed - minimal interval between frames(frame generation may take longer); image_resolution - number of points per line of an image; line_resolution - number of points on the line; optimX - optimizer used; plot_function - two argument function (currently has to work on numpy and torch arrays); bounds - limits of parameters initial values
