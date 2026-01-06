# How the LetThereBeBeans App Works

A casual guide to understanding this hyperspectral scanning application.

## The Big Picture

Think of this app like a control panel for a scientific instrument. It's kind of like a really fancy TV remote, but instead of changing channels, it controls lasers, motors, and cameras to scan samples and collect data.

## The Main Parts

### 1. **The GUI (Graphical User Interface)** - What You See

The app is built with **QML** (Qt Modeling Language), which is basically a way to make pretty buttons and displays. It's split into different sections:

- **Sidebar (left)**: Where you pick which automation mode you want to use
- **XWing Controller**: Moves the sample around (like an X-Y stage - think Etch-A-Sketch but precise)
- **Cornerstone Controller**: Controls the wavelength of light (like tuning a radio, but for light)
- **PMT Gain Shield**: Controls how sensitive the light detector is
- **Start/Stop buttons**: Does exactly what you'd expect!

### 2. **The Cores** - The Brain Cells

"Cores" are Python classes that control individual pieces of hardware. Think of them like drivers for your computer's keyboard or mouse - they translate your clicks into actions the hardware understands.

**Key Cores:**
- **XWing**: Controls the motorized stage that moves samples around
- **Cornerstone**: Controls the monochromator (the thing that picks what color of light to use)
- **PMTGainShield**: Controls the PMT (PhotoMultiplier Tube) - basically an ultra-sensitive light detector
- **Oscilloscope**: Records voltage measurements

Each core:
- Talks to one piece of hardware
- Gets created once when the app starts
- Stays alive the whole time the app is running

### 3. **The Automation Clusters** - The Pre-Programmed Routines

This is where the magic happens! Automation clusters are like recipes - they combine multiple pieces of hardware to do complex tasks automatically.

**Available Automations:**
1. **Extinction**: Scans samples and adjusts the PMT gain automatically to get good measurements
2. **SingleFluor**: Scans samples with a fixed high gain for fluorescence measurements

Think of it like this:
- **Cores** = individual kitchen appliances (oven, mixer, knife)
- **Automation Clusters** = recipes that use those appliances in a specific order

## How Switching Automations Works

Here's the cool part that makes everything work smoothly:

### The Problem We Solved

Imagine you have one USB cable, but two devices that need it. You can't plug both in at once! That was our problem with the Arduino that controls the PMT.

**Old (broken) way:**
- Extinction automation creates its own Arduino connection → Opens COM8
- SingleFluor automation creates its own Arduino connection → Tries to open COM8
- **CRASH!** "Permission denied - port already in use"

**New (working) way:**
- PMTGainShield core opens COM8 once at startup
- Both automations share that same connection
- No conflicts! Everyone's happy!

### The Step-by-Step Process

When you click an automation button in the sidebar:

1. **Cleanup Phase**: If there's already an automation running:
   - Stop any active scans
   - Reset the PMT gain to 0 (turn down the sensitivity)
   - Clear out the old automation (but keep the hardware connections!)

2. **Initialize Phase**: Create the new automation:
   - Pass references to the cores (XWing, Cornerstone, PMTGainShield)
   - The automation uses the Arduino connection from PMTGainShield
   - No new hardware connections are created!

3. **Update Phase**: Tell the QML interface about the new automation
   - The "AutomationBackend" now points to your selected automation
   - The Start/Stop buttons now control the new automation

## The Hardware Sharing System

This is the genius part (if I do say so myself):

```
Startup:
├── Create XWing (opens motor controller)
├── Create Cornerstone (opens monochromator)
└── Create PMTGainShield (opens Arduino on COM8) ← This is the key!

When you select Extinction automation:
├── Extinction receives: xwing, cornerstone, pmt_shield
├── Extinction uses: pmt_shield.ac (the Arduino connection)
└── No new hardware connections created!

When you switch to SingleFluor:
├── Reset PMT gain to 0
├── Clear Extinction automation
├── Create SingleFluor with: xwing, cornerstone, pmt_shield
├── SingleFluor uses: pmt_shield.ac (same Arduino connection!)
└── Still no new hardware connections!
```

## The Automation Manager - The Traffic Cop

The `AutomationManager` class is like a traffic cop directing which automation gets to "drive" at any given time.

**What it does:**
- Keeps track of which automation is currently active
- Makes sure only one automation runs at a time
- Handles the cleanup when switching
- Shares the hardware cores with whichever automation needs them

**Important:** No automation is loaded at startup! You MUST pick one from the sidebar. This prevents the PMTGainShield GUI from fighting with an automation for the Arduino.

## The Menu Bar & Sidebar

You have TWO ways to switch automations:

1. **Sidebar buttons** (on the left): Big, colorful, shows which is selected
2. **Menu bar** (at the top): Traditional dropdown menu

Both do the exact same thing! Pick whichever you like. The sidebar has a cool status light:
- 🟠 Orange = "Not Loaded" (pick an automation!)
- 🟢 Green = "Ready" (automation is loaded and ready to scan)

## Common Questions

**Q: Why can't I just start a scan when the app opens?**
A: No automation is loaded at startup to avoid hardware conflicts. Click Extinction or SingleFluor first!

**Q: What happens to my data if I switch automations mid-scan?**
A: The scan gets stopped and saved up to the current point. Don't switch during a scan!

**Q: Can I use the PMTGainShield GUI while a scan is running?**
A: Technically yes, but DON'T! The automation is controlling the gain automatically. You'll mess up your data!

**Q: Why does the app print all that stuff to the console?**
A: That's debug info to help us know what's happening. Look for:
- "Initialized automation: [name]" = automation loaded successfully
- "Reset PMT gain to 0" = cleaned up properly before switching
- "Closed PMT serial connection" = you shouldn't see this anymore! (means old buggy code)

## The Code Files (Where Everything Lives)

- **LetThereBeBeans.py**: The main file - starts everything up
- **cores.py**: All the hardware controllers (XWing, Cornerstone, PMTGainShield, etc.)
- **automation_clusters.py**: The automation recipes (Extinction, SingleFluor)
- **hardware_controllers.py**: Low-level code that talks directly to hardware
- **components/main.qml**: The main window layout
- **components/AutomationSidebar.qml**: The sidebar with automation buttons
- **components/[Other].qml**: Individual control panels (XWing, Cornerstone, etc.)

## TL;DR (Too Long; Didn't Read)

1. App starts, creates all hardware connections ONCE
2. You pick an automation from the sidebar
3. That automation uses the shared hardware to do its thing
4. Switch automations anytime - hardware stays connected
5. Only one automation runs at a time
6. No permission errors because hardware is shared, not duplicated!

---

*Written for humans by humans (with a little help from an AI). If something's confusing, just ask!*
