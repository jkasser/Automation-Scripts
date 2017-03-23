from Tkinter import *

# create the root window
root = Tk()
root.title("Simple Gui")
root.geometry("200x100")

# create a frame
app = Frame(root)
app.grid()

# create a label in the frame
lbl = Label(app, text = "I'm a label!")
lbl.grid()

# create a button
bttn1 = Button(app, text = "I do nothing!")
bttn1.grid()

# Another way
bttn2 = Button(app)
bttn2.grid()

bttn2.configure(text = "Me too!")

# A third way
bttn3 = Button(app)
bttn3.grid()

bttn3["text"] = "Same here!"


# kick off the window's event loop
root.mainloop()

