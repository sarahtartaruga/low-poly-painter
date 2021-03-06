# Python Modules
import time
import numpy as np
from Tkinter import *
from PIL import ImageTk, Image
import tkMessageBox
import tkFileDialog
import os, errno
import colorpicker_modified as cp

# Local Modules
from store import save, load, savePath, loadPath, saveState
from export import exportDialog
from canvas.frame import CanvasFrame
from triangulate.frame import MaskFrame
from triangulate.frame import TriangulateFrame
from zoomTransformer import ZoomTransformer
from lowpolypainter.undoManager import UndoManager
from lowpolypainter.controlMode import ControlMode, Mode
from lowpolypainter.toolTip import CreateToolTip

ACTIVE_MODE_COLOR = "#DADADA"

class Window(object):
    """
    Window Class

    Description:
    Contains canvas and roots the application.
    """

    def __init__(self, inputimage):
        self.root = Tk()

        # Zoom
        self.zoom = ZoomTransformer()
        self.zoomlist = []

        # Image Path
        self.inputimage = inputimage

        # Control Modus
        self.controlMode = ControlMode(self)

        # Settings
        off_x = 0
        off_y = -100
        min_width = 800
        min_height = 400
        font1 = "-family {Heiti TC} -size 14 -weight normal -slant "  \
            "roman -underline 0 -overstrike 0"

        self.root.config(bg='#ffffff')
        self.root.resizable(True, False)
        self.root.title('Low Poly Painter')
        self.root.minsize(min_width, min_height)
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        dist_right = int(self.root.winfo_screenwidth()/2 - min_width/2 + off_x)
        dist_down = int(self.root.winfo_screenheight()/2 - min_height/2 + off_y)
        self.root.geometry("+{}+{}".format(dist_right, dist_down))

        # Frame
        self.frame = Frame(self.root, bg='#ffffff')
        self.frame.grid(sticky=N+S+W)
        self.frame.grid_rowconfigure(0, weight=0)
        self.frame.grid_rowconfigure(1, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_columnconfigure(1, weight=0)
        self.frame.grid_columnconfigure(2, weight=0)
        self.frame.grid_columnconfigure(3, weight=1)

        # Canvas Frame
        self.canvasFrameToggle = False
        self.canvasFrame = CanvasFrame(self, inputimage)
        self.canvasFrame.grid(row=1, column=1, sticky=NSEW, padx=10)
        self.frame.bind_all("<Control-p>", self.fun)

        # Toolbar Frame
        self.toolbarFrame = ToolbarFrame(self)
        self.toolbarFrame.grid(row=1, column=0, sticky=N+E+W)

        self.frame.bind_all("<MouseWheel>", self.mouse_wheel_wheel)
        self.frame.bind_all("<Button-4>", self.mouse_wheel_button)
        self.frame.bind_all("<Button-5>", self.mouse_wheel_button)

        self.frame.bind_all("<Control-z>", self.undo)
        self.frame.bind_all("<Control-y>", self.redo)
        self.frame.bind_all("<Control-s>", self.saveState)

        self.frame.bind_all("<KeyPress>", self.controlMode.changeModeKeyPress, add="+")

        #Title Frame
        self.titleFrame = Frame(self.frame, bg="white")
        space = Frame(self.titleFrame, width=400, height=20, bg="white")
        self.titleLabel = Label(self.titleFrame, text="Low Poly Painter", height=3, bg="white", anchor="se", font=font1)
        space.grid(row=0, column=0)
        self.titleLabel.grid(row=0, column=1)
        self.titleFrame.grid(row=0, column=1, sticky=S+N+E+W, pady=3)

        # Mask Frame
        self.maskFrame = MaskFrame(self, inputimage)

        # Detail Frame
        self.detailFrame = DetailFrame(self)
        self.detailFrame.grid(row=1, column=2, sticky=NSEW, padx=10)

        # Zoom and Toggle Frame
        self.zoomAndToggleFrame = ZoomAndToggleFrame(self)
        self.zoomAndToggleFrame.grid(row=2, column=1, sticky=N+E+S+W)

        # Space Frame for right padding
        spaceFrame1 = Frame(self.frame, bg="white")
        spaceFrame1.grid(row=0, column=3)

        # Space Frame for below padding
        spaceFrame2 =  Frame(self.frame, bg="white", height=65)
        spaceFrame2.grid(row=3, column=1)

        self.controlMode.reset()

        self.undoManager = UndoManager()

        self.saveName = None
        # default save directory
        defaultDirectory = "lowpolypainter/resources/stored_mesh_data/"
        try:
            os.makedirs(defaultDirectory)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

    def updateColor(self, event=None):
        self.detailFrame.updateColor()

    """ Control Mode"""
    # point mode
    def changeModeToP(self, event=None):
        self.toolbarFrame.buttonFrame.pointsButton.config(bg=ACTIVE_MODE_COLOR)
        self.toolbarFrame.buttonFrame.pointsAndLinesButton.config(bg="#ffffff")
        self.toolbarFrame.buttonFrame.splitLineButton.config(bg="#ffffff")
        self.detailFrame.colorpicker.pipetteFrame.config(bg="#ffffff")

    # point and line mode
    def changeModeToPAL(self, event=None):
        self.toolbarFrame.buttonFrame.pointsButton.config(bg="#ffffff")
        self.toolbarFrame.buttonFrame.pointsAndLinesButton.config(bg=ACTIVE_MODE_COLOR)
        self.toolbarFrame.buttonFrame.splitLineButton.config(bg="#ffffff")
        self.detailFrame.colorpicker.pipetteFrame.config(bg="#ffffff")

    # split line mode
    def changeModeToSL(self, event=None):
        self.toolbarFrame.buttonFrame.pointsButton.config(bg="#ffffff")
        self.toolbarFrame.buttonFrame.pointsAndLinesButton.config(bg="#ffffff")
        self.toolbarFrame.buttonFrame.splitLineButton.config(bg=ACTIVE_MODE_COLOR)
        self.detailFrame.colorpicker.pipetteFrame.config(bg="#ffffff")

    # pipette enabled mode
    def changeModeToPipette(self, event=None):
        self.toolbarFrame.buttonFrame.pointsButton.config(bg="#ffffff")
        self.toolbarFrame.buttonFrame.pointsAndLinesButton.config(bg="#ffffff")
        self.toolbarFrame.buttonFrame.splitLineButton.config(bg="#ffffff")
        self.detailFrame.colorpicker.pipetteFrame.config(bg=ACTIVE_MODE_COLOR)

    def changeModeToBucket(self, event=None):
        self.toolbarFrame.buttonFrame.pointsButton.config(bg="#ffffff")
        self.toolbarFrame.buttonFrame.pointsAndLinesButton.config(bg="#ffffff")
        self.toolbarFrame.buttonFrame.splitLineButton.config(bg="#ffffff")
        self.detailFrame.colorpicker.pipetteFrame.config(bg="#ffffff")
        self.detailFrame.colorpicker.okButton.config(bg=ACTIVE_MODE_COLOR)


    """ ZOOM """
    def mouse_wheel_button(self, event):
        if event.num == 4:
            self.mouse_wheel(120, event.x, event.y)
        elif event.num == 5:
            self.mouse_wheel(-120, event.x, event.y)

    def mouse_wheel_wheel(self, event):
        if event.delta <0:
            self.mouse_wheel(-120, event.x, event.y)
        else:
            self.mouse_wheel(120, event.x, event.y)

    def mouse_wheel(self, delta, x, y):

        #Bug: Resizing the window makes the zoom weird
        #TODO: insert the magic numbers of the canvas top right corner and update them when resizing

        # fixing window coordinates
        # (magic numbers for default window)
        x = x - 112
        y = y - 80


        # checking bounds
        if x < 0:
            x=0
        if y < 0:
            y=0
        if x>self.canvasFrame.image.size[0]:
            x = self.canvasFrame.image.size[0]
        if y>self.canvasFrame.image.size[1]:
            y = self.canvasFrame.image.size[1]

        #logging zoom
        if delta > 0:
            self.zoomlist.append(x)
            self.zoomlist.append(y)
        if delta < 0:
            if len(self.zoomlist)==0:
                return
            y = self.zoomlist.pop()
            x = self.zoomlist.pop()

        delta = 2**(delta * 0.001)
        self.zoom.ZoomAt(delta, [x, y])
        #self.canvasFrame.mesh.updatePositions()
        self.canvasFrame.canvas.scale("all", x, y, delta, delta)

        currentScale = self.zoom.CurrentScale()
        backgroundPosition = self.zoom.ToViewport([0,0])

        width, height = self.canvasFrame.image.size
        new_size = int(currentScale * width), int(currentScale * height)
        self.canvasFrame.background = ImageTk.PhotoImage(self.canvasFrame.image.resize(new_size))
        self.canvasFrame.canvas.delete(self.canvasFrame.backgroundId)
        self.canvasFrame.backgroundId = self.canvasFrame.canvas.create_image(
            backgroundPosition[0], backgroundPosition[1],
            image=self.canvasFrame.background, anchor=NW)
        self.canvasFrame.canvas.lower(self.canvasFrame.backgroundId)
        self.canvasFrame.mesh.updateSize()


    """ ACTIONS """
    def toggleEntryFocus(self):
        self.canvasFrame.focus = not self.canvasFrame.focus

    def toggleCanvasFrame(self, event=None):
        if self.canvasFrameToggle:
            self.canvasFrameToggle = False
            self.maskFrame.grid_remove()
            self.canvasFrame.grid(row=1, column=1, sticky=N+S+E+W)
        else:
            self.canvasFrameToggle = True
            self.canvasFrame.grid_remove()
            self.maskFrame.grid(row=1, column=1, sticky=N+S+E+W)

    def insert(self, event=None):
        defaultDirectory = "lowpolypainter/resources/stored_mesh_data/"
        file_path = tkFileDialog.askopenfilename(initialdir = defaultDirectory, filetypes=[("all files","*"), ("low poly painter","*.lpp"), ("portable pixmap","*.ppm"), ("JPEG","*.jpg")])
        if file_path != "":
            if file_path.endswith('.lpp'):
                name = file_path[file_path.rindex('/')+1:]
                content = loadPath(file_path)
                image = Image.fromarray(content[0])
                self.loadImage(image, name)
                self.canvasFrame.mesh.quickload(content[1])
                self.saveName = file_path
            else:
                self.saveName = None
                self.loadImagePath(file_path)

    def clear(self, event=None):
        self.undoManager.do(self)
        self.canvasFrame.clear()

    def export(self, event=None):
        exportDialog(self.canvasFrame.mesh, self.canvasFrame.width, self.canvasFrame.height)

    # currently unused
    def saveMeshData(self, event=None):
        save(self.canvasFrame.mesh.save(), self.inputimage)

    def loadMeshData(self, event=None):
        self.canvasFrame.mesh.load(load(self.inputimage))

    def saveMeshDataPath(self, path, event=None):
        savePath(self.canvasFrame.mesh.quicksave(), path)

    def loadMeshDataPath(self, path, event=None):
        self.canvasFrame.mesh.quickload(loadPath(path))

    def saveState(self, event=None):
        if self.saveName == None:
            self.saveStateAs()
        else:
            saveState(self.canvasFrame.mesh, self.canvasFrame.image, self.saveName)

    def saveStateAs(self, event=None):
        defaultDirectory = "lowpolypainter/resources/stored_mesh_data/"
        file_path = tkFileDialog.asksaveasfilename(initialdir = defaultDirectory, filetypes=[("low poly painter", "*.lpp")])
        if file_path != "":
            if not file_path.endswith('.lpp'):
                file_path += '.lpp'
            self.saveName = file_path
            self.saveState()


    # undoes the last change
    def undo(self, event=None):
        self.undoManager.undo(self)

    # redoes the last undo
    def redo(self, event=None):
        self.undoManager.redo(self)

    def border(self, step=0):
        self.undoManager.do(self)
        self.canvasFrame.border(step=step)

    def borderTriangulate(self, event=None):
        self.undoManager.do(self)
        self.canvasFrame.border(triangulate=True)

    def random(self, size=0):
        self.undoManager.do(self)
        self.canvasFrame.random(size=size)

    def triangulate(self, size=0):
        self.undoManager.do(self)
        if self.canvasFrameToggle:
            self.toggleCanvasFrame()
            self.maskFrame.canvas.delete("v")
            self.canvasFrame.triangulate(size, self.maskFrame.mask)
            self.maskFrame.mask = np.zeros([self.maskFrame.width, self.maskFrame.height], dtype=bool)
        else:
            self.canvasFrame.triangulate(size)

    def fun(self, event):
        self.canvasFrame.fun = not self.canvasFrame.fun
        if (self.canvasFrame.fun):
            self.canvasFrame.housePartyProtocol()

# TODO: check if necessary
    """ DETAIL VIEW """
    # def show_triangulate(self, event=None):
    #     self.detailFrame.selectedFrame.grid_forget()
    #     self.detailFrame.triangulateFrame.grid(row=0, column=1, sticky=N+E+S+W)
    #     self.detailFrame.selectedFrame = self.detailFrame.triangulateFrame

    def loadImagePath(self, path):
        name = path[path.rindex('/')+1:]
        # changes in window
        self.clear()
        self.inputimage = name
        self.undoManager.clear()
        # changes in canvas
        self.canvasFrame.insert(path, name)
        # changes in maskFrame
        self.maskFrame.insert(path, name)
        # changes in frame
        self.frame.update()

    def loadImage(self, image, name):
        # changes in window
        self.clear()
        self.inputimage = name
        self.undoManager.clear()
        # changes in canvas
        self.canvasFrame.insert(image, name)
        # changes in maskFrame
        self.maskFrame.insert(image, name)
        # changes in frame
        self.frame.update()


class ToolbarFrame(Frame):
    """
    Toolbar Frame Class

    Description:
    Contains tools and visual states of canvas
    """
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent.frame)
        self.parent = parent
        self.config(bg='#ffffff', width=47)
        self.grid_columnconfigure(0, weight=1)

        self.buttonFrame = ButtonFrame(self)
        self.buttonFrame.grid(row=0, sticky=N+E+S+W)

class ButtonFrame(Frame):
    """
    Button Frame Class

    Description:
    Contains two buttons for clearing and testing.
    """
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, background="white")

        spaceFrame = Frame(self, bg="black")
        spaceFrame.grid(row=0, column=0)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, minsize=100, weight=0)
        path = "lowpolypainter/resources/icons/"

        self.insertImg = ImageTk.PhotoImage(file=path + "open.png")
        self.exportImg = ImageTk.PhotoImage(file=path + "export.png")
        self.saveImg = ImageTk.PhotoImage(file=path + "save.png")

        self.deleteImg = ImageTk.PhotoImage(file=path + "delete.png")
        self.clearImg = ImageTk.PhotoImage(file=path + "clear.png")
        self.undoImg = ImageTk.PhotoImage(file=path + "undo.png")
        self.redoImg = ImageTk.PhotoImage(file=path + "redo.png")

        self.pointImg = ImageTk.PhotoImage(file=path + "point.png")
        self.point_and_lineImg = ImageTk.PhotoImage(file=path + "point_and_line.png")
        self.line_breakImg = ImageTk.PhotoImage(file=path + "line_break.png")

        options = {'activebackground':"#ffffff", 'activeforeground':"#000000", 'background':"#ffffff", 'borderwidth':"0", 'foreground':"#000000", 'relief':'flat', 'highlightbackground':'#ffffff', 'highlightcolor':'#ffffff', 'justify':'center'}
        font1 = "-family {Heiti TC} -size 10 -weight normal -slant "  \
                "roman -underline 0 -overstrike 0"

        # Insert Button
        self.insertButton = Label(self, image=self.insertImg, activebackground="#ffffff", activeforeground="#000000", background="#ffffff", borderwidth="0", width='36', height='30')
        self.insertButton.grid(row=0, column=1, sticky=N+E+S+W, pady=5)
        self.insertButton.bind("<Button-1>", parent.parent.insert)

        # Save Button
        self.saveButton = Menubutton(self, image=self.saveImg,  height='30', bd='0', direction='below', background="#ffffff", relief='flat', highlightthickness='1', highlightcolor='#ffffff')
        self.saveButton.grid(row=1, column=1, columnspan=2, sticky=N+E+S+W, pady=5)
        self.saveButton.menu =  Menu(self.saveButton, tearoff = 0)
        self.saveButton.menu.add('checkbutton', label="Save", command=parent.parent.saveState, font=font1)
        self.saveButton.menu.add('checkbutton', label="Save as ... ", command=parent.parent.saveStateAs, font=font1)
        self.saveButton.config(menu=self.saveButton.menu)

        # Export Button
        self.exportButton = Label(self, image=self.exportImg, **options)
        self.exportButton.grid(row=2, column=1, sticky=N+E+S+W, pady=5)
        self.exportButton.bind("<Button-1>", parent.parent.export)

        # Space1
        self.space1 = Frame(self, height=1, width=1, bg='#DADADA', borderwidth=0)
        self.space1.grid(row=3, column=1, sticky=N+E+S+W, padx=8, pady=15)

        # Clear Button
        self.clearButton = Label(self, image=self.clearImg, **options)
        self.clearButton.grid(row=4, column=1, sticky=N+E+S+W, pady=5)
        self.clearButton.bind("<Button-1>", parent.parent.clear)
        self.clearButton_ttp = CreateToolTip(self.clearButton,
                                             "Delete everything.")

        # Delete Button
        self.deleteButton = Label(self, image=self.deleteImg, **options)
        self.deleteButton.grid(row=5, column=1, sticky=N+E+S+W, pady=5)
        self.deleteButton.bind("<Button-1>", parent.parent.canvasFrame.deleteSelected)
        self.deleteButton_ttp = CreateToolTip(self.deleteButton,
                                             "Delete selected.\n"
                                             "Shortcut: DELETE")

        # Undo Button
        self.undoButton = Label(self, image=self.undoImg, **options)
        self.undoButton.grid(row=6, column=1, sticky=N+E+S+W, pady=5)
        self.undoButton.bind("<Button-1>", parent.parent.undo)

        # Redo Button
        self.redoButton = Label(self, image=self.redoImg, **options)
        self.redoButton.grid(row=7, column=1, sticky=N+E+S+W, pady=5)
        self.redoButton.bind("<Button-1>", parent.parent.redo)

        # Space2
        self.space2 = Frame(self, height=1,  bg='#DADADA', borderwidth=0)
        self.space2.grid(row=8, column=1, sticky=N+E+S+W, padx=8, pady=15)

        # Change to Points Mode
        self.pointsFrame = Frame(self, height='35', bg='white')
        self.pointsButton = Label(self.pointsFrame, image=self.pointImg, width=35, height=36, **options)
        self.pointsButton.pack()
        self.pointsFrame.grid(row=10, column=1, sticky=N+E+S+W, pady=5)
        def click_handler_point(event):
            parent.parent.controlMode.changeMode(Mode.POINT)
        self.pointsButton.bind("<Button-1>", click_handler_point)
        self.pointsButton_ttp = CreateToolTip(self.pointsButton, "Place single points without connecting "
                                                                 "to other points.\n"
                                                                 "Shortcut: Q")

        # Change to Points and Lines Mode
        self.pointsAndLinesFrame = Frame(self, height='35', bg='white')
        self.pointsAndLinesButton = Label(self.pointsAndLinesFrame, image=self.point_and_lineImg, width=35, height=36, **options)
        self.pointsAndLinesButton.pack()
        self.pointsAndLinesFrame.grid(row=11, column=1, sticky=N+E+S+W, pady=5)
        self.pointsAndLinesButton_ttp = CreateToolTip(self.pointsAndLinesButton,
                                                      "Place point that automtically connects to the "
                                                      "currently selectd point.\n"
                                                      "If the lines connect as a triangle, a face is created "
                                                      "and filled automatically.\n"
                                                      "Clicking other points selects them.\n"
                                                      "Shortcut: W")

        def click_handler_point_and_line(event):
            parent.parent.controlMode.changeMode(Mode.POINT_AND_LINE)
        self.pointsAndLinesButton.bind("<Button-1>", click_handler_point_and_line)

        # Change to Split Line Mode
        self.splitLineFrame = Frame(self, height='35', bg='white')
        self.splitLineButton = Label(self.splitLineFrame, image=self.line_breakImg, width=35, height=36, **options)
        self.splitLineButton.pack()
        self.splitLineFrame.grid(row=12, column=1, sticky=N+E+S+W, pady=5)
        def click_handler_split(event):
            parent.parent.controlMode.changeMode(Mode.CONNECT_OR_SPLIT)
        self.splitLineButton.bind("<Button-1>", click_handler_split)
        self.splitLineButton_ttp = CreateToolTip(self.splitLineButton,
                                                      "Connect selected to clicked point.\n"
                                                      "If the lines connect as a triangle, a face is created "
                                                      "and filled automatically.\n"
                                                      "Can also be used to split a line and create a point there.\n"
                                                      "Shortcut: E or Right-Click")


class DetailFrame(Frame):
    """
    Detail Frame Class

    Description:
    Contains details about current selected tool
    Contains the color picker tool by which face color can be updated
    """
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent.frame)
        self.parent = parent
        self.config(bg='#ffffff', width=5)
        font1 = "-family {Heiti TC} -size 12 -weight normal -slant "  \
            "roman -underline 0 -overstrike 0"

        self.grid_rowconfigure(1, weight=0, uniform="detailframe")
        self.grid_rowconfigure(3, weight=1, uniform="detailframe")

        self.colorpicker = cp.ColorPicker(self)
        self.middleLine = Frame(self, bg='#DADADA', height=1, width=50)
        self.triangulateFrame = TriangulateFrame(self)

        self.colorpicker.grid(row=0, column=1, sticky=N+E+S+W)
        self.middleLine.grid(row=1, column=0, columnspan=3, sticky=N+E+S+W, padx=10)
        self.triangulateFrame.grid(row=2, column=1, sticky=N+E+S+W)

    #Legacy content
    def updateFaceColor(self, newColor):
        if not self.parent.canvasFrame.selectedFace:
            tkMessageBox.showinfo("Error", "No face selected!")
        else:
            self.parent.canvasFrame.selectedFace.setColor(newColor)
            self.parent.canvasFrame.selectedFace.deselect()
            self.parent.canvasFrame.selectedFace.IsCustomColored = True
            self.parent.canvasFrame.selectedFace = None

class ZoomAndToggleFrame(Frame):
    """
    Zoom And Toggle Frame Class

    Description:
    Contains Zoom Frame and Toggle Frame
    """

    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent.frame)
        self.config(bg='#ffffff', height=1)
        self.parent=parent
        self.zoomFrame=ZoomFrame(self)
        self.toggleFrame=ToggleFrame(self)
        spaceFrame=Label(self, bg='#ffffff', width=8)
        self.grid_columnconfigure(0, weight=2, uniform="ZoomAndToggle")
        self.grid_columnconfigure(1, weight=2, uniform="ZoomAndToggle")
        self.grid_columnconfigure(2, weight=0, uniform="ZoomAndToggle")
        self.toggleFrame.grid(row=0, column=0, sticky=N+W)
        spaceFrame.grid(row=0, column=1, sticky=N+E+S+W)
        self.zoomFrame.grid(row=0, column=2, sticky=N+E+S+W)


class ZoomFrame(Frame):
    """
    Zoom Frame Class

    Description:
    Contains two Zoom Buttons
    """

    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent)
        self.config(bg='#ffffff')
        font1 = "-family {Heiti TC} -size 15 -weight normal -slant "  \
            "roman -underline 0 -overstrike 0"
        self.grid_columnconfigure(0, weight=1, uniform="zoomFrame")
        self.grid_columnconfigure(1, weight=0, uniform="zoomFrame")
        self.grid_columnconfigure(2, weight=0, uniform="zoomFrame")
        self.grid_columnconfigure(3, weight=1, uniform="zoomFrame")

        path = "lowpolypainter/resources/icons/"

        self.zoomPlusImg = ImageTk.PhotoImage(file=path + "plus.png")
        self.zoomMinusImg = ImageTk.PhotoImage(file=path + "minus.png")

        # zoom-in Button
        self.zoomInButton = Button(self, image=self.zoomPlusImg, command=lambda: parent.parent.mouse_wheel(120, 0, 0), relief="flat", background='#ffffff',font=font1, width=15, height=15)
        self.zoomInButton.grid(row=0, column=1, sticky=N+S+E+W,)

        # zoom-out Button
        self.zoomOutButton = Button(self, image=self.zoomMinusImg, command=lambda: parent.parent.mouse_wheel(-120, 0, 0), borderwidth=2, relief='flat', highlightthickness='1',background='#ffffff',font=font1, width=15, height=15)
        self.zoomOutButton.grid(row=0, column=2, padx=3)


class ToggleFrame(Frame):
    """
    Toogle Frame Class

    Descripton:
    Contains the Toggle Checkboxes
    """
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent)
        self.config(bg="#ffffff")
        font1 = "-family {Heiti TC} -size 10 -weight normal -slant "  \
            "roman -underline 0 -overstrike 0"

        # Checkbox for Vertices and Edges
        self.vertexCheckbox = Checkbutton(self, text="Vertices", command=parent.parent.canvasFrame.toggleVerts, activebackground="#ffffff", activeforeground="#000000", background="#ffffff", borderwidth=2, compound='none', font=font1, foreground='#5b5b5b')
        self.vertexCheckbox.grid(row=0, column=0, sticky=NSEW, padx=7)
        self.vertexCheckbox.select()

        # Checkbox for Vertices and Edges
        self.edgesCheckbox = Checkbutton(self, text="Edges", command=parent.parent.canvasFrame.toggleEdges, activebackground="#ffffff", activeforeground="#000000", background="#ffffff", borderwidth=2, compound='none', font=font1, foreground='#5b5b5b')
        self.edgesCheckbox.grid(row=0, column=1, sticky=NSEW)
        self.edgesCheckbox.select()

        # Checkbox for Faces
        self.facesCheckbox = Checkbutton(self, text="Faces", command=parent.parent.canvasFrame.toggleFaces, activebackground="#ffffff", activeforeground="#000000", background="#ffffff", borderwidth=2, compound='none', font=font1, foreground='#5b5b5b')
        self.facesCheckbox.grid(row=0, column=2, sticky=NSEW, padx=7)
        self.facesCheckbox.select()


# TODO: Move description to tags
"""
Place, select and move points and lines with the mouse.
A line to the next point will automatically be created, as long as CTRL is not pressed.
Faces are selected by simply clicking on them.
To connect two points with a line, or to split a line in two, hold the SHIFT button.
If a line creates one or more triangles, then they will be automatically added.
Delete selected objects with DEL.
Toggle the visibility of the vertices with UP.
Toggle the visibility of the edges with DOWN.
Toggle the visibility of the faces with SPACE.
"""
