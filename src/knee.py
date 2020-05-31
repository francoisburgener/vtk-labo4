import os
import time
import vtk

# All color skin/bone and step background
colors = vtk.vtkNamedColors()
colors.SetColor("SkinColor", [201, 148, 150, 255])
colors.SetColor("BoneColor", [222, 222, 222, 255])
colors.SetColor("sphere", [255, 255, 200, 255])
colors.SetColor("background_step1", [255, 203, 205, 255])
colors.SetColor("background_step2", [203, 254, 205, 255])
colors.SetColor("background_step3", [205, 203, 255, 255])
colors.SetColor("background_step4", [205, 203, 205, 255])

FILENAME_STEP_4 = "step4.vtk"


def read_slc_file(filename):
    print("Reading SLC file")
    reader = vtk.vtkSLCReader()
    reader.SetFileName(filename)
    reader.Update()

    return reader


def writer_vtk(filename, data):
    """
    Util function to create a vtk file
    :param filename: the name of the file
    :param data: A Polydata you wish to write
    :return: void
    """
    writer = vtk.vtkDataSetWriter()
    writer.SetFileName(filename)
    writer.SetInputData(data)
    writer.Write()


def reader_vtk(filename):
    """
    Util function to read from a vtk file
    :param filename: the name of the file
    :return: a poly data object
    """
    reader = vtk.vtkPolyDataReader()
    reader.SetFileName(filename)
    reader.Update()
    return reader


def get_mapper(reader_slc_data, counter_value):
    """
    Gets the mapper object from an SLC Data
    Example: 72.0 works to get the bone, 50~ish for the leg
    :param reader_slc_data: The data
    :param counter_value: The layer to extract from
    :return: A Mapper object
    """
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
    """
    Creates a camera object
    :return: A camera object
    """
    cam = vtk.vtkCamera()
    cam.SetPosition(0, 1, 0)
    cam.SetViewUp(0, 0, 1)
    cam.Roll(180.)
    cam.Azimuth(180.)

    return cam


def get_renderer(actors_list, bg_color, cam):
    """
    Makes a renderer object from an actor list
    :param actors_list: The list of actors you wish to display
    :param bg_color: The background of the scene
    :param cam: the camera object to use
    :return: A renderer object
    """
    ren = vtk.vtkRenderer()

    for ac in actors_list:
        ren.AddActor(ac)

    ren.SetBackground(bg_color)

    ren.SetActiveCamera(cam)
    ren.ResetCamera()

    return ren


def actors_step_1(contour_filter_leg):
    """
    Creates the visualization actors for step 1
    :param contour_filter_leg: The data SLC from the leg
    :return: A list with the tube actor
    """
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
    """
    Makes an actor for the leg which cuts it using a clipper
    The goal here is to make a boolean difference between
    the leg and a sphere placed on the knee area.
    :param contour_filter_leg: The raw SLC data for the leg
    :return: Leg cut actor, and the sphere
    """
    sphere = vtk.vtkSphere()
    sphere.SetRadius(50)
    sphere.SetCenter(75, 40, 110)

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
    """
    Creates the visualization actors for step 2
    :param contour_filter_leg: The data SLC from the leg
    :return: A list with the leg actor
    """
    # Clipping the knee skin with a sphere
    actor_leg, _ = clipping_skin_with_sphere(contour_filter_leg)

    # transparency and backface property
    prop = vtk.vtkProperty()
    prop.SetColor(colors.GetColor3d("SkinColor"))

    actor_leg.GetProperty().SetOpacity(0.666)
    actor_leg.SetBackfaceProperty(prop)

    return [actor_leg]


def actors_step_3(contour_filter_leg):
    """
    Creates the visualization actors for step 3
    :param contour_filter_leg: The data SLC from the leg
    :return: The leg actor and the sphere actor
    """
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


def actors_step_4(mapper_bone, mapper_leg):
    """
    Creates the visualization actors for step 4
    :param mapper_bone: The Mapper of the bone
    :param mapper_leg: The Mapper of the leg
    :return: The list with the distance bone actor
    """
    print('start step 4')
    start = time.perf_counter()

    if not os.path.isfile(FILENAME_STEP_4):
        distance_filter = vtk.vtkDistancePolyDataFilter()
        distance_filter.SetInputData(0, mapper_bone.GetInput())
        distance_filter.SetInputData(1, mapper_leg.GetInput())
        distance_filter.SignedDistanceOff()
        distance_filter.Update()

        writer_vtk(FILENAME_STEP_4, distance_filter.GetOutput())

    reader = reader_vtk(FILENAME_STEP_4)

    end = time.perf_counter()
    print(f"End of step 4 in: {end - start:0.4f} seconds")

    mapper_distance = vtk.vtkPolyDataMapper()
    mapper_distance.SetInputData(reader.GetOutput())
    mapper_distance.SetScalarRange(reader.GetOutput().GetPointData().GetScalars().GetRange())
    
    actor_distance = vtk.vtkActor()
    actor_distance.SetMapper(mapper_distance)

    return [actor_distance]


def main():
    """
    The main function
    :return: void
    """

    start = time.perf_counter()
    reader_slc_data = read_slc_file('vw_knee.slc')
    end = time.perf_counter()

    print(f"Reading SLC file in {end - start:0.4f} seconds")

    print("Create mapper")

    outline = vtk.vtkOutlineFilter()
    outline.SetInputConnection(reader_slc_data.GetOutputPort())

    mapper_bone, _ = get_mapper(reader_slc_data, 72.0)
    mapper_leg, contour_filter_leg = get_mapper(reader_slc_data, 47.0)

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
    ren_4 = get_renderer([actor_outline] + actors_step_4(mapper_bone, mapper_leg), colors.GetColor3d("background_step4"), cam)

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

    print("Render")
    ren_win.Render()

    # Little animation at start
    for i in range(0, 360):
        time.sleep(0.05)
        cam.Azimuth(1)
        ren_win.Render()

    # Enable user interface interactor
    render_wind_interactor.Initialize()
    ren_win.Render()
    render_wind_interactor.Start()


main()
