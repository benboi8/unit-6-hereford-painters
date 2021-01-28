import pygame as pg
from pygame import gfxdraw
import datetime as dt
import os
from os import listdir
from os.path import isfile, join

pg.init()

colDarkGray = (55, 55, 55)
colLightGray = (205, 205, 205)
colBlack = (0, 0, 0)
colWhite = (255, 255, 255)
colRed = (195, 90, 90)
colGreen = (90, 195, 90)
colBlue = (90, 90, 195)

scalingFactor = 2
WIDTH, HEIGHT = 640 * scalingFactor, 360 * scalingFactor
screen = pg.display.set_mode((WIDTH, HEIGHT))
Font = pg.font.SysFont("arial", 8 * scalingFactor)
pg.display.set_caption("Hereford painters")
icon = pg.image.load("paint brush icon.png")
pg.display.set_icon(icon)

allInputBoxs = []
allRadioButtons = []
allLabels = []
allCheckBoxs = []

allWallInputBoxs = []
allWindowInputBoxs = []

# for wall and window text inputs
allowedKeys = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "."]


paintQualityCosts = {
	"Standard": 1.00,
	"Economic": 0.80,
	"Premium": 1.75,
}

wallWidthMinimum = 1
wallWidthMaximum = 25
wallHeightMinimum = 2.4
wallHeightMaximum = 6

windowWidthMinimum = 0.9
windowWidthMaximum = 2
windowHeightMinimum = 0.9
windowHeightMaximum = 1.5

errorMessage = "Error messages: None" 

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

def CalculateTotalArea(walls, windows, numberOfWindowsTextBox):
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

def CheckAllValues(wallInput, windowInput, paintQualityButton, undercoatCheckBox, numberOfWindowsTextBox):
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

	totalArea, numberOfWindows = CalculateTotalArea(allWalls, allWindows, numberOfWindowsTextBox)
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
		print("New folder with name {name} created in current directory at {time}.".format(name=invoiceDirectoryName, time=time))

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
		InvoiceFile.write(invoiceMessage)
		InvoiceFile.write("Invoice number: {number}.\n".format(number=invoiceNumber))
		InvoiceFile.write("Cost: £{cost}.\n".format(cost=cost))
		InvoiceFile.write("Area: {area}m^2.\n".format(area=area))
		InvoiceFile.write("Paint quality: {quality}\n".format(quality=paintQuality))
		InvoiceFile.write("Time processed: {time}.\n".format(time=time))
		InvoiceFile.close()
		print("New invoice with name {name} created at {time}.".format(name=fileName, time=time))

	invoiceNumberLabel.UpdateText("Invoice number: {number}.".format(number=invoiceNumber))
	costLabel.UpdateText("Cost: £{cost}.".format(cost=cost))
	areaLabel.UpdateText("Area: {area}m^\u00b2.".format(area=area))
	timeLabel.UpdateText("Time processed: {time}.".format(time=time))

class Label:
	def __init__(self, rect, text="", font=Font, color=colLightGray):
		self.surface = screen
		self.rect = pg.Rect(rect)
		self.text = text
		self.color = color
		self.font = font
		self.textSurface = self.font.render(self.text, True, self.color)
		width = max(50, self.textSurface.get_width()+10)
		height = max(25, self.textSurface.get_height()+10)
		self.rect.w = width
		self.rect.h = height
		allLabels.append(self)

	def Draw(self, width=3):
		self.surface.blit(self.textSurface, (self.rect.x + 5, self.rect.y + 5))
		DrawRectOutline(self.surface, self.color, self.rect, width)

	def UpdateText(self, newText):
		self.text = newText
		self.textSurface = self.font.render(self.text, True, self.color)
		width = max(50, self.textSurface.get_width()+10)
		height = max(25, self.textSurface.get_height()+10)
		self.rect.w = width
		self.rect.h = height

class InputBox:
	def __init__(self, rect, displayText='', inactiveColor=colLightGray, activeColor=colWhite):
		self.surface = screen
		self.rect = pg.Rect(rect)
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
		self.surface.blit(self.displayTextSurface, (self.rect.x+5, self.rect.y+5))
		self.surface.blit(self.textSurface, (self.rect.x+self.displayTextSurface.get_width()+10, self.rect.y+5))
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
				self.text = "0."
				return
			if self.text == "0":
				self.text = ""
			if key in allowedKeys:
				self.text += key

class RadioButton:
	def __init__(self, rect, text=[], color=colLightGray):
		self.surface = screen
		self.allRects = rect
		# used for the border around all the radio buttons
		x = self.allRects[0][0] - 10
		y = self.allRects[0][1]
		w = self.allRects[0][2]
		h = 0
		for i in range(len(self.allRects)): 
			h += self.allRects[0][3]
		self.containingRect = pg.Rect(x, y, w, h)
		self.allText = text
		self.color = color
		self.active = [False for i in range(len(self.allRects))]
		self.value = "none"
		allRadioButtons.append(self)

	def Draw(self, radius=8):
		# draw border
		DrawRectOutline(self.surface, self.color, self.containingRect, 3)
		for i, rect in enumerate(self.allRects):
			rect = pg.Rect(rect)
			# draw the circle in the radio select
			center = GetCenterOfRect(rect)
			pg.gfxdraw.circle(self.surface, rect.x, center[1], radius, self.color)
			# render the text of each button
			self.textSurface = Font.render((self.allText[i] + " £"+ str(paintQualityCosts[self.allText[i]]) + " per squre meter."), True, self.color)
			self.surface.blit(self.textSurface, (rect.x + 10, center[1] - 10))

			# fill the radio button when pressed
			if self.active[i]:
				pg.gfxdraw.filled_circle(self.surface, rect.x, center[1], radius, self.color)

	def HandleEvent(self, event):
		for i, rect in enumerate(self.allRects):
			rect = pg.Rect(rect)
			if event.type == pg.MOUSEBUTTONUP:
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
	def __init__(self, rect, text="", undercoatCost=0.45, color=colLightGray):
		self.surface = screen
		self.rect = pg.Rect(rect)
		# rect for the inner box
		x = self.rect.x + 5
		y = self.rect.y + (self.rect.h // 2) - 5
		w = 10
		h = 10
		self.checkRect = pg.Rect(x, y, w, h)

		self.text = text
		self.color = color
		self.textSurface = Font.render(text, True, self.color)

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
		self.surface.blit(self.textSurface, (self.checkRect.x + self.checkRect.w + 5, self.rect.y + 5))

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

# create objects 
# title
TitleFont = pg.font.SysFont("arial", 18 * scalingFactor)
titleLabel = Label((350, 25, WIDTH - 50, 40), "Hereford Painters and Decorators", TitleFont)

# create wall width and height input boxs as well as label
wallLabel = Label((100, 100, 100, 30), "Wall dimensions:")
wallLabel = Label((310, 100, 100, 30), "Minimum width: " + str(wallWidthMinimum) + "m. Maximum width: " + str(wallWidthMaximum) + "m. Minimum height: " + str(wallHeightMinimum) + "m. Maximum height: " + str(wallHeightMaximum) + "m.")
wall1WidthTextBox = InputBox((100, 140, 200, 30), "First wall width:")
wall1HeightTextBox = InputBox((100, 180, 200, 30), "Wall height:")
wall2WidthTextBox = InputBox((310, 140, 200, 30), "Second wall width:")

allWallInputBoxs.append((wall1WidthTextBox, wall1HeightTextBox))
allWallInputBoxs.append((wall2WidthTextBox, wall1HeightTextBox))

# create window width and height input boxs as well as label
windowLabel = Label((410, 250, 100, 30), "Window dimensions:")
windowLabel = Label((410, 290, 100, 30), "Minimum width: " + str(windowWidthMinimum) + "m. Maximum width: " + str(windowWidthMaximum) + "m. Minimum height: " + str(windowHeightMinimum) + "m. Maximum height: " + str(windowHeightMaximum) + "m.")
numberOfWindowsTextBox = InputBox((410, 330, 200, 30), "Number of Windows:")
windowWidthTextBox = InputBox((410, 370, 200, 30), "Window width:")
windowHeightTextBox = InputBox((410, 410, 200, 30), "Window height:")

allWindowInputBoxs.append((windowWidthTextBox, windowHeightTextBox))

# create input for paint qulity 
radioLabel = Label((100, 250, 100, 30), "Paint quality:")
paintQualityButton = RadioButton([(110, 290, 250, 30), (110, 320, 250, 30), (110, 350, 250, 30)], ["Standard", "Economic", "Premium"])

# input for undercoat
undercoatCheckBox = CheckBox((100, 390, 100, 30), "Undercoat")

# used to display error messages to the user such as width being to short
errorMessageLabel = Label((100, 680, 500, 30), str(errorMessage))

# used to display invoice data
invoiceNumberLabel = Label((100, 490, 500, 30), "Invoice number: ")
costLabel = Label((100, 530, 500, 30), "Cost: ")
areaLabel = Label((100, 570, 500, 30), "Area: ")
timeLabel = Label((100, 610, 500, 30), "Time processed: ")