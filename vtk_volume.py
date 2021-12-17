import sys
import vtk
import os
import numpy as np 

# Window width and height
WIDTH=800
HEIGHT=800

def set_file_parameters(raw_reader, raw_file):
    # Set data type and dimensions depending on file imported
    raw_reader.SetDataByteOrderToLittleEndian()
    raw_reader.SetFileDimensionality(3)

    if raw_file == "case1_fMRI.raw":
      raw_reader.SetDataScalarTypeToUnsignedShort()
      raw_reader.SetDataExtent(0, 63, 0, 63, 0, 35)
    elif raw_file == "case1_fMRI_tMAP.raw":
      raw_reader.SetDataScalarTypeToFloat()
      raw_reader.SetDataExtent(0, 63, 0, 63, 0, 35)
    elif raw_file == "case1_DTI.raw":
      raw_reader.SetDataScalarTypeToUnsignedShort()
      raw_reader.SetDataExtent(0, 127, 0, 127, 0, 71)
    elif raw_file == "case1_T1_post.raw":
      raw_reader.SetDataScalarTypeToUnsignedShort()
      raw_reader.SetDataExtent(0, 511, 0, 511, 0, 175)
    elif raw_file == "case1_T1_post_tumormask.raw":
      raw_reader.SetDataScalarTypeToUnsignedChar()
      raw_reader.SetDataExtent(0, 43, 0, 42, 0, 18)
    elif raw_file == "case1_T1_pre_brainmask.raw":
      raw_reader.SetDataScalarTypeToUnsignedChar()
      raw_reader.SetDataExtent(0, 511, 0, 511, 0, 175)
    elif raw_file == "case1_T1_pre.raw":
      raw_reader.SetDataScalarTypeToUnsignedShort()
      raw_reader.SetDataExtent(0, 511, 0, 511, 0, 175)
    elif raw_file == "case1_FLAIR.raw":
      raw_reader.SetDataScalarTypeToUnsignedShort()
      raw_reader.SetDataExtent(0, 431, 0, 511, 0, 23) 
    elif raw_file == "case1_T2.raw":
      raw_reader.SetDataScalarTypeToUnsignedShort()
      raw_reader.SetDataExtent(0, 543, 0, 639, 0, 23) 
    elif raw_file == "case1_SWI.raw":
      raw_reader.SetDataScalarTypeToUnsignedShort()
      raw_reader.SetDataExtent(0, 191, 0, 255, 0, 59) 

def get_matrix(txt_file):
  matrix = np.loadtxt(txt_file, skiprows=1)
  matrix_array = np.reshape(matrix, (1, 16))
  return tuple(map(tuple, matrix_array))[0]

def create_volumemapper(reslice, image_data, renderer):
  if not isinstance(image_data, vtk.vtkImageData):
    raise TypeError("input has to be vtkImageData")

  smin, smax = image_data.GetScalarRange()

  # Create opacity transfer table at 20% ramp
  opacity_function = vtk.vtkPiecewiseFunction()
  opacity_function.AddPoint(smin, 0.0)
  opacity_function.AddPoint(4.0, 0.0)
  opacity_function.AddPoint(smax, 1.0)
  
  # Create colour transfer table: mapping scalar value to colour
  colour_function = vtk.vtkColorTransferFunction()
  # colour_function.AddRGBSegment(smin, 0.0, 0.0, 255, smax, 255, 1.0, 1.0)
  colour_function.AddRGBPoint(smin, 0.0, 0.0, 255)
  colour_function.AddRGBPoint((smin+smax)/2, 0.0, 0.0, 0)
  colour_function.AddRGBPoint(smax, 255, 1.0, 1.0)

  volume_property = vtk.vtkVolumeProperty()
  volume_property.SetColor(colour_function)
  volume_property.SetScalarOpacity(opacity_function)
  volume_property.SetInterpolationTypeToLinear()
  
  volume_mapper = vtk.vtkSmartVolumeMapper()
  volume_mapper.SetInputData(image_data)
  # volume_mapper.SetInputConnection(reslice.GetOutputPort())
  
  volume = vtk.vtkVolume() ;# note: not a vtkActor
  volume.SetMapper(volume_mapper)
  volume.SetProperty(volume_property)
  renderer.AddVolume(volume)

def main(argv):
    # if not os.path.exists(filename):
    #     sys.stderr.write("file '%s' not found\n" % filename)
    #     return 1

    # 1. Use vtkImage reader 
    # 2. Use vtkImageReslice
    # 3. Specify transform -> setResliceTransform -> setMatrix
    reader = vtk.vtkImageReader()

    reader.SetFileName("case1_T2.raw")
    set_file_parameters(reader, "case1_T2.raw")
    reader.Update()
    

    # Reshape matrix
    # reading txt file
    # matrix = get_matrix(argv[2])

    matrix = np.loadtxt("case1_T2.txt", skiprows=1)

    vtk_matrix = vtk.vtkMatrix4x4()
    for i in range(4):
      for j in range(4):
        vtk_matrix.SetElement(i, j, matrix[i, j])
    
    
    transform = vtk.vtkTransform()
    transform.SetMatrix(vtk_matrix)
    # transform = vtk.vtkPerspectiveTransform()
    # transform.SetMatrix(vtk_matrix)

    # SetResliceAxes can replace the SetResliceTransform(transform)
    reslice = vtk.vtkImageReslice()
    reslice.SetInputConnection(reader.GetOutputPort())
    reslice.SetResliceAxes(vtk_matrix)
    
    # reslice.SetResliceTransform(transform)

    # reslice.SetInformationInput(reader.GetOutput())

    print(reslice)

    ##########
    # reader2 = vtk.vtkImageReader()

    # reader2.SetFileName('case1_T1_post_tumormask.raw')
    # set_file_parameters(reader2, 'case1_T1_post_tumormask.raw')
    # reader2.Update()
    

    # # Reshape matrix
    # # reading txt file
    # matrix2 = np.loadtxt("case1_T2.txt", skiprows=1)

    # vtk_matrix2 = vtk.vtkMatrix4x4()
    # for i in range(4):
    #   for j in range(4):
    #     vtk_matrix2.SetElement(i, j, matrix2[i, j])

    # reslice2 = vtk.vtkImageReslice()
    # reslice2.SetInputConnection(reader2.GetOutputPort())
    # reslice2.SetResliceAxes(vtk_matrix2)
    ###########


    # Volume rendering
    ren = vtk.vtkRenderer()
    renWin = vtk.vtkRenderWindow()
    renWin.AddRenderer(ren)
    renWin.SetSize(WIDTH, HEIGHT)

     # create a renderwindowinteractor
    iren = vtk.vtkRenderWindowInteractor()
    iren.SetRenderWindow(renWin)

    # add a volume mapper
    data = reader.GetOutput()
    create_volumemapper(reslice, data, ren)

    # data2 = reader2.GetOutput()
    # create_volumemapper(data2, ren)

    iren.Initialize()
    iren.Start()


main(sys.argv)
