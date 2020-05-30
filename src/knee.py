import vtk
import time

#All color skin/bone and step background
colors = vtk.vtkNamedColors()
colors.SetColor("SkinColor", [201, 148, 150, 255])
colors.SetColor("BoneColor", [222, 222, 222, 255])
colors.SetColor("sphere", [255, 255, 200, 255])
colors.SetColor("background_step1", [255, 203, 205, 255])
colors.SetColor("background_step2", [203, 254, 205, 255])
colors.SetColor("background_step3", [205, 203, 255, 255])
colors.SetColor("background_step4", [205, 203, 205, 255])


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

    return mapper, contour_filter


def make_camera():
    cam = vtk.vtkCamera()
    cam.SetPosition(0, 1, 0)
    cam.SetViewUp(0, 0, 1)
    cam.Roll(180.)
    cam.Azimuth(90.)  # TODO 180

    return cam


def get_renderer(actors_list, bg_color, cam):
    ren = vtk.vtkRenderer()

    for ac in actors_list:
        ren.AddActor(ac)

    ren.SetBackground(bg_color)

    ren.SetActiveCamera(cam)
    ren.ResetCamera()

    return ren


def actors_step_1(contour_filter_leg):
    # Step 1
    plane = vtk.vtkPlane()
    plane.SetOrigin(0, 0, 0)
    plane.SetNormal(0, 0, 1)

    cutter = vtk.vtkCutter()
    cutter.SetCutFunction(plane)
    cutter.GenerateValues(21, 0, 207)
    cutter.SetInputConnection(contour_filter_leg.GetOutputPort())
    cutter.Update()

    stripper = vtk.vtkStripper()
    stripper.SetInputConnection(cutter.GetOutputPort())
    stripper.Update()

    tube_filter = vtk.vtkTubeFilter()
    tube_filter.SetInputConnection(stripper.GetOutputPort())
    tube_filter.SetRadius(1)
    tube_filter.Update()

    mapper_tube = vtk.vtkPolyDataMapper()
    mapper_tube.ScalarVisibilityOff()
    mapper_tube.SetInputConnection(tube_filter.GetOutputPort())

    actor_tube = vtk.vtkActor()
    actor_tube.SetMapper(mapper_tube)
    actor_tube.GetProperty().SetColor(colors.GetColor3d("SkinColor"))

    # End step 1
    return [actor_tube]

def clipping_skin_with_sphere(contour_filter_leg):
    sphere = vtk.vtkSphere()
    sphere.SetRadius(50)
    sphere.SetCenter(75, 35, 110)

    clipper = vtk.vtkClipPolyData()
    clipper.SetInputConnection(contour_filter_leg.GetOutputPort())
    clipper.SetClipFunction(sphere)
    clipper.SetValue(0)
    clipper.Update()

    mapper = vtk.vtkDataSetMapper()
    mapper.SetInputData(clipper.GetOutput())
    mapper.ScalarVisibilityOff()

    actor = vtk.vtkActor()
    actor.GetProperty().SetColor(colors.GetColor3d("SkinColor"))
    actor.SetMapper(mapper)

    return actor, sphere


def actors_step_2(contour_filter_leg):
    # Clipping the knee skin with a sphere
    actor_leg, _ = clipping_skin_with_sphere(contour_filter_leg)


    # transparency and backface property
    prop = vtk.vtkProperty()
    prop.SetColor(colors.GetColor3d("SkinColor"))

    actor_leg.GetProperty().SetOpacity(0.666)
    actor_leg.SetBackfaceProperty(prop)

    return [actor_leg]


def actors_step_3(contour_filter_leg):
    # Clipping the knee skin with a sphere
    actor_leg, sphere = clipping_skin_with_sphere(contour_filter_leg)

    sample = vtk.vtkSampleFunction()
    sample.SetImplicitFunction(sphere)
    sample.SetModelBounds(-200.5, 200.5, -200.5, 200.5, -200.5, 200.5)
    sample.SetSampleDimensions(200, 200, 200)
    sample.ComputeNormalsOff()

    contour_filter = vtk.vtkContourFilter()
    contour_filter.SetInputConnection(sample.GetOutputPort())
    contour_filter.SetValue(0, 0.0)

    mapper = vtk.vtkDataSetMapper()
    mapper.SetInputConnection(contour_filter.GetOutputPort())
    mapper.ScalarVisibilityOff()

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(colors.GetColor3d("sphere"))
    actor.GetProperty().SetOpacity(0.4)

    return [actor_leg, actor]


def main():
    start = time.perf_counter()
    reader_slc_data = read_slc_file('vw_knee.slc')
    end = time.perf_counter()

    print(f"Reading SLC file in {end - start:0.4f} seconds")

    print("Create mapper")

    outline = vtk.vtkOutlineFilter()
    outline.SetInputConnection(reader_slc_data.GetOutputPort())

    mapper_bone, _ = get_mapper(reader_slc_data, 72.0)
    mapper_leg, contour_filter_leg = get_mapper(reader_slc_data, 52.0)

    mapper_outline = vtk.vtkPolyDataMapper()
    mapper_outline.SetInputConnection(outline.GetOutputPort())

    print("Create actor")
    actor_bone = vtk.vtkActor()
    actor_bone.GetProperty().SetColor(colors.GetColor3d("BoneColor"))
    actor_leg = vtk.vtkActor()
    # Step 2

    actor_outline = vtk.vtkActor()
    actor_outline.SetMapper(mapper_outline)
    actor_outline.GetProperty().SetColor(colors.GetColor3d("ivory_black"))

    # actor_leg.GetProperty().SetColor(colors.GetColor3d("pink_light"))

    actor_bone.SetMapper(mapper_bone)
    actor_leg.SetMapper(mapper_leg)

    print("Create a 4 renderers")

    actors_list = [actor_bone,  actor_outline]

    cam = make_camera()

    ren_1 = get_renderer(actors_list + actors_step_1(contour_filter_leg), colors.GetColor3d("background_step1"), cam)
    ren_2 = get_renderer(actors_list + actors_step_2(contour_filter_leg), colors.GetColor3d("background_step2"), cam)
    ren_3 = get_renderer(actors_list + actors_step_3(contour_filter_leg), colors.GetColor3d("background_step3"), cam)
    ren_4 = get_renderer(actors_list, colors.GetColor3d("background_step4"), cam)

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
