import vtk
import time

colors = vtk.vtkNamedColors()


def read_slc_file(filename):
    print("Reading SLC file")
    reader = vtk.vtkSLCReader()
    reader.SetFileName(filename)
    reader.Update()

    print(reader)
    return reader


def main():
    start = time.perf_counter()
    reader_slc_data = read_slc_file('vw_knee.slc')
    end = time.perf_counter()

    print(f"Reading SLC file in {end - start:0.4f} seconds")

    print("Create mapper")
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(reader_slc_data.GetOutputPort())

    contourFilter = vtk.vtkContourFilter()
    contourFilter.SetInputConnection(reader_slc_data.GetOutputPort())
    contourFilter.SetValue(0, 72.0)

    outliner = vtk.vtkOutlineFilter()
    outliner.SetInputConnection(reader_slc_data.GetOutputPort())
    outliner.Update()

    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(contourFilter.GetOutputPort())
    mapper.SetScalarVisibility(0)

    print("Create actor")
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)

    print("Create a rendering window and renderer")
    ren = vtk.vtkRenderer()
    ren_win = vtk.vtkRenderWindow()
    ren.AddActor(actor)
    ren_win.AddRenderer(ren)
    ren.SetBackground(colors.GetColor3d("pink_light"))

    print("Create a renderwindowinteractor")
    iren = vtk.vtkRenderWindowInteractor()
    iren.SetRenderWindow(ren_win)

    ren.GetActiveCamera().SetPosition(-382.606608, -3.308563, 223.475751)
    ren.GetActiveCamera().SetFocalPoint(77.311562, 72.821162, 100.000000)
    ren.GetActiveCamera().SetViewUp(0.235483, 0.137775, 0.962063)
    ren.GetActiveCamera().SetDistance(482.25171)
    ren.GetActiveCamera().SetClippingRange(27.933848, 677.669341)
    ren.GetActiveCamera().Roll(180.)
    ren.GetActiveCamera().Azimuth(180.)
    ren_win.Render()

    print("Render")
    # Enable user interface interactor
    iren.Initialize()
    ren_win.Render()
    iren.Start()


main()
