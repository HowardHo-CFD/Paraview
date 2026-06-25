"""
ParaView data extraction script for wake velocity profiles.
Exports multiple slice data to CSV files organized by case name.
"""

from paraview.simple import *
import os

# ============================================================================
# CONFIGURATION - Edit these variables for different cases
# ============================================================================
CASE_NAME = "coarse-v4-no-neck"
#FOAM_FILE = "actuated-v3.foam"
FOAM_FILE = CASE_NAME + ".foam"
STATE_FILE = "paraview-states/wake-u-profile-z-0-v1.pvsm"
SLICES_TO_EXPORT = ["x-d-1-06", "x-d-1-54", "x-d-2-02"]

# ============================================================================
# SETUP
# ============================================================================
# Disable automatic camera reset on 'Show'
paraview.simple._DisableFirstRenderCameraReset()

# Create output directory structure
output_dir = os.path.join("outputs", CASE_NAME)
os.makedirs(output_dir, exist_ok=True)

# Clean up any existing views
renderView1 = GetActiveViewOrCreate('RenderView')
Delete(renderView1)
del renderView1

# ============================================================================
# LOAD STATE AND SETUP VIEWS
# ============================================================================
# Load the ParaView state file
LoadState(STATE_FILE)

# Update the foam reader
for _, proxy in GetSources().items():
    if hasattr(proxy, 'FileName'):
        foam_path = os.path.join(CASE_NAME, FOAM_FILE)
        proxy.FileName = foam_path
        proxy.UpdatePipeline()
        break  # Only need to update the first (root) foam reader

timeKeeper1 = GetTimeKeeper()
#timeKeeper1.Time = 47.4	# output specified time
timeKeeper1.Time = timeKeeper1.TimestepValues[-1]	# output latest timestep

current_time = timeKeeper1.Time
time_str = f"{current_time:.1f}".replace(".", "_")

print(f"Current time: {timeKeeper1.Time}")

# Find and set up views
renderView1 = FindViewOrCreate('RenderView1', viewtype='RenderView')
spreadSheetView1 = FindViewOrCreate('SpreadSheetView1', viewtype='SpreadSheetView')
SetActiveView(spreadSheetView1)

# ============================================================================
# EXPORT DATA FROM EACH SLICE
# ============================================================================
for slice_name in SLICES_TO_EXPORT:
    print(f"Exporting {slice_name}...")
    
    # Find and activate the source
    source = FindSource(slice_name)
    SetActiveSource(source)
    
    # Show data in spreadsheet view
    display = Show(source, spreadSheetView1, 'SpreadSheetRepresentation')
    display.Assembly = ''
    display.BlockVisibilities = []
    
    # Export to CSV
    output_file = os.path.join(output_dir, f"{slice_name}_t_{time_str}s.csv")
    ExportView(output_file, view=spreadSheetView1,
               RealNumberNotation='Mixed', RealNumberPrecision=6)
    
    # Hide the source before moving to next
    Hide(source, spreadSheetView1)
    
    print(f"  → Saved to {output_file}")

print(f"\nAll exports saved to: {output_dir}")

# ============================================================================
# LAYOUT CONFIGURATION (for reproducibility)
# ============================================================================
layout1 = GetLayoutByName("Layout #1")
layout3 = GetLayout()

# Set layout sizes
layout1.SetSize(1119, 749)
layout3.SetSize(400, 400)

# Set camera for renderView1
renderView1.InteractionMode = '2D'
renderView1.CameraPosition = [0.0, 0.0, 2.7480508027409014]
renderView1.CameraFocalPoint = [0.0, 0.0, 0.015999995172023773]
renderView1.CameraParallelScale = 0.584385769575659
