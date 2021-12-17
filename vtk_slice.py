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
  matrix = np.transpose(matrix)
  matrix_array = np.reshape(matrix, (1, 16))
  return tuple(map(tuple, matrix_array))[0]

def create_slicemapper(image_data, outputport, renderer):
  if not isinstance(image_data, vtk.vtkImageData):
    raise TypeError("input has to be vtkImageData")

  smin, smax = image_data.GetScalarRange()

  colour_function= vtk.vtkColorTransferFunction()
  colour_function.SetRange(smin, smax)
  colour_function.SetNanColorRGBA(1.0, 1.0, 0.0, 1.0)
  colour_function.AddRGBPoint(smin, 0.0, 0.0, 1.0)
  # colour_function.AddRGBPoint((smin+smax)/2, 0.0, 0.0, 0)
  colour_function.AddRGBPoint(smax, 1.0, 0.0, 0.0)

  
  slice_property = vtk.vtkImageProperty()
  # slice_property.SetColorWindow(smax - smin)
  # slice_property.SetColorLevel((smax + smin) / 2.0)
  slice_property.SetLookupTable(colour_function)
  slice_property.SetInterpolationTypeToLinear()
  
  slice_mapper = vtk.vtkImageSliceMapper()
  slice_mapper.SliceAtFocalPointOn()
  slice_mapper.SliceFacesCameraOn()
  slice_mapper.SetInputConnection(outputport)
  
  slice = vtk.vtkImageSlice() ;# note: not a vtkActor
  slice.SetMapper(slice_mapper)
  slice.SetProperty(slice_property)
  renderer.AddViewProp(slice)
  # renderer.SetViewport(0.5,0.5,1.0,1.0)

def main(argv):
    # if not os.path.exists(filename):
    #     sys.stderr.write("file '%s' not found\n" % filename)
    #     return 1

    # 1. Use vtkImage reader 
    # 2. Use vtkImageReslice
    # 3. Specify transform -> setResliceTransform -> setMatrix

    reader = vtk.vtkImageReader()

    reader.SetFileName('case1_T1_post.raw')
    set_file_parameters(reader, 'case1_T1_post.raw')
    reader.Update()
    

    # Reshape matrix
    # reading txt file
    matrix = get_matrix('case1_T1_post.txt')

    transform = vtk.vtkTransform()
    transform.SetMatrix(matrix)

    reslice = vtk.vtkImageReslice()
    reslice.SetInputConnection(reader.GetOutputPort())
    reslice.SetResliceTransform(transform)

    ##########
    reader2 = vtk.vtkImageReader()

    reader2.SetFileName('case1_T1_post_tumormask.raw')
    set_file_parameters(reader2, 'case1_T1_post_tumormask.raw')
    reader2.Update()
    

    # Reshape matrix
    # reading txt file
    matrix2 = get_matrix('case1_T1_post_tumormask.txt')

    transform2 = vtk.vtkTransform()
    transform2.SetMatrix(matrix2)

    reslice2 = vtk.vtkImageReslice()
    reslice2.SetInputConnection(reader2.GetOutputPort())
    reslice2.SetResliceTransform(transform2)
    ###########


    # Volume rendering
    ren1 = vtk.vtkRenderer()
    
    

    
    # add a slice mapper
    data = reader.GetOutput()
    port = reader.GetOutputPort()
    create_slicemapper(data, port, ren1)

    # ren2 = vtk.vtkRenderer()
    data2 = reader2.GetOutput()
    port2 = reader2.GetOutputPort()
    create_slicemapper(data2, port2, ren1)


    renWin = vtk.vtkRenderWindow()
    renWin.AddRenderer(ren1)
    # renWin.AddRenderer(ren2)
    renWin.SetSize(WIDTH, HEIGHT)

    # create a renderwindowinteractor
    iren = vtk.vtkRenderWindowInteractor()
    iren.SetRenderWindow(renWin)

    iren.Initialize()
    iren.Start()


main(sys.argv)
