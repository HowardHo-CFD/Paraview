from paraview.simple import *
import os

# Case identifiers
case_series = ['a', 'b', 'c']
case_numbers = ['1', '2', '3']
all_cases = [f"{s}-{n}" for s in case_series for n in case_numbers]

# Time range for screenshots
t_min = 0.35
t_max = 0.355

# Paths
input_base_dir = "."                   # current directory
output_base_dir = "uy-contours"       # save screenshots here

# Loop over each case
for case_name in all_cases:
    ResetSession()
    from paraview.simple import *

    # Path to .foam file: ./a-1/a-1.foam
    foam_path = os.path.join(case_name, f"{case_name}.foam")
    if not os.path.exists(foam_path):
        print(f"[WARNING] Missing .foam file: {foam_path}")
        continue

    # Load the PVSM file (assumes it references some initial foam file)
    LoadState("paraview-scripts/uy-contour-po-1.pvsm")

    # Swap in the correct .foam file
    for _, proxy in GetSources().items():
        if hasattr(proxy, 'FileName'):
            proxy.FileName = foam_path
            proxy.UpdatePipeline()

    # Get the correct view
    renderView3 = FindViewOrCreate('RenderView3', viewtype='RenderView')
    SetActiveView(renderView3)

    # Find source and color map
    contour1 = FindSource('Contour1')
    SetActiveSource(contour1)

    u_YLUT = GetColorTransferFunction('U_Y')
    u_YPWF = GetOpacityTransferFunction('U_Y')
    u_YTF2D = GetTransferFunction2D('U_Y')
    contour1Display = GetDisplayProperties(contour1, view=renderView3)

    # Set layout preview mode
    layout3 = GetLayout()
    layout3.PreviewMode = [0, 0]         # Exit preview
    layout3.PreviewMode = [1280, 800]    # Enter preview
    layout3.SetSize(1280, 800)
    Render()

    # Set interaction mode and camera
    renderView3.InteractionMode = '2D'
    renderView3.CameraPosition = [-0.8847254191111265, 0.8423471309524623, 1.0939458705211629]
    renderView3.CameraFocalPoint = [0.021901547650443776, 0.024829524005463156, 0.00956757099151584]
    renderView3.CameraViewUp = [0.3226123621152194, 0.8656363101509489, -0.38287732024590954]
    renderView3.CameraParallelScale = 0.02421925153675304

    # Annotate time
    #timeAnnotation = AnnotateTimeFilter()
    #timeAnnotation.Format = "Time: {time:.5f}s"
    #timeDisplay = Show(timeAnnotation, renderView3)
    #timeDisplay.Color = [0, 0, 0]
    #timeDisplay.WindowLocation = 'Lower Left Corner'

    # Time control
    animationScene = GetAnimationScene()
    animationScene.UpdateAnimationUsingDataTimeSteps()
    timesteps = animationScene.TimeKeeper.TimestepValues

    if not timesteps:
        print(f"[WARNING] No timesteps found in {foam_path}")
        continue

    # Output folder
    case_output_dir = os.path.join(output_base_dir, case_name)
    os.makedirs(case_output_dir, exist_ok=True)

    # Save screenshots within desired time range
    for t in timesteps:
        if t_min <= t <= t_max:
            animationScene.AnimationTime = t
            for _, proxy in GetSources().items():
                proxy.UpdatePipeline(time=t)
            Render()

            output_file = os.path.join(case_output_dir, f"uy_po_1_m_per_s_iso_t{t:.5f}.png")
            SaveScreenshot(output_file, layout3, ImageResolution=[1280, 800])
