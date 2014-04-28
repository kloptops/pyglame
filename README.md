pyglame
=======

pyglame provides an object-orientated programming interface that closely follows
pyglet. It runs on top of pygame, giving you access to pyglets excellent
app/window/clock/resource framework.


It is pronounced pig-lame, it is a combination of pyglet and pygame.


I cannot stress this enough that it does not support OpenGL at all at the
moment, and I have little motivation to do so. Unless someone can give me a
compelling argument, use pyglet if you really need opengl?


What works?
===========

* pyglame.window works fairly well, some events maybe shaky, definitely needs
  more testing.
* pyglame.surface stuff should work in theory but really needs fleshing out.
* pyglame.app works ok, seems to hold a steady fps, and seems to be sending out
  events and stuff like its supposed to.
* pyglame.clock same deal as pyglame.app.
* pyglame.font doesnt work at all, since it needed the surface stuff written.
