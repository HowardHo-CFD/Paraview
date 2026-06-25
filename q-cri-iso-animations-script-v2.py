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
output_base_dir = "q-cri-videos"       # save screenshots here

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
    LoadState("paraview-scripts/q-cri-iso.pvsm")

    # Swap in the correct .foam file
    for _, proxy in GetSources().items():
        if hasattr(proxy, 'FileName'):
            proxy.FileName = foam_path
            proxy.UpdatePipeline()

    # Get the correct view
    renderView2 = FindViewOrCreate('RenderView2', viewtype='RenderView')
    SetActiveView(renderView2)

    # Set layout preview mode
    layout2 = GetLayout()
    layout2.PreviewMode = [0, 0]         # Exit preview
    layout2.PreviewMode = [1280, 920]    # Enter preview
    layout2.SetSize(1280, 920)
    Render()

    # Set interaction mode and camera
    renderView2.InteractionMode = '2D'
    renderView2.CameraPosition = [-0.8863148110507589, 0.841869617705111, 1.0929770111236452]
    renderView2.CameraFocalPoint = [0.020312155710811203, 0.02435201075811195, 0.008598711593997456]
    renderView2.CameraViewUp = [0.3226123621152193, 0.865636310150949, -0.38287732024590937]
    renderView2.CameraParallelScale = 0.026701724819270228

    # Annotate time
    #timeAnnotation = AnnotateTimeFilter()
    #timeAnnotation.Format = "Time: {time:.5f}s"
    #timeDisplay = Show(timeAnnotation, renderView2)
    #timeDisplay.Color = [0, 0, 0]
    #timeDisplay.WindowLocation = 'Upper Left Corner'

    # Time control
    animationScene = GetAnimationScene()
    animationScene.UpdateAnimationUsingDataTimeSteps()
    timesteps = animationScene.TimeKeeper.TimestepValues

    # Filter timesteps in desired time range
    timestep_indices = [i for i, t in enumerate(timesteps) if t_min <= t <= t_max]
    if not timestep_indices:
        print(f"[WARNING] No timesteps in desired range for {case_name}")
        continue

    # Frame window
    frame_window = [timestep_indices[0], timestep_indices[-1]]

    # Output folder
    case_output_dir = output_base_dir #os.path.join(output_base_dir, case_name)
    os.makedirs(case_output_dir, exist_ok=True)

    # Output animation path
    animation_output_path = os.path.join(case_output_dir, f"{case_name}.avi")

    # Save animation (only once per case)
    SaveAnimation(
        animation_output_path,
        viewOrLayout=layout2,
        ImageResolution=[1280, 920],
        FrameRate=4,
        FrameWindow=frame_window
    )

