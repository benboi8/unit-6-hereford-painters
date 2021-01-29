from classes import *

# draws all objects to screen
def DrawLoop():
    screen.fill(colDarkGray)

    for inputBox in allInputBoxs:
        inputBox.Draw()

    for radioButton in allRadioButtons:
        radioButton.Draw() 

    for label in allLabels:
        label.Draw()

    for checkBox in allCheckBoxs:
        checkBox.Draw()

    for button in allButtons:
        button.Draw()

    # change the text of the error message
    errorMessageLabel.UpdateText(str(errorMessage))

    pg.display.update()

def Quit():
    global running
    running = False

def Main():
    global running, errorMessage
    running = True
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                Quit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    Quit()

            for inputBox in allInputBoxs:
                inputBox.HandleEvent(event)

            for radioButton in allRadioButtons:
                radioButton.HandleEvent(event)

            for checkbox in allCheckBoxs:
                checkbox.HandleEvent(event)

            for button in allButtons:
                button.HandleEvent(event)

        # submit all the data to create an invoice
        if submitButton.active:
            errorMessage = "Error message: "
            errorMessage += CheckAllValues(allWallInputBoxs, allWindowInputBoxs)
            submitButton.active = False

        DrawLoop()

if __name__ == "__main__":
    Main()