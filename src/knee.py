import vtk
import time


def read_slc_file(filename):
    print("Reading SLC file")
    reader = vtk.vtkSTLReader()
    reader.SetFileName(filename)
    reader.Update()
    return reader


def main():
    start = time.perf_counter()
    stl_data = read_slc_file('vw_knee.slc')
    end = time.perf_counter()

    print(f"Reading SLC file in {end - start:0.4f} seconds")

    print("Create mapper")
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(stl_data.GetOutputPort())

    print("Create actor")
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.SetScale(0.1, 0.1, 0.1)
    actor.GetProperty().SetColor(0.5, 0.5, 0.5)
    actor.GetProperty().SetRepresentationToSurface()

    print("Create a rendering window and renderer")
    ren = vtk.vtkRenderer()
    ren.AddActor(actor)
    renWin = vtk.vtkRenderWindow()
    renWin.AddRenderer(ren)
    ren.SetBackground(1, 1, 1)

    print("Create a renderwindowinteractor")
    iren = vtk.vtkRenderWindowInteractor()
    iren.SetRenderWindow(renWin)

    print("Render")
    # Enable user interface interactor
    iren.Initialize()
    renWin.Render()
    iren.Start()


main()
