# Live Code Pygame

## Description

This is an example of how to execute pygame in a separate thread, so that
control is returned to the interpreter running in the terminal. This gives
you the ability to change your pygame code on the fly, as you can typically
do with other code in the terminal, and immediately see the results on the
screen.

The ability to edit code while the event
loop is running is like that given by the [Processing coding platform](https://py.processing.org/), but
this is not so complex and flexible as that.

This works by creating a second thread (not a separate process, so that
memory is shared between them). They run concurrently, meaning that Python
switches back and forth between the two frequently enough they appear to be
separate.

This example includes a basic ThreadedRenderer for pygame, which is really
the core of the concept. The two additional classes are simply provided to
serve as examples and test cases.

## Relevance to the Links project

As of 2022, Pygame is the current API we're using in Python for simpler prototyping.

While working on a GridTree prototype (the background structure within the Filing Tree),
we found it would be handy for added control and debugging of our tree if we could
effect live changes to what was going on on the screen via code, rather than having to
create a UI button for every desirable action. Essentially, we wanted to unblock the
IPython interpreter so we could have terminal control of our GUI - a desirable trait
for the eventual end-product anyway - and threading worked to accomplish this with Pygame in
our prototype system.

The end result was pleasant, and could be useful to other learners, so
we decided to post it here as a side-product of our work. Enjoy.

## Instructions

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
        m.center = (o._rect.x+o.radius, o._rect.y+o.radius)
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

A few further details may be found in the function and class descriptions.
