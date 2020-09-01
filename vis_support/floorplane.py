import vtk
import numpy as np


def build_plane(position, params, colour):
    """
    Generates floor plane using individual layered rectilinear grids   
    """
    x = np.arange(params[0], params[1], params[2])
    y = np.arange(params[0], params[1], params[2])
    z = np.arange(params[0], params[1], params[2])

    # Create a rectilinear grid by defining three arrays specifying the
    # coordinates in the x-y-z directions.
    x_coords = vtk.vtkFloatArray()
    for i in x:
        x_coords.InsertNextValue(i)
    
    y_coords = vtk.vtkFloatArray()
    for i in y:
        y_coords.InsertNextValue(i)
        
    z_coords = vtk.vtkFloatArray()
    for i in z:
        z_coords.InsertNextValue(i)
    
    # The coordinates are assigned to the rectilinear grid. Make sure that
    # the number of values in each of the XCoordinates, YCoordinates,
    # and ZCoordinates is equal to what is defined in SetDimensions().
    rgrid = vtk.vtkRectilinearGrid()
    rgrid.SetDimensions(len(x), len(y), len(z))
    rgrid.SetXCoordinates(x_coords)
    rgrid.SetYCoordinates(y_coords)
    rgrid.SetZCoordinates(z_coords)
    
    # Extract a plane from the grid
    plane = vtk.vtkRectilinearGridGeometryFilter()
    plane.SetInputData(rgrid)
    plane.SetExtent(0, 46, 0, 46, 0, 0)

    rgrid_mapper = vtk.vtkPolyDataMapper()
    rgrid_mapper.SetInputConnection(plane.GetOutputPort())
    
    wire_actor = vtk.vtkActor()
    wire_actor.SetMapper(rgrid_mapper)
    wire_actor.GetProperty().SetRepresentationToWireframe()
    wire_actor.GetProperty().SetColor(colour)
    wire_actor.SetOrientation(0, 0, 90)
    wire_actor.GetProperty().LightingOff()
    wire_actor.SetPosition(3000, -2000, position)
    
    return wire_actor
