import pygame as pg
from pygame import gfxdraw
import datetime as dt
import os
from os import listdir
from os.path import isfile, join

pg.init()

colDarkGray = (55, 55, 55)
colLightGray = (205, 205, 205)
colWhite = (255, 255, 255)


# change SF to change how the screen is scaled. deafualt is 2
# SF = 1: 640, 360
# SF = 2: 1280, 720
# SF = 3: 1920, 1080
SF = 2
WIDTH, HEIGHT = 640 * SF, 360 * SF
screen = pg.display.set_mode((WIDTH, HEIGHT))
Font = pg.font.SysFont("arial", 8 * SF)
pg.display.set_caption("Hereford painters")
pg.display.set_icon(pg.image.load("paint brush icon.png"))

allInputBoxs = []
allRadioButtons = []
allLabels = []
allCheckBoxs = []
allButtons = []

allWallInputBoxs = []
allWindowInputBoxs = []

# for wall and window text inputs
allowedKeys = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "."]

paintQualityCosts = {
	"Standard": 1.00,
	"Economic": 0.80,
	"Premium": 1.75,
}

undercoatCost = 0.45

wallWidthMinimum = 1
wallWidthMaximum = 25
wallHeightMinimum = 2.4
wallHeightMaximum = 6

windowWidthMinimum = 0.9
windowWidthMaximum = 2
windowHeightMinimum = 0.9
windowHeightMaximum = 1.5

errorMessage = "Error message: None" 

# used to create and store invoices
invoicePrefix = "HPI-"
invoiceDirectoryName = invoicePrefix + "invoices"
rootDirectory = os.getcwd()
invoiceDirectoryCreated = False

invoiceMessage = "Company name: Hereford Painters and Decorators\nAddress: 45 High Street\nLocation: Hereford\nPostcode: HR1 1RT\nVAT Number: 123456789A\nTelephone: 01432 123456\n\n"


def DrawRectOutline(surface, color, rect, width=1):
    x, y, w, h = rect
    width = max(width, 1)  # Draw at least one rect.
    width = min(min(width, w//2), h//2)  # Don't overdraw.

    # This draws several smaller outlines inside the first outline
    # Invert the direction if it should grow inwards.
    for i in range(width):
        pg.gfxdraw.rectangle(surface, (x-i, y-i, w+i*2, h+i*2), color)

def GetCenterOfRect(rect):
	x, y, w, h = rect
	midX, midY = x + (w // 2), y + (h // 2)
	return (midX, midY)

def CalculateTotalArea(walls, windows):
	totalWallArea = 0
	totalWindowArea = 0
	# go through every wall and get area
	for dimensions in walls:
		width, height = dimensions
		totalWallArea += width * height

	# go through every window and get area
	for dimensions in windows:
		width, height = dimensions
		totalWindowArea += width * height

	numberOfWindows = int(numberOfWindowsTextBox.text)

	# get area of all four walls
	totalWallArea *= 2
	totalWindowArea *= numberOfWindows

	return round(totalWallArea - totalWindowArea, ndigits=2), numberOfWindows

def CalculateTotalCost(totalArea, paintCost, undercoatCost):
	# get normal paint cost and add the cost of undercoat
 	return round(float((totalArea * paintCost) + (totalArea * undercoatCost)), ndigits=2)

def CheckAllValues(wallInput, windowInput):
	allWalls = []
	allWindows = []
	for wallDimensions in wallInput:
		# check each walls width and height
		width, height = float(wallDimensions[0].text), float(wallDimensions[1].text)
		if width < wallWidthMinimum:
			return "Wall width is too short."
		if width > wallWidthMaximum:
			return "Wall width is too long."
		if height < wallHeightMinimum:
			return "Wall height is too short."
		if height > wallHeightMaximum:
			return "Wall height is too long."
		allWalls.append((width, height))

	for windowDimensions in windowInput:
		# check each windows width and height
		width, height = float(windowDimensions[0].text), float(windowDimensions[1].text)
		if width < windowWidthMinimum:
			return "Window width is too short."
		if width > windowWidthMaximum:
			return "Window width is too long."
		if height < windowHeightMinimum:
			return "Window height is too short."
		if height > windowHeightMaximum:
			return "Window height is too long."
		allWindows.append((width, height))

	# check if a paint quality has been selected
	paintQuality = paintQualityButton.value
	if paintQuality == "none":
		return "Paint quality not chosen."

	undercoatCost = undercoatCheckBox.value

	totalArea, numberOfWindows = CalculateTotalArea(allWalls, allWindows)
	if totalArea <= 0:
		return "The area of windows is greater than the area of walls."

	if numberOfWindows < 1:
		return "At least 1 window needs to be selected."
	totalCost = CalculateTotalCost(totalArea, paintQualityCosts[paintQuality], undercoatCost)

	CreateInvoice(totalCost, totalArea, paintQuality)

	# no error message
	return "None"

def CreateInvoice(cost, area, paintQuality):
	global 	invoicePrefix, invoiceDirectoryName, rootDirectory, invoiceDirectoryCreated
	time = dt.datetime.utcnow()

	# check if folder called HPI-invoices exists
	filesInDirectory = [file for file in listdir(rootDirectory)]
	invoiceExists = False

	for file in filesInDirectory:
		if invoiceDirectoryName in file:
			invoiceExists = True

	# make folder if HPI-invoices doesn't exist
	if not invoiceExists: 
		os.mkdir(invoiceDirectoryName)
		print("New folder with name {name} created in '{directory}' at {time}.".format(name=invoiceDirectoryName, directory=rootDirectory, time=time))

	# change current working directory to HPI-invoices
	if not invoiceDirectoryCreated:
		os.chdir(invoiceDirectoryName)
		invoiceDirectoryCreated = True
	currentWorkingDirectory = os.getcwd()
	directory = [file for file in listdir(currentWorkingDirectory)]

	# check if there are already existing invoices
	allInvoices = []
	invoice = ""
	for file in directory:
		if invoicePrefix in file:
			for char in file[4:]:
				if char == ".":
					break
				else:
					invoice += char
			allInvoices.append(int(invoice))
			invoice = ""

	if len(allInvoices) > 0:
		# find the largest invoice and add 1 to get new invoice number
		largestInvoice = max(allInvoices)
		invoiceNumber = int(largestInvoice) + 1
	else:
		# no invoices exist so start at 0 
		invoiceNumber = 0	
	invoiceNumber = str(invoiceNumber)

	# create invoice with invoice number
	fileName = invoicePrefix + invoiceNumber + ".txt"
	with open(fileName, "w+") as InvoiceFile:
		time = dt.datetime.utcnow()
		timeFormat = time.strftime("%Y/%m/%d %H:%M:%S")
		if undercoatCheckBox.value == undercoatCost:
			hasUndercoat = "Yes"
		else:
			hasUndercoat = "No"
		InvoiceFile.write(invoiceMessage)
		InvoiceFile.write("Invoice number: {number}.\n".format(number=invoiceNumber))
		InvoiceFile.write("Cost: £{cost}.\n".format(cost=cost))
		InvoiceFile.write("Area: {area}m\u00b2.\n".format(area=area))
		InvoiceFile.write("Paint quality: {quality}\n".format(quality=paintQuality))
		InvoiceFile.write("Included undercoat: {hasUndercoat}.\n".format(hasUndercoat=hasUndercoat))
		InvoiceFile.write("Time processed: {time}.\n".format(time=timeFormat))
		InvoiceFile.close()
		print("New invoice created in '{directory}' with name {name} created at {time}.".format(directory=currentWorkingDirectory, name=fileName, time=timeFormat))

	invoiceNumberLabel.UpdateText("Invoice number: {number}.".format(number=invoiceNumber))
	costLabel.UpdateText("Cost: £{cost}.".format(cost=cost))
	areaLabel.UpdateText("Area: {area}m\u00b2.".format(area=area))
	timeLabel.UpdateText("Time processed: {time}.".format(time=timeFormat))

class Label:
	def __init__(self, rect, text="", font=Font, color=colLightGray):
		self.surface = screen
		self.rect = pg.Rect(rect[0] * SF, rect[1] * SF, rect[2] * SF, rect[3] * SF)
		self.text = text
		self.color = color
		self.font = font
		self.textSurface = self.font.render(self.text, True, self.color)
		width = max(25 * SF, self.textSurface.get_width()+5*SF)
		height = max(13.5 * SF, self.textSurface.get_height()+5*SF)
		self.rect.w = width
		self.rect.h = height
		allLabels.append(self)

	def Draw(self, width=3):
		self.surface.blit(self.textSurface, (self.rect.x + 2.5 * SF, self.rect.y + 2.5 * SF))
		DrawRectOutline(self.surface, self.color, self.rect, width)

	def UpdateText(self, newText):
		self.text = newText
		self.textSurface = self.font.render(self.text, True, self.color)
		# change with and height for text
		width = max(25 * SF, self.textSurface.get_width()+5*SF)
		height = max(13.5 * SF, self.textSurface.get_height()+5*SF)
		self.rect.w = width
		self.rect.h = height

class InputBox:
	def __init__(self, rect, displayText='', inactiveColor=colLightGray, activeColor=colWhite):
		self.surface = screen
		self.rect = pg.Rect(rect[0] * SF, rect[1] * SF, rect[2] * SF, rect[3] * SF)
		self.InactiveColor = inactiveColor
		self.activeColor = activeColor
		self.currentColor = self.InactiveColor
		self.displayText = displayText	
		self.text = "0"
		self.characterLimit = 3
		self.displayTextSurface = Font.render(self.displayText, True, self.currentColor)
		self.textSurface = Font.render(self.text, True, self.currentColor)
		self.active = False
		allInputBoxs.append(self)

	def Draw(self):
		self.surface.blit(self.displayTextSurface, (self.rect.x+2.5 * SF, self.rect.y+2.5 * SF))
		self.surface.blit(self.textSurface, (self.rect.x+self.displayTextSurface.get_width()+5 * SF, self.rect.y+2.5 * SF))
		pg.draw.rect(self.surface, self.currentColor, self.rect, 2)

	def HandleEvent(self, event):
		if event.type == pg.MOUSEBUTTONUP:
			# If the user clicked on the input_box rect.
			if self.rect.collidepoint(pg.mouse.get_pos()):
				# Toggle the active variable.
				self.active = not self.active
			else:
				self.active = False
			# Change the current color of the input box.
			if self.active:
				self.currentColor = self.activeColor
			else:
				self.currentColor = self.InactiveColor
			# change display text color
			self.displayTextSurface = Font.render(self.displayText, True, self.currentColor)
		# get key inputs 
		if event.type == pg.KEYDOWN:
			if self.active:
				if event.key == pg.K_BACKSPACE:
					self.text = self.text[:-1]
				else:
					self.FilterText(event.unicode)
				# make empty text = 0
				if self.text == "":
					self.text = "0"
				# Re-render the text.
				self.textSurface = Font.render(self.text, True, self.currentColor)

	def FilterText(self, key):
		# check if new text will surpass characterLimit
		if len(self.text) + 1 <= self.characterLimit:
			# allow only certain characters
			if key == "." and self.text == "0":
				# allow decimal numbers that start with 0
				self.text = "0."
				return
			# clear the box when user starts typing
			if self.text == "0":
				self.text = ""
			# check if key is within allowed keys and add it to the text
			if key in allowedKeys:
				self.text += key

class RadioButton:
	def __init__(self, rect, text=[], color=colLightGray):
		self.surface = screen
		self.allRects = rect
		# used for the border around all the radio buttons
		x = (self.allRects[0][0] * SF) - 5 * SF
		y = self.allRects[0][1] * SF
		w = self.allRects[0][2] * SF
		h = 0
		for i in range(len(self.allRects)): 
			h += self.allRects[0][3] * SF
		self.containingRect = pg.Rect(x, y, w, h)
		self.allText = text
		self.color = color
		self.active = [False for i in range(len(self.allRects))]
		self.value = "none"
		allRadioButtons.append(self)

	def Draw(self, radius=4*SF):
		# draw border
		DrawRectOutline(self.surface, self.color, self.containingRect, 3)
		for i, rect in enumerate(self.allRects):
			rect = pg.Rect(rect[0] * SF, rect[1] * SF, rect[2] * SF, rect[3] * SF)
			# draw the circle in the radio select
			center = GetCenterOfRect(rect)
			pg.gfxdraw.circle(self.surface, rect.x, center[1], radius, self.color)
			# render the text of each button
			self.textSurface = Font.render((self.allText[i] + " £"+ str(paintQualityCosts[self.allText[i]]) + " per m\u00b2."), True, self.color)
			self.surface.blit(self.textSurface, (rect.x + 5 * SF, center[1] - 5 * SF))

			# fill the radio button when pressed
			if self.active[i]:
				pg.gfxdraw.filled_circle(self.surface, rect.x, center[1], radius, self.color)

	def HandleEvent(self, event):
		if event.type == pg.MOUSEBUTTONUP:
			for i, rect in enumerate(self.allRects):
				rect = pg.Rect(rect[0] * SF, rect[1] * SF, rect[2] * SF, rect[3] * SF)
				# check if button is pressed
				if rect.collidepoint(pg.mouse.get_pos()):
					# reset the buttons so that only one can be active
					for j in range(len(self.active)):
						self.active[j] = False
						self.value = "none"
					# set the active button
					self.active[i] = not self.active[i]
					self.value = self.allText[i]
			
class CheckBox:
	def __init__(self, rect, text="", undercoatCost=undercoatCost, color=colLightGray):
		self.surface = screen
		self.rect = pg.Rect(rect[0] * SF, rect[1] * SF, rect[2] * SF, rect[3] * SF)
		# rect for the inner box
		x = self.rect.x + 2.5 * SF
		y = self.rect.y + (self.rect.h // 2) - 2.5 * SF
		w = 5 * SF
		h = 5 * SF
		self.checkRect = pg.Rect(x, y, w, h)

		self.text = text
		self.color = color
		self.textSurface = Font.render(text + " £0.45 per m\u00b2.", True, self.color)
		self.rect = pg.Rect(self.rect.x, self.rect.y, self.textSurface.get_width() + 12 * SF, self.rect.h)

		self.undercoatCost = undercoatCost

		allCheckBoxs.append(self)
		self.checked = False

	def Draw(self, width=3):
		# draw border
		DrawRectOutline(self.surface, self.color, self.rect, width)
		if not self.checked:
			# draw unfilled check box
			DrawRectOutline(self.surface, self.color, self.checkRect)
		else:
			# draw filled check box
			pg.draw.rect(self.surface, self.color, self.checkRect)
		# render text for button
		self.surface.blit(self.textSurface, (self.checkRect.x + self.checkRect.w + 2.5 * SF, self.rect.y + 2.5 * SF))

	def HandleEvent(self, event):
		if event.type == pg.MOUSEBUTTONUP:
			# check if button has been pressed
			if self.rect.collidepoint(pg.mouse.get_pos()):
				# toggle checked value
				self.checked = not self.checked

		# switch the undercoat cost between 0 and 0.45
		if self.checked:
			self.value = self.undercoatCost
		else:
			self.value = 0

class Button:
	def __init__(self, rect, text="", inactiveColor=colLightGray, activeColor=colWhite):
		self.surface = screen
		self.rect = pg.Rect(rect[0] * SF, rect[1] * SF, rect[2] * SF, rect[3] * SF)
		self.text = text
		self.inactiveColor = inactiveColor
		self.activeColor = activeColor
		self.currentColor = self.inactiveColor
		self.textSurface = Font.render(self.text, True, self.currentColor)
		self.active = False
		allButtons.append(self)

	def Draw(self, width=3):
		DrawRectOutline(self.surface, self.currentColor, self.rect, width)
		self.surface.blit(self.textSurface, (self.rect.x+2.5 * SF, self.rect.y + 2.5 * SF))

	def HandleEvent(self, event):
		if event.type == pg.MOUSEBUTTONDOWN:
			# check if button has been pressed
			if self.rect.collidepoint(pg.mouse.get_pos()):
				self.active = True

		# check if button has been released
		if event.type == pg.MOUSEBUTTONUP:
			self.active = False

		# change color
		if self.active:
			self.currentColor = self.activeColor
		else:
			self.currentColor = self.inactiveColor
		# re-render text
		self.textSurface = Font.render(self.text, True, self.currentColor)

# create objects 
# title
TitleFont = pg.font.SysFont("arial", 18 * SF)
titleLabel = Label((175, 12.5, WIDTH - (25 ), 20), "Hereford Painters and Decorators", TitleFont)

# create wall width and height input boxs as well as label
wallLabel = Label((50, 50, 50, 15), "Wall dimensions:")
wallLabel = Label((50, 70, 50, 15), "Minimum width: " + str(wallWidthMinimum) + "m. Maximum width: " + str(wallWidthMaximum) + "m. Minimum height: " + str(wallHeightMinimum) + "m. Maximum height: " + str(wallHeightMaximum) + "m.")
wall1WidthTextBox = InputBox((50, 90, 100, 15), "First wall width:")
wall2WidthTextBox = InputBox((50, 110, 100, 15), "Second wall width:")
wall1HeightTextBox = InputBox((50, 130, 100, 15), "Wall height:")

allWallInputBoxs.append((wall1WidthTextBox, wall1HeightTextBox))
allWallInputBoxs.append((wall2WidthTextBox, wall1HeightTextBox))

# create window width and height input boxs as well as label
windowLabel = Label((205, 155, 50, 15), "Window dimensions:")
windowLabel = Label((205, 175, 50, 15), "Minimum width: " + str(windowWidthMinimum) + "m. Maximum width: " + str(windowWidthMaximum) + "m. Minimum height: " + str(windowHeightMinimum) + "m. Maximum height: " + str(windowHeightMaximum) + "m.")
numberOfWindowsTextBox = InputBox((205, 195, 100, 15), "Number of Windows:")
windowWidthTextBox = InputBox((205, 215, 100, 15), "Window width:")
windowHeightTextBox = InputBox((205, 235, 100, 15), "Window height:")

allWindowInputBoxs.append((windowWidthTextBox, windowHeightTextBox))

# create input for paint qulity 
radioLabel = Label((50, 155, 50, 15), "Paint quality:")
paintQualityButton = RadioButton([(55, 175, 95, 15), (55, 190, 95, 15), (55, 205, 95, 15)], ["Standard", "Economic", "Premium"])

# input for undercoat
undercoatCheckBox = CheckBox((50, 225, 50, 15), "Undercoat")

# used to display error messages to the user such as width being to short
errorMessageLabel = Label((50, 340, 250, 15), str(errorMessage))

# used to display invoice data
invoiceNumberLabel = Label((50, 255, 250, 15), "Invoice number: ")
costLabel = Label((50, 275, 250, 15), "Cost: ")
areaLabel = Label((50, 295, 250, 15), "Area: ")
timeLabel = Label((50, 315, 250, 15), "Time processed: ")

# subit button to create invoice
submitButton = Button((205, 280, 50, 15), "Submit")
