import sys
import vtk
import os
import numpy as np 

# Window width and height
WIDTH=800
HEIGHT=800

def create_volumemapper(image_data, renderer):
  if not isinstance(image_data, vtk.vtkImageData):
    raise TypeError("input has to be vtkImageData")

  smin, smax = image_data.GetScalarRange()

  # Create opacity transfer table at 20% ramp
  opacity_function = vtk.vtkPiecewiseFunction()
  opacity_function.AddPoint(smin, 0.0)
  opacity_function.AddPoint(smax, 0.2)
  
  # Create colour transfer table: mapping scalar value to colour
  colour_function = vtk.vtkColorTransferFunction()
  colour_function.AddRGBPoint(smin, 0.0, 0.0, 0.0)
  colour_function.AddRGBPoint(smax, 1.0, 1.0, 1.0)
  # or, in case of HSV:
  #colour_function.SetColorSpaceToHSV()
  #colour_function.AddHSVPoint(smin, 0.0, 0.0, 0.0)
  #colour_function.AddHSVPoint(smax, 0.0, 0.0, 1.0)

  volume_property = vtk.vtkVolumeProperty()
  volume_property.SetColor(colour_function)
  volume_property.SetScalarOpacity(opacity_function)
  volume_property.ShadeOn() ;# adds shading, but will introduce artefacts (and CPU/GPU load)
  volume_property.SetInterpolationTypeToLinear()
  
  volume_mapper = vtk.vtkSmartVolumeMapper()
  volume_mapper.SetInputData(image_data)
  
  volume = vtk.vtkVolume() ;# note: not a vtkActor
  volume.SetMapper(volume_mapper)
  volume.SetProperty(volume_property)
  renderer.AddVolume(volume)

def main(argv):
    filename = argv[1]

    if not os.path.exists(filename):
        sys.stderr.write("file '%s' not found\n" % filename)
        return 1

    # 1. Use vtkImage reader 
    # 2. Use vtkImageReslice
    # 3. Specify transform -> setResliceTransform -> setMatrix
    reader = vtk.vtkImageReader2()
    
    reader.SetDataScalarTypeToFloat()
    reader.SetFileDimensionality(3)
    reader.SetDataExtent(0,0,0, 63, 63, 35)

    # Reshape matrix
    # reading txt file
    matrix = np.loadtxt(argv[2], skiprows=1)
    matrix_array = np.reshape(matrix, (1, 16))
    matrix_tuple = tuple(map(tuple, matrix_array))

    transform = vtk.vtkTransform()
    transform.SetMatrix(matrix_tuple[0])

    reslice = vtk.vtkImageReslice()
    reslice.SetInputConnection(reader.GetOutputPort())
    reslice.SetResliceTransform(transform)

    reader.SetFileName(filename)
    reader.Update()
    

    ren = vtk.vtkRenderer()
    renWin = vtk.vtkRenderWindow()
    renWin.AddRenderer(ren)
    renWin.SetSize(WIDTH, HEIGHT)

     # create a renderwindowinteractor
    iren = vtk.vtkRenderWindowInteractor()
    iren.SetRenderWindow(renWin)

    # add a volume mapper
    data = reader.GetOutput()
    create_volumemapper(data, ren)

    iren.Initialize()
    iren.Start()


main(sys.argv)
