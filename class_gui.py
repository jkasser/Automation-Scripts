from Tkinter import *

class Application(Frame, object):
	""" Gui Application """
	def __init__(self, master):
		""" Initialize the frame """
		super(Application, self).__init__(master)
		self.grid()
		self.bttn1_clicks = 0 # number of button clicks
		self.create_widgets()

	def create_widgets(self):
		""" Create three buttons that do nothing """
		# create first button
		self.bttn1 = Button(self)
		self.bttn1["text"] = "Total Clicks: 0"
		self.bttn1["command"] = self.update_count
		self.bttn1.grid()

		# # create second button
		# self.bttn2 = Button(self)
		# self.bttn2.grid()
		# self.bttn2.configure(text = "Me too!")

		# # create a third button
		# self.bttn3 = Button(self)
		# self.bttn3.grid()
		# self.bttn3["text"] = "Same here! "

	def update_count(self):
		""" Increase click count and display new total. """
		self.bttn1_clicks += 1
		self.bttn1["text"] = "Total Clicks: " + str(self.bttn1_clicks)

# main
root = Tk()
root.title("Lazy buttons")
root.geometry("200x85")
app = Application(root)

root.mainloop()