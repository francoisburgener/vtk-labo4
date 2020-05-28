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


def get_mapper(reader_slc_data, counter_value):
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(reader_slc_data.GetOutputPort())

    contour_filter = vtk.vtkContourFilter()
    contour_filter.SetInputConnection(reader_slc_data.GetOutputPort())
    contour_filter.SetValue(0, counter_value)

    outliner = vtk.vtkOutlineFilter()
    outliner.SetInputConnection(reader_slc_data.GetOutputPort())
    outliner.Update()

    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(contour_filter.GetOutputPort())
    mapper.SetScalarVisibility(0)

    return mapper


def get_renderer(actor_bone, actor_leg, actor_outline, bg_color):
    ren = vtk.vtkRenderer()
    ren.AddActor(actor_bone)
    ren.AddActor(actor_leg)
    ren.AddActor(actor_outline)
    ren.SetBackground(bg_color)

    ren.GetActiveCamera().SetPosition(-382.606608, -3.308563, 223.475751)
    ren.GetActiveCamera().SetFocalPoint(77.311562, 72.821162, 100.000000)
    ren.GetActiveCamera().SetViewUp(0.235483, 0.137775, 0.962063)
    ren.GetActiveCamera().SetDistance(482.25171)
    ren.GetActiveCamera().SetClippingRange(27.933848, 677.669341)
    ren.GetActiveCamera().Roll(180.)
    ren.GetActiveCamera().Azimuth(180.)

    return ren


def main():
    start = time.perf_counter()
    reader_slc_data = read_slc_file('vw_knee.slc')
    end = time.perf_counter()

    print(f"Reading SLC file in {end - start:0.4f} seconds")

    print("Create mapper")

    outline = vtk.vtkOutlineFilter()
    outline.SetInputConnection(reader_slc_data.GetOutputPort())

    mapper_bone = get_mapper(reader_slc_data, 72.0)
    mapper_leg = get_mapper(reader_slc_data, 52.0)

    mapper_outline = vtk.vtkPolyDataMapper()
    mapper_outline.SetInputConnection(outline.GetOutputPort())

    print("Create actor")
    actor_bone = vtk.vtkActor()
    actor_leg = vtk.vtkActor()

    actor_outline = vtk.vtkActor()
    actor_outline.SetMapper(mapper_outline)
    actor_outline.GetProperty().SetColor(colors.GetColor3d("ivory_black"))

    actor_leg.GetProperty().SetColor(colors.GetColor3d("pink_light"))

    actor_bone.SetMapper(mapper_bone)
    actor_leg.SetMapper(mapper_leg)

    print("Create a 4 renderers")

    ren_1 = get_renderer(actor_bone, actor_leg, actor_outline, colors.GetColor3d("pink_light"))
    ren_2 = get_renderer(actor_bone, actor_leg, actor_outline, colors.GetColor3d("green_pale"))
    ren_3 = get_renderer(actor_bone, actor_leg, actor_outline, colors.GetColor3d("plum"))
    ren_4 = get_renderer(actor_bone, actor_leg, actor_outline, colors.GetColor3d("light_grey"))

    top_left = (0, 0.5, 0.5, 1)
    top_right = (0.5, 0.5, 1, 1)
    bottom_left = (0, 0, 0.5, 0.5)
    bottom_right = (0.5, 0, 1, 0.5)

    ren_1.SetViewport(top_left)
    ren_2.SetViewport(top_right)
    ren_3.SetViewport(bottom_left)
    ren_4.SetViewport(bottom_right)

    ren_win = vtk.vtkRenderWindow()
    ren_win.AddRenderer(ren_1)
    ren_win.AddRenderer(ren_2)
    ren_win.AddRenderer(ren_3)
    ren_win.AddRenderer(ren_4)
    ren_win.SetSize(800, 800)

    print("Create a renderwindowinteractor")
    # Mouse move
    render_wind_interactor = vtk.vtkRenderWindowInteractor()
    render_wind_interactor.SetRenderWindow(ren_win)

    ren_win.Render()

    print("Render")
    # Enable user interface interactor
    render_wind_interactor.Initialize()
    ren_win.Render()
    render_wind_interactor.Start()


main()
