""" 
live_code_pygame.py
Author: Nathan Tibbetts
Date: 15-16 June 2022
License: To be determined, but Open Source, free to use, modify, distribute, etc.
GitHub: 

DESCRIPTION:

    This is an example of how to execute pygame in a separate thread, so that
    control is returned to the interpreter running in the terminal. This gives
    you the ability to change your pygame code on the fly, as you can typically
    do with other code in the terminal, and immediately see the results on the
    screen.
    
    The ability to edit code while the event
    loop is running is like that given by the Processing coding platform, but
    this is not so complex and flexible as that.

    This works by creating a second thread (not a separate process, so that
    memory is shared between them). They run concurrently, meaning that Python
    switches back and forth between the two frequently enough they appear to be
    separate.

    This example includes a basic ThreadedRenderer for pygame, which is really
    the core of the concept. The two additional classes are simply provided to
    serve as examples and test cases.

INSTRUCTIONS:

    It defeats the purpose of this example to try to simply execute it alone, like this:

        python3 live_code_pygame.py

    Instead, running the file from within an interpreter like iPython
    will give you the simultaneous control we're interested in. For example:

        ipython3
        run live_code_pygame.py

    Which defines o and r for you nicely, and leaves you a console to play with.
    Of course, you can just go into iPython and do it yourself:

        ipython3
        import live_code_pygame as lcp
        o = lcp.Orbiter()
        r = lcp.ThreadedRenderer(instances=[o])

    In either case, you may then try things like these examples below (though
    if you did run the code as a script you will still have to import
    live_code_pygame as lcp):

        # Mess with an orbiter o
        o.dist = 30
        o.rot = -.02
        o.radius = 4
        o.color = (200, 0, 255)
        o.center = (20, 78)

        # Make a second orbiter
        m = lcp.Orbiter()
        r.instances.append(m)

        # Replace m's update function to cause it to orbit o
        u = m.update # Save the update function because we want to still call it
        def moon_update(): # Make a new update function
            m.center = (o.rect.x+o.radius, o.rect.y+o.radius)
            u() # Call the old update function too
        m.update = moon_update
        
        # Stop clearing the background with a color
        m.radius = 2 # To better see the effect
        r.background = None
        # Note that the effect isn't perfect BECAUSE we're not using alpha on
        #   our surfaces in pygame, so black corners are being drawn with our
        #   current setup, but that could be easily fixed.

    Note that any live change that is illegal, like an invalid color,
    will cause the thread to panic and crash. Robustness will take effort.
"""

#------------------------------------------------------------------------------#

import threading
import pygame
from math import pi, sin, cos

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)



class ThreadedRenderer(threading.Thread):
    """ A simple class to run Pygame in a separate thread. This allows you to
        edit the code of this object and instances within your game, live,
        and watch the results on the screen immediately.
        
        Note that Pygame only supports one actual game window, though you may
        run multiple of these at once by having separate terminals, with
        separate python interpreters running in each."""

    instantiated = False # Attempt to prevent the user from running multiple at once

    def __init__(self, instances=[], size=(128, 128), fps=30, background=BLACK, event_functions={}):
        """ Instantiate and AUTOMATICALLY start the thread and pygame window.
        
            instances: list of Instance objects on which to call 'draw' and 'update'.
            background: background color tuple like (r, g, b), 0-255 each.
                Use None to cause it not to clear the screen each frame, such
                as for continual drawing.
            event_functions: a dictionary with pygame event types as keys, and
                callback functions as values. These functions will be called
                upon the occurrence of their keyed events in the program loop.
                Each callback function should take the given event object as its
                argument."""

        if ThreadedRenderer.instantiated:
            raise RuntimeError("Only one ThreadedRenderer may run at a time")
        threading.Thread.__init__(self) # Run the Thread parent init
        ThreadedRenderer.instantiated = True # Limit one running at once

        # Set up program structure
        self.instances = instances
        self.fps = fps
        self.background = background
        self.events = event_functions
        self.running = True

        # Set up Pygame
        pygame.init()
        self.screen = pygame.display.set_mode(size)
        self.clock = pygame.time.Clock()

        # Start the thread, which starts the loop
        self.start()

    def _step(self):
        """ Update the program objects, called each frame."""
        for inst in self.instances:
            inst.update()

    def _draw(self):
        """ Redraw the screen, called each frame."""
        if self.background is not None: self.screen.fill(self.background)
        for inst in self.instances:
            inst.draw(self.screen)
        pygame.display.flip()

    def run(self):
        """ The function that is Threaded. DO NOT call this function."""
        try:
            while self.running is True:
                self.clock.tick(self.fps)
                for event in pygame.event.get():
                    if event.type in self.events:
                        self.events[event.type](event)
                    elif event.type == pygame.QUIT: # May be overridden
                        self.running = False
                self._step()
                self._draw()
        except: # Fail gracefully instead of freezing if we have an error
            self.error = "".join(format_exception(*exc_info()))
            print(self.error)
            self.running = False
        # Below will be executed whenever the thread quits gracefully or kill is called
        pygame.quit()
        ThreadedRenderer.instantiated = False
        return self.error

    def kill(self):
        """ Gracefully halt the thread and shutdown Pygame.
            Calling del on a ThreadedRenderer will not do close the window,
            just decrement its reference count, as the Thread is still running.
            
            This leaves behind a stopped thread object. You may still access
            its variables, but since it inherits from threading.Thread,
            start may not be called on it again, and calling run will not start
            a new thread."""
        self.running = False



#------------------------------------------------------------------------------#

class Instance:
    """ A base class from which to build easily editable objects."""

    def __init__(self, x=0, y=0, w=16, h=16):
        """ Derived classes should call super()__init__() in their own init."""
        self.rect = pygame.Rect(x, y, w, h)
        self._rerender = True

    def update(self):
        """ This function will be called once per frame.
            Derived classes should override this."""
        pass

    def render(self):
        """ This function is for rendering a sprite or such the like to
            self.image, which will be drawn each frame.
            Derived classes can override this, but should still set
            self._rerender=False unless you don't need automatic rerendering."""
        self.image = pygame.Surface((self.rect.w, self.rect.h))
        self.image.fill(WHITE)
        self._rerender = False

    def draw(self, surface):
        """ This function defines how the previously rendered object should be
            drawn on the screen.
            It is unlikely that derived classes will need to override this."""
        if self._rerender: self.render()
        surface.blit(self.image, (self.rect.x, self.rect.y))

    def __setattr__(self, name, value):
        """ This function override exists to allow you to change things that
            will need rerendered and still have the change show up automatically.
            It is a quick and dirty solution that causes it to rerender whenever
            the user changes anything.
            This is not needed if the image itself is static.
            Derived classes can override this, but only if you know what you're doing."""
        self.__dict__[name] = value # Must set the attribute
        self.__dict__["_rerender"] = True # Also note the need for an update
        # A possible alternative solution could have a selection of attribute
        #   names which are checked, such as: if name in ["radius", "color"]
        #   then do the second line.



class Orbiter(Instance):
    """ An example of an object built from the Instance base class.
        It simply orbits a point in space."""

    def __init__(self, x=64, y=64, angle=0, dist=48, rot=.1, radius=8, color=WHITE):
        """ Setup this instance."""
        super().__init__( 
            x + dist * cos(angle) - radius,
            y + dist * sin(angle) - radius,
            radius * 2,
            radius * 2,
        ) # Call parent class initializer. Necessary, though the arguments may be optional.
        self.center = (x, y) # Center of orbit, NOT the same x and y as for self.rect
        self.angle = angle # Current theta around orbit, in radians
        self.dist = dist # Distance from center of orbit, in pixels
        self.rot = rot # Angular velocity, in radians per frame
        self.radius = radius # Size of the object, in pixels
        self.color = WHITE # Color of the object, (r, g, b) from 0-255 each

    def update(self):
        """ What to do every step."""
        # No need to call super().__init__() here, as the parent function is empty.
        self.angle += self.rot
        if self.angle > 2*pi:
            self.angle -= 2*pi
        elif self.angle < 0:
            self.angle += 2*pi
        self.rect.x = self.center[0]+self.dist*cos(self.angle)-self.radius
        self.rect.y = self.center[1]+self.dist*sin(self.angle)-self.radius
        self.rect.w = self.radius*2
        self.rect.h = self.radius*2

    def render(self):
        """ How to draw this object."""
        self.image = pygame.Surface((self.radius*2, self.radius*2))
        pygame.draw.circle(self.image, self.color, (self.radius, self.radius), self.radius)
        self._rerender = False



#------------------------------------------------------------------------------#

if __name__ == "__main__":
    """ Script behavior for quickly starting up a thread with an Orbiter, if
        run from inside a python interpreter """
    o = Orbiter()
    r = ThreadedRenderer(instances=[o])


"""
Some additional notes:

    I considered the possibility of making it so you can save the state of your
    renderer. This can be done, but since threads aren't picklable, it
    would require creating a specialized serializer and deserializer, which
    I have not done. The most useful solution would be to have it save what
    you have changed as code, as if you were editing, live, the file controlling
    the renderer. This might be possible, but would be very difficult, and
    would likely require the introspection module and would be a recursive mess.
    My initial, non-functional test of any kind of save feature would look like:

import pickle

def save(obj, filename):
    f = open(filename, 'wb')
    pickle.dump(obj, f)
    print(f"{filename} saved successfully.")

def load(filename):
    f = open(filename, 'rb')
    o = pickle.load(f)
    print(f"{filename} loaded successfully.")
    return o

save(r, "my_session.pkl")
t = load("my_session.pkl")
"""
