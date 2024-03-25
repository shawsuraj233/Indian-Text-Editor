# importing required libraries
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtPrintSupport import *
from indic_transliteration import sanscript
import os
import sys
try:
    from ListenJs import Listen,driver
except:
    pass


class FindDialog(QDialog):
	def __init__(self, parent=None):
		super().__init__(parent)
		self.setWindowTitle("Find Text")
		self.setStyleSheet("background-color: white; color: black;")
		self.layout = QVBoxLayout()

		self.found_indices = []
		self.current_index = -1

		self.label = QLabel("Find:")
		self.layout.addWidget(self.label)

		self.find_input = QLineEdit()
		self.layout.addWidget(self.find_input)

		self.find_button = QPushButton("Find")
		self.find_button.clicked.connect(self.find_text)
		self.layout.addWidget(self.find_button)

		self.find_next_button = QPushButton("Find Next")
		self.find_next_button.clicked.connect(self.select_next)
		self.layout.addWidget(self.find_next_button)

		self.find_previous_button = QPushButton("Find Previous")
		self.find_previous_button.clicked.connect(self.select_previous)
		self.layout.addWidget(self.find_previous_button)

		self.result_label = QLabel()
		self.layout.addWidget(self.result_label)

		self.setLayout(self.layout)

		self.last_found_cursor = None


	def find_text(self):
		# Reset found indices and current index
		select_text = self.find_input.text().lower()
		self.found_indices.clear()
		self.current_index = -1

		words = self.parent().editor.document().toPlainText().lower().split(" ")
		self.found_indices = [i for i, word in enumerate(words) if word == select_text ]
		

		if len(self.found_indices) != 0:
			self.current_index = 0  # Start from the first found index
			self.select_current_index()

		else:
			self.result_label.setText("Please enter text to find")

	def select_current_index(self):
		words = self.parent().editor.document().toPlainText().lower().split(" ")
		if self.current_index >= 0 and self.current_index < len(self.found_indices):
			index = self.found_indices[self.current_index]
			start_pos = sum(len(words[i]) + 1 for i in range(index))
			end_pos = start_pos + len(words[index])
			cursor = self.parent().editor.textCursor()
			cursor.setPosition(start_pos)
			cursor.setPosition(end_pos, QTextCursor.KeepAnchor)
			self.parent().editor.setTextCursor(cursor)

	def select_next(self):
		if self.found_indices:
			self.current_index = (self.current_index + 1) % len(self.found_indices)
			self.select_current_index()

	def select_previous(self):
		if self.found_indices:
			self.current_index = (self.current_index - 1) % len(self.found_indices)
			self.select_current_index()


class FindReplaceDialog(QDialog):

	def __init__(self, parent=None):
		super().__init__(parent)
		self.setWindowTitle("Find and Replace Text")
		self.setStyleSheet("background-color: white; color: black;")
		self.layout = QVBoxLayout()

		self.find_text_label = QLabel("Find:")
		self.layout.addWidget(self.find_text_label)

		self.find_input = QLineEdit()
		self.layout.addWidget(self.find_input)

		self.replace_text_label = QLabel("Replace with:")
		self.layout.addWidget(self.replace_text_label)

		self.replace_input = QLineEdit()
		self.layout.addWidget(self.replace_input)

		self.find_button = QPushButton("Find")
		self.find_button.clicked.connect(self.find_text)
		self.layout.addWidget(self.find_button)

		self.replace_button = QPushButton("Replace")
		self.replace_button.clicked.connect(self.replace_text)
		self.layout.addWidget(self.replace_button)

		self.replace_next_button = QPushButton("Replace Next")
		self.replace_next_button.clicked.connect(self.replace_next)
		self.layout.addWidget(self.replace_next_button)

		self.replace_all_button = QPushButton("Replace All")
		self.replace_all_button.clicked.connect(self.replace_all)
		self.layout.addWidget(self.replace_all_button)

		self.skip_button = QPushButton("Skip")
		self.skip_button.clicked.connect(self.skip_next)
		self.layout.addWidget(self.skip_button)

		self.result_label = QLabel()
		self.layout.addWidget(self.result_label)

		self.setLayout(self.layout)
		self.found_indices = []
		self.current_index = -1
		self.last_found_cursor = None


	def find_text(self):
		# Reset found indices and current index
		select_text = self.find_input.text().lower()
		self.found_indices.clear()
		self.current_index = -1

		words = self.parent().editor.toPlainText().lower().split(" ")
		self.found_indices = [i for i, word in enumerate(words) if word == select_text]

		if self.found_indices:
			self.current_index = 0  # Start from the first found index
			self.select_current_index()

	def select_current_index(self):
		words = self.parent().editor.toPlainText().split(" ")
		if self.current_index >= 0 and self.current_index < len(self.found_indices):
			index = self.found_indices[self.current_index]
			start_pos = sum(len(words[i]) + 1 for i in range(index))
			end_pos = start_pos + len(words[index])
			cursor = self.parent().editor.textCursor()
			cursor.setPosition(start_pos)
			cursor.setPosition(end_pos, QTextCursor.KeepAnchor)
			self.parent().editor.setTextCursor(cursor)


	def select_next(self):
		if self.found_indices:
			self.current_index = (self.current_index + 1) % len(self.found_indices)
			self.select_current_index()

	def replace_text(self):
		selected_text = self.parent().editor.textCursor().selectedText()
		if selected_text:
			replace_text = self.replace_input.text()
			cursor = self.parent().editor.textCursor()
			cursor.insertText(replace_text)
			cursor.setPosition(cursor.position() - len(replace_text), QTextCursor.KeepAnchor)
			self.parent().editor.setTextCursor(cursor)

	def replace_next(self):
		if self.found_indices:
			self.select_next()
			self.replace_text()

	def replace_all(self):
		while self.current_index >= 0 :
			self.find_text()
			self.replace_text() 

	def skip_next(self):
		if self.found_indices:
			self.select_next()




	# Creating main window class


# Creating main window class
class MainWindow(QMainWindow):

    # constructor
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        # setting window geometry
        self.setGeometry(100, 100, 1200, 650)

        # creating a layout
        layout = QVBoxLayout()

        # creating a QPlainTextEdit object
        self.editor = QTextEdit()
        self.editor.textChanged.connect(self.update_text)

        

        # setting font to the editor
        fixedfont = QFontDatabase.systemFont(QFontDatabase.FixedFont)
        fixedfont.setPointSize(12)
        self.editor.setFont(fixedfont)

        # self.path holds the path of the currently open file.
        # If none, we haven't got a file open yet (or creating new).
        self.path = None

        # adding editor to the layout
        layout.addWidget(self.editor)

        # creating a QWidget layout
        container = QWidget()

        # setting layout to the container
        container.setLayout(layout)

        # making container as central widget
        self.setCentralWidget(container)

        # creating a status bar object
        self.status = QStatusBar()

        # setting stats bar to the window
        self.setStatusBar(self.status)

        # creating a file tool bar
        file_toolbar = QToolBar("File")

        # adding file tool bar to the window
        self.addToolBar(file_toolbar)

        # creating a file menu
        file_menu = self.menuBar().addMenu("&File")

        # creating actions to add in the file menu

        # creating a new file action
        new_file_action = QAction("New File", self)
        new_file_action.setIcon(QIcon('Images/new.png'))
        new_file_action.setStatusTip("Create a new file")
        new_file_action.triggered.connect(self.file_new)
        new_file_action.setShortcut(QKeySequence.New)
        file_menu.addAction(new_file_action)

        # creating a open file action
        open_file_action = QAction("Open file", self)
        open_file_action.setIcon(QIcon('Images/open.png'))

        # setting status tip
        open_file_action.setStatusTip("Open file")

        # adding action to the open file
        open_file_action.triggered.connect(self.file_open)

        #adding shortcut to open file i.e. Ctrl+o
        open_file_action.setShortcut(QKeySequence.Open) 

        # adding this to file menu
        file_menu.addAction(open_file_action)

    
        # similarly creating a save action
        save_file_action = QAction("Save", self)
        save_file_action.setIcon(QIcon('Images/save.png'))
        save_file_action.setStatusTip("Save current page")
        save_file_action.triggered.connect(self.file_save)
        save_file_action.setShortcut(QKeySequence.Save)
        file_menu.addAction(save_file_action)

        # similarly creating save action
        saveas_file_action = QAction("Save As", self)
        saveas_file_action.setIcon(QIcon('Images/save_as.png'))
        saveas_file_action.setStatusTip("Save current page to specified file")
        saveas_file_action.triggered.connect(self.file_saveas)
        saveas_file_action.setShortcut(QKeySequence.SaveAs)
        file_menu.addAction(saveas_file_action)
        
        # for print action
        print_action = QAction("Print", self)
        print_action.setIcon(QIcon('Images/print.png'))
        print_action.setStatusTip("Print current page")
        print_action.triggered.connect(self.file_print)
        print_action.setShortcut(QKeySequence.Print)
        file_menu.addAction(print_action)

        file_menu.addSeparator()
        

        # creating a edit menu bar
        edit_menu = self.menuBar().addMenu("&Edit")

        # adding actions to the tool bar and menu bar

        # undo action
        undo_action = QAction("Undo", self)
        undo_action.setIcon(QIcon('Images/undo.png'))
        # adding status tip
        undo_action.setStatusTip("Undo last change")

        # when triggered undo the editor
        undo_action.triggered.connect(self.editor.undo)
        undo_action.setShortcut(QKeySequence.Undo)

        edit_menu.addAction(undo_action)

        # redo action
        redo_action = QAction("Redo", self)
        redo_action.setIcon(QIcon('Images/redo.png'))
        redo_action.setStatusTip("Redo last change")

        # when triggered redo the editor
        redo_action.triggered.connect(self.editor.redo)
        redo_action.setShortcut(QKeySequence.Redo)

        edit_menu.addAction(redo_action)

        # cut action
        cut_action = QAction("Cut", self)
        cut_action.setIcon(QIcon('Images/cut.png'))
        cut_action.setStatusTip("Cut selected text")

        # when triggered cut the editor text
        cut_action.triggered.connect(self.editor.cut)
        cut_action.setShortcut(QKeySequence.Cut) 

        # adding this to menu and tool bar
        edit_menu.addAction(cut_action)

        # copy action
        copy_action = QAction("Copy", self)
        copy_action.setIcon(QIcon('Images/copy.png'))
        copy_action.setStatusTip("Copy selected text")

        # when triggered copy the editor text
        copy_action.triggered.connect(self.editor.copy)
        copy_action.setShortcut(QKeySequence.Copy)

        # adding this to menu and tool bar
        edit_menu.addAction(copy_action)

        # paste action
        paste_action = QAction("Paste", self)
        paste_action.setIcon(QIcon('Images/paste.png'))
        paste_action.setStatusTip("Paste from clipboard")

        # when triggered paste the copied text
        paste_action.triggered.connect(self.editor.paste)
        paste_action.setShortcut(QKeySequence.Paste)

        # adding this to menu and tool bar
        edit_menu.addAction(paste_action)

        # select all action
        select_action = QAction("Select all", self)
        select_action.setIcon(QIcon('Images/select.png'))
        select_action.setStatusTip("Select all text")

        # when this triggered select the whole text
        select_action.triggered.connect(self.editor.selectAll)
        select_action.setShortcut(QKeySequence.SelectAll)

        # adding this to menu and tool bar
        edit_menu.addAction(select_action)

        # select all action
        find_action = QAction("Find", self)
        find_action.setIcon(QIcon('Images/find.png'))
        find_action.setStatusTip("Find Text")

        # when this triggered select the whole text
        find_action.triggered.connect(self.find_clicked)
        find_action.setShortcut(QKeySequence.Find)

        # adding this to menu and tool bar
        edit_menu.addAction(find_action)


        # select all action
        replace_action = QAction("Find and Replace", self)
        replace_action.setIcon(QIcon('Images/replace.png'))
        replace_action.setStatusTip("Find and Replace Text")

        # when this triggered select the whole text
        replace_action.triggered.connect(self.open_find_replace_dialog)
        replace_action.setShortcut(QKeySequence.Replace)

        # adding this to menu and tool bar
        edit_menu.addAction(replace_action)
        

        edit_menu.addSeparator()
        # wrap action
        wrap_action = QAction("Wrap text to window", self)
        wrap_action.setStatusTip("Check to wrap text to window")

        # making it checkable
        wrap_action.setCheckable(True)

        # making it checked
        wrap_action.setChecked(True)

        # adding action
        wrap_action.triggered.connect(self.edit_toggle_wrap)

        # adding it to edit menu not to the tool bar
        edit_menu.addAction(wrap_action)

        #Creating theme bar
        theme_menu = self.menuBar().addMenu('&Themes')

        lightIcon = QIcon("Images/light_default.png")
        darkIcon = QIcon("Images/dark.png")
        pinkIcon = QIcon("Images/red.png")
        monokaiIcon = QIcon("Images/monokai.png")


        lightAction = QAction(lightIcon, 'Light Default', self, triggered=lambda: self.change_theme('white', 'black'))
        theme_menu.addAction(lightAction)

        darkAction = QAction(darkIcon, 'Dark', self, triggered=lambda: self.change_theme('#333333', 'white'))
        theme_menu.addAction(darkAction)

        pinkAction = QAction(pinkIcon, 'Pink', self, triggered=lambda: self.change_theme('pink', 'blue'))
        theme_menu.addAction(pinkAction)

        monokaiAction = QAction(monokaiIcon, 'Monokai', self, triggered=lambda: self.change_theme('orange', 'red'))
        theme_menu.addAction(monokaiAction)

        # Add these import statements at the beginning of your code
        font_toolbar = QToolBar("Font")
        self.addToolBar(font_toolbar)

        # Add font family selection combo box
        self.font_family_combo = QFontComboBox()
        self.font_family_combo.currentFontChanged.connect(self.change_font_family)
        font_toolbar.addWidget(self.font_family_combo)

        self.language_combo = QComboBox()
        self.language_combo.addItems(["English","Bengali","Devanagari","Gujarati","Gurumukhi","Grantha","Kannada","Malyalam","Oriya","Tamil","Tamil_SUB","Tamil_SUP","Telgu"])  
        font_toolbar.addWidget(self.language_combo)

        # Add font size selection combo box
        self.font_size_combo = QComboBox()
        self.font_sizes = [str(i) for i in range(8,81,2)]
        self.font_size_combo.addItems(self.font_sizes)
        self.font_size_combo.currentTextChanged.connect(self.change_font_size)
        font_toolbar.addWidget(self.font_size_combo)

        #Voice Typing
        self.microphone = QPushButton(self)
        self.microphone.setCheckable(True)
        self.microphone.setIcon(QIcon('Images/voice-control.png'))
        self.microphone.setToolTip("Voice Typing")
        self.microphone.clicked.connect(self.recording)
        font_toolbar.addWidget(self.microphone)

        # creating a bold button
        bold_button = QPushButton()
        bold_button.setCheckable(True)
        bold_button.setIcon(QIcon('Images/bold.png'))
        bold_button.setToolTip("Bold selected text")
        bold_button.clicked.connect(self.toggle_bold)
        bold_button.setShortcut(QKeySequence.Bold)

        # adding bold action to menu and toolbar
        file_toolbar.addWidget(bold_button)
        

        # creating an italic button with an image
        italic_button = QPushButton()
        italic_button.setCheckable(True)
        italic_button.setIcon(QIcon('Images/italic.png'))  # Replace 'path_to_italic_icon.png' with the actual path to your image
        italic_button.setToolTip("Italicize selected text")
        italic_button.clicked.connect(self.toggle_italic)

        # adding italic action to menu and toolbar
        file_toolbar.addWidget(italic_button)


        # creating a underline button with an image
        underline_button = QPushButton()
        underline_button.setCheckable(True)
        underline_button.setIcon(QIcon('Images/underline.png'))  # Replace 'path_to_underline_icon.png' with the actual path to your image
        underline_button.setToolTip("Underline selected text")
        underline_button.clicked.connect(self.toggle_underline)

        # adding underline action to menu and toolbar
        file_toolbar.addWidget(underline_button)

        #Alignment Buttons
        align_left = QPushButton()
        align_left.setCheckable(True)
        align_left.setIcon(QIcon('Images/left.png'))
        align_left.setToolTip("Align Text to Left")
        align_left.clicked.connect(self.Align_Left)
        file_toolbar.addWidget(align_left)
        
        align_right = QPushButton()
        align_right.setCheckable(True)
        align_right.setIcon(QIcon('Images/right.png'))
        align_right.setToolTip("Align Text to Right")
        align_right.clicked.connect(self.Align_Right)
        file_toolbar.addWidget(align_right)

        align_center = QPushButton()
        align_center.setCheckable(True)
        align_center.setIcon(QIcon('Images/center.png'))
        align_center.setToolTip("Align Text to Center")
        align_center.clicked.connect(self.Align_Center)
        file_toolbar.addWidget(align_center)

        align_justify = QPushButton()
        align_center.setCheckable(True)
        align_justify.setIcon(QIcon('Images/justify.png'))
        align_justify.setToolTip("Justify the Text")
        align_justify.clicked.connect(self.Align_Justify)
        file_toolbar.addWidget(align_justify)

        # Add color button to the toolbar
        color_button = QPushButton()
        color_button.setIcon(QIcon('Images/font_color.png'))
        color_button.setToolTip("Font Color Changer")
        color_button.clicked.connect(self.change_text_color)
        font_toolbar.addWidget(color_button)
        self.text_color = Qt.black  # Default text color

        # creating a find button with an image
        find_button = QPushButton()
        find_button.setIcon(QIcon('Images/find.png'))  # Replace 'path_to_find_icon.png' with the actual path to your image
        find_button.setToolTip("Find text")
        find_button.clicked.connect(self.find_clicked)

        # adding find action to menu and toolbar
        file_toolbar.addWidget(find_button)



        replace_button = QPushButton()
        replace_button.setIcon(QIcon('Images/replace.png'))
        replace_button.setToolTip("Replace Text")
        replace_button.clicked.connect(self.open_find_replace_dialog)
        file_toolbar.addWidget(replace_button)
        
        
        # Add a button to toggle highlighting of selected text
        highlight_button = QPushButton()
        highlight_button.setIcon(QIcon('Images/marker.png'))
        highlight_button.setToolTip("Highlighter")
        highlight_button.clicked.connect(self.toggle_highlight_selected_text)
        file_toolbar.addWidget(highlight_button)
    
        # calling update title method
        self.update_title()

        # Set window flag to keep window on top
        self.setWindowFlags(self.windowFlags())

        # showing all the components
        self.show()
        

    # creating dialog critical method
    # to show errors
    def dialog_critical(self, s):

        # creating a QMessageBox object
        dlg = QMessageBox(self)

        # setting text to the dlg
        dlg.setText(s)

        # setting icon to it
        dlg.setIcon(QMessageBox.Critical)

        # showing it
        dlg.show()

    # action for changing themes
    def change_theme(self, background_color, text_color):
        # Change background color of the main window
        self.setStyleSheet(f"background-color: {background_color};")

        # Change text color of menu bar
        self.menuBar().setStyleSheet(f"color: {text_color};")

        # Change text color of toolbars
        for toolbar in self.findChildren(QToolBar):
            toolbar.setStyleSheet(f"color: {text_color};")

        # Change text color of status bar
        self.statusBar().setStyleSheet(f"color: {text_color};")

        # Change text color of QTextEdit
        self.editor.setStyleSheet(f"color: {text_color};")
            


    # action called by file open action
    def file_open(self):

        # getting path and bool value
        path, _ = QFileDialog.getOpenFileName(self, "Open file", "", 
                            "Text documents (*.txt);All files (*.*)")

        # if path is true
        if path:
            # try opening path
            try:
                with open(path, 'r') as f:
                    # read the file
                    text = f.read()

            # if some error occurred
            except Exception as e:

                # show error using critical method
                self.dialog_critical(str(e))
            # else
            else:
                # update path value
                self.path = path

                # update the text
                self.editor.setPlainText(text)

                # update the title
                self.update_title()

    # action called by file new action
    def file_new(self):
        self.editor.clear()
        self.path = None
        self.update_title()

    # action called by file save action
    def file_save(self):

        # if there is no save path
        if self.path is None:

            # call save as method
            return self.file_saveas()

        # else call save to path method
        self._save_to_path(self.path)

    # action called by save as action
    def file_saveas(self):
        default_filename = "untitled.txt"

        # opening path
        path, _ = QFileDialog.getSaveFileName(self, "Save file", default_filename, 
                            "Text documents (*.txt);;All files (*.*)")

        # if dialog is cancelled i.e no path is selected
        if not path:
            # return this method
            # i.e no action performed
            return None
         

        # else call save to path method
        else:
            self._save_to_path(path)

    # save to path method
    def _save_to_path(self, path):

        # get the text
        text = self.editor.toPlainText()

        # try catch block
        try:

            # opening file to write
            with open(path, 'w') as f:
                # write text in the file
                f.write(text)

        # if error occurs
        except Exception as e:
            # show error using critical
            self.dialog_critical(str(e))
        # else do this
        else:
            # change path
            self.path = path
            # update the title
            self.update_title()

    # action called by print
    def file_print(self):

        # creating a QPrintDialog
        dlg = QPrintDialog()

        # if executed
        if dlg.exec_():

            # print the text
            self.editor.print_(dlg.printer())


    def closeEvent(self,event):
        if self.path is not None:  # If there is a file path
            with open(self.path, 'r') as f:
                current_content = f.read()  # Read the current content of the file

            if self.editor.toPlainText() != current_content:  # Check if current content is different from the file content
                msg = QMessageBox()
                msg.setText("You have unsaved changes. Save before closing?")
                msg.setWindowTitle("Warning!!!")
                # Load the image
                pixmap = QPixmap("Images/warning.png")
                # Resize the image to a new width and height
                new_width = 100  # Set your desired width
                new_height = 100  # Set your desired height
                resized_pixmap = pixmap.scaled(new_width, new_height)
                msg.setIconPixmap(resized_pixmap)
                msg.setStyleSheet("background-color: white;color: blue;")
                msg.addButton(QMessageBox.Save)
                msg.addButton(QMessageBox.Cancel)
                msg.addButton(QMessageBox.Discard)
                answer = msg.exec_()
            
                if answer == QMessageBox.Save:

                    saved_file = self.file_save()
                    if saved_file != None:                            
                        try:
                            driver.quit()
                        except:
                            pass
                        event.accept()
                    else:
                        event.ignore()
                elif answer == QMessageBox.Discard:
                    try:
                        driver.quit()
                    except:
                        pass
                    self.close()
                else:
                    event.ignore()
                # No need to handle the Cancel option separately, as the method will return if it's selected.
            else:
                try:
                    driver.quit()
                except:
                    pass
                self.close()
        else:
            if self.editor.document().isModified(): # Check if the editor is 
                
                msg = QMessageBox()
                msg.setText("You have unsaved changes. Save before closing?")
                msg.setWindowTitle("Warning!!!")
                # Load the image
                pixmap = QPixmap("Images/warning.png")
                # Resize the image to a new width and height
                new_width = 100  # Set your desired width
                new_height = 100  # Set your desired height
                resized_pixmap = pixmap.scaled(new_width, new_height)
                msg.setIconPixmap(resized_pixmap)
                msg.setStyleSheet("background-color: white;color: blue;")
                msg.addButton(QMessageBox.Save)
                msg.addButton(QMessageBox.Cancel)
                msg.addButton(QMessageBox.Discard)
                answer = msg.exec_()
            
                
                if answer == QMessageBox.Save:
                    saved_file = self.file_save()  # Save the file with a new name
                    if saved_file != None:
                        try:
                            driver.quit()
                        except:
                            pass
                        event.accept()
                    else:
                        event.ignore()
                elif answer == QMessageBox.Discard:    
                    try:
                        driver.quit()
                    except:
                        pass
                    self.close()
                else:
                    event.ignore()
                # No need to handle the Cancel option separately, as the method will return if it's selected.'''
            else:
                try:
                    driver.quit()
                except:
                    pass
                self.close() # Do nothing if there is no file path and the editor is empty

    
            
    # update title method
    def update_title(self):

        # setting window title with prefix as file name
        # suffix as PyQt5 Notepad
        self.setWindowTitle("%s - Indian Text Editor" %(os.path.basename(self.path) 
                                                if self.path else "Untitled"))

    # action called by edit toggle
    def edit_toggle_wrap(self):

        # chaining line wrap mode
        self.editor.setLineWrapMode(1 if self.editor.lineWrapMode() == 0 else 0 )

    # action called to toggle bold style for selected text
    def toggle_bold(self):
        # Get the current font
        font = self.editor.currentCharFormat()
        # Check if bold is already applied to the selected text
        is_bold = font.fontWeight() == QFont.Bold
        # Toggle bold style for selected text
        font.setFontWeight(QFont.Bold if not is_bold else QFont.Normal)
        # Apply the modified font to the selected text
        self.editor.mergeCurrentCharFormat(font)

    # action called to toggle italic style for selected text
    def toggle_italic(self):
        # Get the current font
        font = self.editor.currentCharFormat()
        # Check if italic is already applied to the selected text
        is_italic = font.fontItalic()
        # Toggle italic style for selected text
        font.setFontItalic(not is_italic)
        # Apply the modified font to the selected text
        self.editor.mergeCurrentCharFormat(font)


    # action called to toggle underline style for selected text
    def toggle_underline(self):
        # Get the current font
        font = self.editor.currentCharFormat()
        # Check if underline is already applied to the selected text
        is_underlined = font.fontUnderline()
        # Toggle underline style for selected text
        font.setFontUnderline(not is_underlined)
        # Apply the modified font to the selected text
        self.editor.mergeCurrentCharFormat(font)

    # Modify the change_font_family method in the MainWindow class
    font = "Arial"
    fontsize = "12"
    def change_font_family(self,font):
        fontsize = self.editor.currentFont().pointSize()
        font = self.editor.setCurrentFont(font)
        fontsize = self.editor.setFontPointSize(int(fontsize))		

    # Modify the change_font_size method in the MainWindow class
    def change_font_size(self, fontsize):
        fontsize = self.editor.setFontPointSize(int(fontsize))

    #Align Functions
    def Align_Left(self):
        self.editor.setAlignment(Qt.AlignLeft)

    def Align_Right(self):
        self.editor.setAlignment(Qt.AlignRight)
    
    def Align_Center(self):
        self.editor.setAlignment(Qt.AlignCenter)

    def Align_Justify(self):
        self.editor.setAlignment(Qt.AlignJustify)

    def change_text_color(self):
        color = QColorDialog.getColor(initial=self.text_color)
        if color.isValid():
            self.text_color = color
            self.editor.setTextColor(self.text_color)

    def toggle_highlight_selected_text(self):
        # Get the currently selected text
        selected_text = self.editor.textCursor().selectedText()

        if selected_text:
            # Get the current cursor
            cursor = self.editor.textCursor()

            # Check if the selected text is already highlighted
            fmt = cursor.charFormat()
            is_highlighted = fmt.background().color() == QColor("yellow")

            # Toggle highlighting
            if is_highlighted:
                # Remove highlighting
                fmt.setBackground(Qt.white)  # Set background to white to remove highlighting
            else:
                # Add highlighting
                fmt.setBackground(QColor("yellow"))

            # Apply the format to the selected text
            cursor.setCharFormat(fmt)

    # Function to find text

    def find_clicked(self):
        self.find_dialog = FindDialog(self)
        self.find_dialog.show()	

    # Replace Functionality
    def open_find_replace_dialog(self):
        dialog = FindReplaceDialog(self)
        dialog.exec_()
 
    def update_text(self):
        try:
            # Get the selected Sanscript language
            selected_language = self.language_combo.currentText()

            # Define a mapping of languages to Sanscript script
            language_mapping = {
				"Bengali": sanscript.BENGALI,
				"Devanagari": sanscript.DEVANAGARI,
				"Gujarati": sanscript.GUJARATI,
				"Gurumukhi":sanscript.GURMUKHI,
				"Grantha":sanscript.GRANTHA,
				"Kannada":sanscript.KANNADA,
				"Malyalam":sanscript.MALAYALAM,
				"Oriya":sanscript.ORIYA,
				"Tamil":sanscript.TAMIL,
				"Tamil_SUB":sanscript.TAMIL_SUB,
				"Tamil_SUP":sanscript.TAMIL_SUP,
				"Telgu":sanscript.TELUGU,
            }

            if selected_language == "English":
                return

            # Get the corresponding Sanscript script for the selected language
            trans_lang = language_mapping.get(selected_language)

            
            # Get the text
            cursor = self.editor.textCursor()
            cursor.movePosition(QTextCursor.PreviousCharacter, cursor.KeepAnchor,2)
            latest_word = cursor.selectedText()

            if latest_word:
                # Disconnect the textChanged signal temporarily
                self.editor.textChanged.disconnect(self.update_text)
                #Get the current font style and size
                char_format = cursor.charFormat()
                # Transliterate the latest word from Hinglish to the selected Sanscript language
                latest_word = sanscript.transliterate(latest_word,trans_lang,sanscript.ITRANS)
                new_word = sanscript.transliterate(latest_word, sanscript.ITRANS, trans_lang)
                cursor.removeSelectedText()
                cursor.insertText(new_word)

                #set font style and size
                new_cursor = self.editor.textCursor()
                new_cursor.setPosition(cursor.position()-len(new_word))
                new_cursor.setPosition(cursor.position(),QTextCursor.KeepAnchor)
                new_cursor.setCharFormat(char_format)

                # Reconnect the textChanged signal
                self.editor.textChanged.connect(self.update_text)

        except Exception as e:
            pass

    def recording(self):
        if self.microphone.isChecked():
            try:
                text = Listen("en-us")
                selected_language = self.language_combo.currentText()

                # Define a mapping of languages to Sanscript script
                language_mapping = {
				"Bengali": sanscript.BENGALI,
				"Devanagari": sanscript.DEVANAGARI,
				"Gujarati": sanscript.GUJARATI,
				"Gurumukhi":sanscript.GURMUKHI,
				"Grantha":sanscript.GRANTHA,
				"Kannada":sanscript.KANNADA,
				"Malyalam":sanscript.MALAYALAM,
				"Oriya":sanscript.ORIYA,
				"Tamil":sanscript.TAMIL,
				"Tamil_SUB":sanscript.TAMIL_SUB,
				"Tamil_SUP":sanscript.TAMIL_SUP,
				"Telgu":sanscript.TELUGU,
                }

                if selected_language == "English":
                    text = ' ' + text
                else:
                    trans_lang = language_mapping.get(selected_language)
                    
                    vowels = ['e', 'i', 'o', 'u','.','?',',','/','!','(',')','[',']','{','}','"',':','%']
                    words = text.lower().split()
                    modified_text = [' ']
                    for word in words:
                        if word[-1] not in vowels:
                            word += 'a'
                        modified_text.append(word)
                    text = ' '.join(modified_text)
                    text = sanscript.transliterate(text,sanscript.ITRANS,trans_lang)

                cursor = self.editor.textCursor()
                char_format = cursor.charFormat()
                position = cursor.position()                
                cursor.insertText(text)
                cursor.setPosition(position+len(text))     

                new_cursor = self.editor.textCursor()
                new_cursor.setPosition(cursor.position()-len(text))
                new_cursor.setPosition(cursor.position(),QTextCursor.KeepAnchor)
                new_cursor.setCharFormat(char_format)
                self.editor.textChanged.connect(self.update_text)

            except Exception as e:
                print(f"A error found: {e}")
            self.microphone.setChecked(False)
 

if __name__ == '__main__':

    # creating PyQt5 application
    app = QApplication(sys.argv)

    # setting application name
    app.setApplicationName("Indian Text Editor")

    # creating a main window object
    window = MainWindow()

    # loop
    app.exec_()
